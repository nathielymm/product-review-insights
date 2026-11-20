"""Product-level v2 execution. Preparation never authorizes a frozen run."""
import contextlib
import copy
import hashlib
import importlib
import importlib.metadata
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlparse

from . import generation
from .data import digest_file, read_corpus


class IntegrityError(ValueError):
    """A run whose identity/budget cannot be trusted must not produce final metrics."""


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def helpers():
    scripts = Path(__file__).resolve().parents[2] / 'scripts'
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return (importlib.import_module('run_product_aspect_pilot'),
            importlib.import_module('run_product_original_pilot'))


def attempt_id(row):
    return f"{row['phase']}/{row['product_id']}/{row['question_id']}/r{row['repetition']}/{row['method']}"


def validate_schedule(schedule, product_ids):
    rows = schedule['english_attempts']
    if len(rows) != 60 or len({attempt_id(r) for r in rows}) != 60:
        raise ValueError('Expected 60 unique scheduled English attempts')
    expected = {(pid, f'Q{q}', method, 1) for pid in product_ids
                for q in range(1, 7) for method in ['traditional', 'thematic']}
    main = [r for r in rows if r['phase'] == 'primary']
    if len(main) != 36 or {(r['product_id'], r['question_id'], r['method'], r['repetition']) for r in main} != expected:
        raise ValueError('Primary grid differs')
    stability = [r for r in rows if r['phase'] == 'stability']
    extra = {(pid, q, m, rep) for pid in product_ids for q in ['Q1', 'Q5']
             for m in ['traditional', 'thematic'] for rep in [2, 3]}
    if len(stability) != 24 or {(r['product_id'], r['question_id'], r['method'], r['repetition']) for r in stability} != extra:
        raise ValueError('Stability grid differs')
    if rows[:36] != main or [r['attempt_order'] for r in rows] != list(range(1, 61)):
        raise ValueError('Execution phase/order differs')
    for i in range(0, 60, 2):
        a, b = rows[i:i+2]
        if any(a[k] != b[k] for k in ['product_id', 'question_id', 'repetition', 'phase']) or {a['method'], b['method']} != {'traditional', 'thematic'}:
            raise ValueError('Methods must be paired')
    if sum(main[i]['method'] == 'traditional' for i in range(0, 36, 2)) != 9:
        raise ValueError('First-method balance differs')
    if any(r['translate_for_presentation'] is not (r['phase'] == 'primary') for r in rows):
        raise ValueError('Translation phase differs')
    return rows


def load_configuration(path):
    """Validate immutable inputs without model/network access; allows not-frozen prep."""
    path = Path(path)
    config = json.loads(path.read_text())
    files = {str(path): digest_file(path)}
    for package, expected in config.get('library_versions', {}).items():
        if importlib.metadata.version(package) != expected:
            raise ValueError('Library version differs: '+package)
    def checked(p, expected):
        actual = digest_file(p)
        if actual != expected:
            raise ValueError(f'Input checksum differs: {p}')
        files[str(p)] = actual
    for record in config.get('technical_evidence', {}).values():
        checked(record['path'], record['sha256'])
    for key in ['questions', 'scoring', 'schedule']:
        checked(config[key]['path'], config[key]['sha256'])
    checked(config['scoring']['units_path'], config['scoring']['units_sha256'])
    for p, expected in config['input_provenance'].items():
        checked(p, expected)
    checked(config['human_review']['selection_plan'], config['human_review']['selection_sha256'])
    checked(config['local_model']['manifest_path'], config['local_model']['manifest_sha256'])
    if config['generation']['config']['ollama_model'] != config['local_model']['name'] or ':cloud' in config['local_model']['name'].lower():
        raise ValueError('Only the approved local model is allowed')
    if hashlib.sha256(generation.STRUCTURED_SYSTEM.encode()).hexdigest() != config['generation']['system_prompt_sha256']:
        raise ValueError('Original English prompt changed')
    pids = {p['product_id'] for p in config['products']}
    if len(pids) != 3 or config['development_only_product'] in pids:
        raise ValueError('Product/development isolation differs')
    for product in config['products']:
        checked(product['corpus'], product['corpus_sha256'])
        corpus = read_corpus(product['corpus'])
        if len(corpus) != product['expected_reviews'] or len({r['id'] for r in corpus}) != len(corpus) or any(r['product_id'] != product['product_id'] for r in corpus):
            raise ValueError('Foreign product, duplicate review or corpus count mismatch')
        checked(product['reference'], product['reference_sha256'])
        reference = json.loads(Path(product['reference']).read_text())
        if reference['product_id'] != product['product_id'] or not {r['id'] for r in reference['evidence']} <= {r['id'] for r in corpus}:
            raise ValueError('Reference identity differs')
        index = Path(product['index'])
        checked(index/'metadata.json', product['index_metadata_sha256'])
        meta = json.loads((index/'metadata.json').read_text())
        if meta['corpus_sha256'] != product['corpus_sha256']:
            raise ValueError('Index corpus differs')
        for name, key in [('index.faiss', 'index_sha256'), ('chunks.jsonl', 'chunks_sha256'), ('clusters.npy', 'clusters_sha256')]:
            checked(index/name, meta[key])
        for name, expected in meta['encoder_files_sha256'].items():
            checked(index/'encoder'/name, expected)
        docs = read_corpus(index/'chunks.jsonl')
        if len(docs) != product['chunks'] or any(d['product_id'] != product['product_id'] for d in docs) or {d['review_id'] for d in docs} != {r['id'] for r in corpus}:
            raise ValueError('Indexed review isolation differs')
    questions = json.loads(Path(config['questions']['path']).read_text())
    if {p['product_id'] for p in questions['products']} != pids:
        raise ValueError('Question products differ')
    for p in questions['products']:
        if len(p['questions']) != 6 or {q['id'] for q in p['questions']} != {f'Q{i}' for i in range(1, 7)}:
            raise ValueError('Question grid differs')
        if any(len(q['aspects']) != 5 or not q['generation_question_en'].strip() for q in p['questions']):
            raise ValueError('English questions/aspect queries incomplete')
    schedule = json.loads(Path(config['schedule']['path']).read_text())
    validate_schedule(schedule, pids)
    rubric = json.loads(Path(config['scoring']['path']).read_text())
    units = json.loads(Path(config['scoring']['units_path']).read_text())
    totals = {k: sum(len(c[k]) for c in units['cases']) for k in ['content', 'qualification', 'contrast']}
    if totals != config['scoring']['totals_per_method'] or len(units['cases']) != 12:
        raise ValueError('Approved denominators differ')
    if not rubric['unit_manifest']['scoring_units_user_approved'] or any(not u['user_approved_as_scoring_unit'] for c in units['cases'] for k in totals for u in c[k]):
        raise ValueError('Scoring units not approved')
    # Seal implementation as well as data at the eventual freeze.
    for name in ['evaluation_v2.py', 'scoring_v2.py']:
        p = Path(__file__).with_name(name)
        files[str(p.relative_to(Path(__file__).resolve().parents[2]))] = digest_file(p)
    return config, questions, schedule, units, files


def validate_freeze(freeze, configuration_sha256, required_hashes):
    if not freeze or freeze.get('status') != 'frozen_user_authorized':
        raise ValueError('No authorized v2 freeze; preparation cannot execute final generations')
    if freeze.get('user_authorized_freeze') is not True or freeze.get('user_authorized_final_generation') is not True:
        raise ValueError('Explicit freeze and generation authorization required')
    if freeze.get('configuration_sha256') != configuration_sha256:
        raise ValueError('Freeze configuration differs')
    if freeze.get('file_hashes') != required_hashes:
        raise ValueError('Frozen input/code manifest differs')
    for p, expected in required_hashes.items():
        if digest_file(p) != expected:
            raise ValueError(f'Frozen file changed: {p}')
    checks = freeze.get('technical_checks', {})
    if set(checks) != {'runtime', 'token_budget', 'reference_applicability', 'cluster_inspection', 'calibration', 'tests'} or any(v is not True for v in checks.values()):
        raise ValueError('Freeze technical checklist incomplete')


def verify_runtime(config, api=None):
    api = api or generation.api
    if urlparse(generation.BASE_URL).hostname not in ['127.0.0.1', 'localhost', '::1']:
        raise ValueError('Remote model endpoint excluded')
    version = api('/api/version', timeout=10)
    tags = api('/api/tags', timeout=10)
    model = next((m for m in tags['models'] if m['name'] == config['local_model']['name']), None)
    if version.get('version') != config['local_model']['expected_runtime_version'] or not model or model['digest'] != config['local_model']['expected_digest']:
        raise ValueError('Active runtime/model differs from approved configuration')
    return {'runtime_version': version['version'], 'model_digest': model['digest']}


def input_fingerprint(payload):
    # Preserve schema insertion order too; do not canonicalize away payload differences.
    data = {k: payload.get(k) for k in ['model', 'messages', 'format']}
    return hashlib.sha256(json.dumps(data, ensure_ascii=False).encode()).hexdigest()


def require_budget(tokens, payload):
    if type(tokens) is not int or tokens < 1:
        raise IntegrityError('Missing runtime input token count')
    if tokens + payload['options']['num_predict'] > payload['options']['num_ctx']:
        raise IntegrityError('Input plus reserved output exceeds context; no silent truncation')


class BudgetTransport:
    """Unchanged final payload; technical one-token probes kept in a separate ledger."""
    def __init__(self, api, token_counts=None, probe_log=None):
        self.api, self.counts = api, dict(token_counts or {})
        self.probe_log, self.calls = probe_log, []
        self.active_attempt_id, self.stage = None, None
        self.allow_probe = True

    def __call__(self, path, payload=None, **kwargs):
        if path != '/api/chat':
            return self.api(path, payload, **kwargs)
        key = input_fingerprint(payload)
        if key not in self.counts:
            if not self.allow_probe:
                raise IntegrityError('English payload not in frozen prechecked token ledger')
            # This is a technical call, not a retry or a candidate quality answer.
            if len(json.dumps(payload, ensure_ascii=False).encode()) + 1024 >= 32768:
                raise IntegrityError('Cannot guarantee untruncated token-count probe')
            probe = copy.deepcopy(payload)
            probe['options'].update(num_ctx=32768, num_predict=1)
            started = time.perf_counter()
            response, probe_error = None, None
            try:
                response = self.api(path, probe, **kwargs)
            except Exception as error:
                probe_error = error
            entry = {'role': 'technical_budget_probe_not_quality_answer', 'input_fingerprint': key,
                     'payload': probe, 'response': response, 'wall_seconds': time.perf_counter()-started,
                     'attempt_id': self.active_attempt_id, 'stage': self.stage,
                     'error': str(probe_error) if probe_error else None}
            if self.probe_log:
                with Path(self.probe_log).open('a') as out:
                    out.write(json.dumps(entry, ensure_ascii=False)+'\n')
            if probe_error:
                raise probe_error
            tokens = response.get('prompt_eval_count')
            if response.get('eval_count') != 1:
                raise IntegrityError('Technical probe output limit not respected')
            require_budget(tokens, payload)
            self.counts[key] = tokens
        require_budget(self.counts[key], payload)
        call = {'payload': copy.deepcopy(payload), 'input_tokens_prechecked': self.counts[key]}
        self.calls.append(call)
        started = time.perf_counter()
        try:
            response = self.api(path, payload, **kwargs)
        except Exception as error:
            call['error'] = type(error).__name__+': '+str(error)
            raise
        finally:
            call['wall_seconds'] = time.perf_counter()-started
        call['response'] = copy.deepcopy(response)
        # Detect a runtime difference instead of treating a smaller/truncated count as safe.
        if response.get('prompt_eval_count') != self.counts[key]:
            call['budget_mismatch'] = True
            raise IntegrityError('Runtime prompt count differs from prechecked count; raw response retained')
        return response


@contextlib.contextmanager
def recorded_transport(transport):
    previous = generation.api
    generation.api = transport
    try:
        yield
    finally:
        generation.api = previous


def cached_token_counts(path):
    counts = {}
    for line in Path(path).read_text().splitlines():
        row = json.loads(line)
        key, n = input_fingerprint(row['payload']), row['prompt_eval_count']
        if key in counts and counts[key] != n:
            raise ValueError('Conflicting token-count measurements')
        counts[key] = n
    return counts


def prepare_attempt(config, questions, scheduled, retriever):
    aspects, _ = helpers()
    from .retrieval import select_hits
    question = next(q for p in questions['products'] if p['product_id'] == scheduled['product_id']
                    for q in p['questions'] if q['id'] == scheduled['question_id'])
    start = time.perf_counter()
    ranked, scores, matches, _ = aspects.candidates_for(retriever, question, config['retrieval'])
    chosen = select_hits(ranked, retriever.clusters, config['retrieval']['top_k'], scheduled['method']=='thematic')
    hits = [{**retriever.documents[i], 'cluster': int(retriever.clusters[i]),
             'score': scores[i], 'matched_aspects': matches[i]} for i in chosen]
    context, evidence = generation.pack_context(hits, config['generation']['config']['context_chars'])
    if not evidence or len({r['review_id'] for r in evidence}) != len(evidence) or any(r['product_id'] != scheduled['product_id'] for r in evidence):
        raise ValueError('Empty, duplicated or foreign-product context')
    return question, hits, evidence, {'retrieval_seconds': time.perf_counter()-start,
                                    'context_chars': len(context), 'candidate_pool_sha256': fingerprint(ranked)}


def execute(path, freeze_path, output, token_ledger):
    """Final-run entry point: no output/model call before authorized freeze checks."""
    output = Path(output)
    if output.exists():
        raise FileExistsError('Preserve existing run; no automatic resume/retry')
    config, questions, schedule, _, files = load_configuration(path)
    freeze = json.loads(Path(freeze_path).read_text()) if freeze_path else None
    validate_freeze(freeze, digest_file(path), files)
    if not output.resolve().is_relative_to(Path('results').resolve()):
        raise ValueError('Individual runs must remain under ignored local results/')
    # Counts are inputs too: changing the ledger after freeze is not allowed.
    if freeze.get('token_ledger_sha256') != digest_file(token_ledger):
        raise ValueError('Token ledger differs from freeze')
    runtime = verify_runtime(config)
    _, original = helpers()
    from .retrieval import Retriever
    output.mkdir(parents=True)
    write_json(output/'provenance.private.json', {'configuration_sha256': digest_file(path),
               'freeze_sha256': digest_file(freeze_path), 'inputs': files, 'runtime': runtime,
               'quality_answers_separate_from_technical_probes': True})
    transport = BudgetTransport(generation.api, cached_token_counts(token_ledger), output/'technical-probes.private.jsonl')
    retrievers, rows, pools = {}, [], {}
    for scheduled in schedule['english_attempts']:
        started = time.perf_counter()
        row = {**scheduled, 'attempt_id': attempt_id(scheduled), 'evidence': [], 'english': None,
               'generation_error': None, 'retrieval_error': None, 'generation_seconds': None,
               'retrieval_seconds': None, 'index_load_seconds': 0., 'transport': []}
        fatal_error = None
        try:
            pid = scheduled['product_id']
            if pid not in retrievers:
                product = next(p for p in config['products'] if p['product_id']==pid)
                loading = time.perf_counter()
                try:
                    retrievers[pid] = Retriever(product['index'])
                finally:
                    row['index_load_seconds'] = time.perf_counter()-loading
            question, hits, evidence, info = prepare_attempt(config, questions, scheduled, retrievers[pid])
            row.update(info, evidence=evidence, question_en=question['generation_question_en'])
            pool_key = (pid, scheduled['question_id'])
            if pool_key in pools and pools[pool_key] != info['candidate_pool_sha256']:
                raise ValueError('Common candidate pool changed across methods/repetitions')
            pools[pool_key] = info['candidate_pool_sha256']
        except Exception as error:
            row['retrieval_error'] = type(error).__name__+': '+str(error)
        if not row['retrieval_error']:
            transport.active_attempt_id, transport.stage = row['attempt_id'], 'English'
            transport.allow_probe = False
            before = len(transport.calls);t = time.perf_counter()
            try:
                with recorded_transport(transport):
                    row['english'] = generation.generate(question['generation_question_en'], hits, config['generation']['config'])
                if [(e['id'],e['text'],e['citation_id']) for e in row['english'].get('evidence',[])] != [(e['id'],e['text'],e['citation_id']) for e in evidence]:
                    raise IntegrityError('Original generator context differs from prepared evidence')
            except Exception as error:
                row['generation_error'] = type(error).__name__+': '+str(error)
                if isinstance(error, IntegrityError):fatal_error=error
                # Never discard a received raw response on an accounting/transport check failure.
                if len(transport.calls)>before and 'response' in transport.calls[-1]:
                    response=transport.calls[-1]['response']
                    row['english']={'raw_model_output':response.get('message',{}).get('content',''),
                                    'structured_output':None,'structured_validation':{'valid':False},'ollama':response}
            row['generation_seconds'] = time.perf_counter()-t
            row['transport'] = copy.deepcopy(transport.calls[before:])
        row['total_seconds'] = time.perf_counter()-started
        with (output/'runs.private.jsonl').open('a') as out:
            out.write(json.dumps(row, ensure_ascii=False)+'\n')
        rows.append(row)
        if fatal_error:
            write_json(output/'status.private.json',{'status':'integrity_failed','error':str(fatal_error),'english_records':len(rows),'translation_records':0})
            raise fatal_error
        write_json(output/'status.private.json', {'status':'english_in_progress','english_records':len(rows),'translation_records':0})
    translated = 0
    for row in rows:
        if row['phase'] != 'primary':
            continue
        english = row['english'];before_hash=fingerprint(english);before=len(transport.calls)
        transport.active_attempt_id, transport.stage = row['attempt_id'], 'presentation'
        transport.allow_probe = True
        if english and english.get('structured_output') is not None:
            settings={k:config['presentation'][k] for k in ['model','num_ctx','num_predict','temperature','seed']}
            with recorded_transport(transport):
                translation=original.translate_presentation(english['structured_output'],row['evidence'],settings)
        else:
            translation={'attempted':False,'valid':False,'reason':'No valid English structure; no repair','total_seconds':0.}
        if before_hash != fingerprint(english):
            raise ValueError('Presentation mutated original English')
        entry={'attempt_id':row['attempt_id'],'english_sha256':before_hash,'translation':translation,
               'transport':copy.deepcopy(transport.calls[before:])}
        with (output/'translations.private.jsonl').open('a') as out:
            out.write(json.dumps(entry,ensure_ascii=False)+'\n')
        translated+=1
    try:
        verify_runtime(config)
        for file, expected in files.items():
            if digest_file(file) != expected:
                raise ValueError('Input changed during run: '+file)
    except Exception as error:
        write_json(output/'status.private.json', {'status':'integrity_failed','error':str(error),
                   'english_records':len(rows),'translation_records':translated})
        raise
    write_json(output/'status.private.json',{'status':'complete','english_records':len(rows),'translation_records':translated,
               'primary_scheduled_attempts':36,'stability_records':24,'annotations_complete':False,
               'runs_sha256':digest_file(output/'runs.private.jsonl'),
               'translations_sha256':digest_file(output/'translations.private.jsonl'),
               'technical_probes_sha256':digest_file(output/'technical-probes.private.jsonl') if (output/'technical-probes.private.jsonl').exists() else None})
    return {'english_records':len(rows),'translation_records':translated}
