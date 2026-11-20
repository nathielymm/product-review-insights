"""Frozen inputs, blinded unit annotations and auditable study scoring."""
import collections
import hashlib
import importlib.metadata
import json
import platform
import random
import statistics
from pathlib import Path

from .data import digest_file, read_corpus
from .scoring import FACTUAL_QUESTIONS, binary_profile, claim_metrics, coverage_metrics, known_support_availability
from .study import validate_corpus


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def source_fingerprints():
    root=Path(__file__).resolve().parents[2]
    return {str(p.relative_to(root)):digest_file(p) for p in sorted((root/'src/product_review_insights').glob('*.py'))}


def runtime_fingerprint():
    versions={}
    for line in Path('requirements.lock.txt').read_text().splitlines():
        if '==' in line and not line.startswith('#'):
            name=line.split('==',1)[0].strip()
            versions[name]=importlib.metadata.version(name)
    return {'python':platform.python_version(),'machine':platform.machine(),'packages':versions}


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def load_freeze(path,check_code=True):
    spec=read_json(path)
    if spec.get('schema')!='evaluation_freeze_v1': raise ValueError('Unsupported evaluation freeze')
    for filename,expected in spec['files_sha256'].items():
        if digest_file(filename)!=expected: raise ValueError(f'Frozen input changed: {filename}')
    if check_code and source_fingerprints()!=spec['source_files_sha256']:
        raise ValueError('Evaluation source changed; use frozen code or a new freeze')
    if check_code and runtime_fingerprint()!=spec['runtime']:
        raise ValueError('Evaluation runtime differs from frozen environment')
    registry=read_json(spec['registry_file'])
    if digest_file(spec['registry_file'])!=spec['registry_sha256']: raise ValueError('Reference registry changed')
    for case_id,case in spec['cases'].items():
        if registry['cases'][case_id]['corpus_sha256']!=case['corpus_sha256']:
            raise ValueError('Case registry and freeze disagree')
    return spec,registry


def validate_case(spec,registry,case_id):
    if case_id not in spec['cases']: raise ValueError('Unknown frozen case')
    case=spec['cases'][case_id]
    rows=read_corpus(case['corpus'])
    manifest=read_json(Path(case['corpus']).with_name('manifest.json'))
    validate_corpus(rows,manifest,case['corpus'])
    if digest_file(case['corpus'])!=case['corpus_sha256']: raise ValueError('Frozen corpus changed')
    if manifest['study']!=case['study'] or manifest['study']['split']!='evaluation':
        raise ValueError('Wrong frozen study scope')
    if set(r['id'] for r in rows)!=set(registry['cases'][case_id]['review_ids']):
        raise ValueError('Case review identities changed')
    return case,rows


def validate_index(spec,case,index_path):
    meta=read_json(Path(index_path)/'metadata.json')
    if meta.get('study')!=case['study'] or meta['corpus_sha256']!=case['corpus_sha256']:
        raise ValueError('Index does not belong to the frozen corpus')
    if meta['config']!=spec['config']: raise ValueError('Index configuration differs from freeze')
    if meta['encoder_files_sha256']!=spec['index_encoder_files_sha256']:
        raise ValueError('Index encoder differs from frozen snapshot')
    if case.get('index') and str(Path(index_path))!=case['index']:
        raise ValueError('Use the bound primary index')
    if case.get('index_metadata_sha256') and digest_file(Path(index_path)/'metadata.json')!=case['index_metadata_sha256']:
        raise ValueError('Frozen primary index metadata changed')
    for name,key in [('index.faiss','index_sha256'),('chunks.jsonl','chunks_sha256'),('clusters.npy','clusters_sha256')]:
        if digest_file(Path(index_path)/name)!=meta[key]: raise ValueError('Index artifact changed')
    return meta


def build_frozen_index(freeze_path,case_id,output):
    spec,registry=load_freeze(freeze_path); case,_=validate_case(spec,registry,case_id)
    if case.get('index'): raise ValueError('Primary index already frozen')
    if Path(output).exists(): raise FileExistsError('Use a new index destination')
    from .retrieval import build
    build(case['corpus'],output,spec['config'])
    validate_index(spec,case,output)
    return {'case_id':case_id,'index':str(output)}


def run_frozen(freeze_path,case_id,destination,index_path=None):
    spec,registry=load_freeze(freeze_path); case,_=validate_case(spec,registry,case_id)
    index_path=index_path or case.get('index')
    if not index_path: raise ValueError('Build a frozen sensitivity index and pass --index')
    validate_index(spec,case,index_path)
    binding={'freeze_sha256':digest_file(freeze_path),'case_id':case_id,'corpus_sha256':case['corpus_sha256'],
             'registry_sha256':spec['registry_sha256'],'index_path':str(index_path),'index_metadata_sha256':digest_file(Path(index_path)/'metadata.json')}
    from .experiments import run
    return run(index_path,spec['questions_file'],destination,case['repetitions'],case['study']['cohort_id'],
               expected_model_digest=spec['model_digest'],expected_ollama_version=spec['ollama_version'],evaluation_binding=binding,preserve_generation_errors=True)


def validate_runset(freeze_path,run_path):
    spec,registry=load_freeze(freeze_path)
    run_path=Path(run_path); metadata=read_json(run_path.with_name('metadata.json'))
    binding=metadata.get('evaluation_binding',{})
    if binding.get('freeze_sha256')!=digest_file(freeze_path): raise ValueError('Run belongs to another freeze')
    case_id=binding.get('case_id'); case,corpus=validate_case(spec,registry,case_id)
    if binding.get('corpus_sha256')!=case['corpus_sha256'] or binding.get('registry_sha256')!=spec['registry_sha256']:
        raise ValueError('Run binding refers to another corpus/reference')
    index_metadata=validate_index(spec,case,binding['index_path'])
    if index_metadata!=metadata['index_metadata'] or digest_file(Path(binding['index_path'])/'metadata.json')!=binding['index_metadata_sha256']:
        raise ValueError('Run index snapshot differs')
    chunk_rows={r['id']:r for r in read_corpus(Path(binding['index_path'])/'chunks.jsonl')}
    if metadata.get('status') not in {'complete','incomplete'}: raise ValueError('Invalid run status/model identity')
    if metadata['config']!=spec['config'] or metadata['questions_sha256']!=digest_file(spec['questions_file']):
        raise ValueError('Run inputs differ from freeze')
    if metadata.get('ollama_version',{}).get('version')!=spec['ollama_version']:
        raise ValueError('Run used another Ollama version')
    if metadata.get('expected_model_digest')!=spec['model_digest']: raise ValueError('Unbound model digest')
    rows=[json.loads(line) for line in run_path.read_text().splitlines()]
    questions={q['id']:q['question'] for q in read_json(spec['questions_file'])}
    corpus_by_id={r['id']:r for r in corpus}; identities=set()
    for row in rows:
        identity=(row['question_id'],row['method'],row['repeat'])
        if identity in identities: raise ValueError('Duplicate run identity')
        identities.add(identity)
        if row.get('evaluation_binding')!=binding or row['study']!=case['study']:
            raise ValueError('Run row has foreign scope/binding')
        if row['question_id'] not in questions or row['question']!=questions[row['question_id']]:
            raise ValueError('Run question changed')
        if row['method'] not in {'traditional','thematic'} or type(row['repeat']) is not int or not 0<=row['repeat']<case['repetitions']:
            raise ValueError('Invalid method/repetition')
        for hit in row['evidence']:
            original=corpus_by_id.get(hit['review_id'])
            if original is None or original['product_id']!=hit['product_id']:
                raise ValueError('Evidence from another corpus/family')
            chunk=chunk_rows.get(hit['id'])
            if chunk is None or any(hit[k]!=chunk[k] for k in ['review_id','product_id','text']):
                raise ValueError('Evidence passage differs from bound index')
    expected=len(questions)*case['repetitions']*2
    if len(rows)!=metadata['completed_runs'] or (metadata['status']=='complete' and len(rows)!=expected):
        raise ValueError('Run completeness does not match metadata')
    return spec,registry,case_id,case,corpus,metadata,rows



def review_frame(row,case_id):
    fields=['id','review_id','citation_id','text','product_id','functional_class','group_alias']
    return {'case_id':case_id,'question_id':row['question_id'],'question':row['question'],'answer':row['answer'],
            'evidence':[{k:h[k] for k in fields if k in h} for h in row['evidence']],
            'technical_state':{'generation_failed':bool(row.get('generation_error')),
                               'structured_valid':row.get('structured_validation',{}).get('valid'),
                               'done_reason':row.get('ollama',{}).get('done_reason')}}

def blind_study(freeze_path,run_path,destination,seed=42):
    spec,registry,case_id,case,corpus,metadata,rows=validate_runset(freeze_path,run_path)
    destination=Path(destination)
    if destination.exists(): raise FileExistsError('Use a new blind review destination')
    shuffled=list(enumerate(rows)); random.Random(seed).shuffle(shuffled)
    frames={}; packets=[]; labels=[]; key={}
    fields=['id','review_id','citation_id','text','product_id','functional_class','group_alias']
    rubric=registry['rubric']
    for index,row in shuffled:
        question_id=row['question_id']; qrole='facts' if question_id in rubric['factual_questions'] else 'proposal' if question_id in rubric['proposal_questions'] else 'control'
        frame=review_frame(row,case_id)
        fingerprint=canonical_digest(frame)
        if fingerprint not in frames:
            identifier=f'A{len(frames)+1:04d}'; frames[fingerprint]=identifier
            packets.append({'annotation_id':identifier,**frame})
            labels.append({'annotation_id':identifier,'status':'unreviewed','retrieval_coverage':None,'answer_coverage':None,
                           'claims':None,'proposal_criteria':{k:None for k in rubric['proposal_criteria']} if qrole=='proposal' else None,
                           'control_criteria':{k:None for k in rubric['control_criteria']} if qrole=='control' else None,
                           'not_applicable_reasons':{},'notes':''})
            key[identifier]={'frame_sha256':fingerprint,'run_rows':[]}
        key[frames[fingerprint]]['run_rows'].append(index)
    units=[u for u in registry['units'] if u['cohort_id']==case['study']['cohort_id']]
    anchors={rid for u in units for group in u['support_groups'] for rid in group}
    known=registry['cases'][case_id]['available_unit_ids']
    reference={'units':[{**u,'eligible_known_support':u['id'] in known} for u in units],
               'supporting_reviews':[r for r in corpus if r['id'] in anchors],'rubric':rubric,
               'note':'Only actual retrieved passages can support retrieval/answer coverage annotations. Missing anchors do not prove corpus absence.'}
    destination.mkdir(parents=True)
    write_json(destination/'blind.private.json',packets); write_json(destination/'annotations.private.json',labels)
    write_json(destination/'reference.private.json',reference)
    private_key={'freeze_sha256':digest_file(freeze_path),'run_sha256':digest_file(run_path),
                 'metadata_sha256':digest_file(Path(run_path).with_name('metadata.json')),
                 'blind_sha256':digest_file(destination/'blind.private.json'),'reference_sha256':digest_file(destination/'reference.private.json'),
                 'case_id':case_id,'key':key}
    write_json(destination/'key.private.json',private_key)
    return {'attempts':len(rows),'unique_review_items':len(packets),'exact_duplicate_reviews_saved':len(rows)-len(packets),
            'quality_annotations_completed':0,'complete_runset':metadata['status']=='complete','destination':str(destination)}


def check_support(entry,unit,hits,answer=None):
    if not isinstance(entry.get('support'),list) or not entry['support']: raise ValueError('Coverage needs quoted passage support')
    for support in entry['support']:
        hit=hits.get(support['evidence_id'])
        if hit is None or hit['product_id']!=unit['product_id']: raise ValueError('Coverage support belongs to another family')
        if not support['quote'] or support['quote'] not in hit['text']: raise ValueError('Support quote not present in retrieved passage')
    if answer is not None and (not entry.get('answer_quote') or entry['answer_quote'] not in answer):
        raise ValueError('Answer coverage quote not present in answer')


def score_label(label,frame,units,review_ids,rubric):
    qid=frame['question_id']; hits={h['citation_id']:h for h in frame['evidence']}
    selected=[u for u in units if u['question_id']==qid]
    by_unit={u['id']:u for u in selected}
    reviewed=label['status']=='reviewed'
    if label['status'] not in {'reviewed','unreviewed'}: raise ValueError('Unknown annotation status')
    result={'annotation_status':label['status']}
    if qid in rubric['factual_questions']:
        for field in ['retrieval_coverage','answer_coverage']:
            entries=label[field] if reviewed else None
            if entries is not None:
                ids=[e['unit_id'] for e in entries]
                if len(ids)!=len(set(ids)) or not set(ids)<=set(by_unit): raise ValueError('Unknown/duplicate coverage unit')
                for entry in entries: check_support(entry,by_unit[entry['unit_id']],hits,frame['answer'] if field=='answer_coverage' else None)
            else: ids=None
            result[field]=coverage_metrics(selected,ids,review_ids)
    else:
        if label['retrieval_coverage'] is not None or label['answer_coverage'] is not None:
            raise ValueError('Proposal/control questions do not use factual coverage denominator')
        result['retrieval_coverage']=None; result['answer_coverage']=None
    claims=label['claims'] if reviewed else None
    if claims is not None:
        if len({c['id'] for c in claims})!=len(claims): raise ValueError('Duplicate claim identity')
        for claim in claims:
            if not claim['text'] or claim['text'] not in frame['answer']: raise ValueError('Claim text not present in answer')
            if claim['label']=='supported':
                if not claim.get('support'): raise ValueError('Supported claim needs passage quotes')
                for support in claim['support']:
                    hit=hits.get(support['evidence_id'])
                    if hit is None or not support['quote'] or support['quote'] not in hit['text']:
                        raise ValueError('Claim support quote not present')
            if claim.get('citation_verdict') not in {'supports','does_not_support','missing','invalid_id','pending'}:
                raise ValueError('Missing/invalid citation verdict')
    if reviewed and label.get('answer_coverage') and claims==[]:
        raise ValueError('Credited factual coverage requires factual claim annotations')
    result['claims']=claim_metrics([c['label'] for c in claims] if claims is not None else None)
    citation_verdicts=[c['citation_verdict'] for c in claims] if claims is not None else None
    assessed=[v for v in citation_verdicts if v!='missing'] if citation_verdicts is not None else []
    result['citation_support_rate']=sum(v=='supports' for v in assessed)/len(assessed) if assessed and 'pending' not in assessed else None
    result['claims_without_citation']=sum(v=='missing' for v in citation_verdicts) if citation_verdicts is not None else None
    for name,questions,criteria in [('proposal_criteria',rubric['proposal_questions'],rubric['proposal_criteria']),
                                    ('control_criteria',rubric['control_questions'],rubric['control_criteria'])]:
        if qid in questions:
            values=label[name] if reviewed else {k:None for k in criteria}
            result[name]=binary_profile(values,criteria)
            if reviewed:
                for k,value in values.items():
                    if value is None and qid in rubric['control_questions']:
                        raise ValueError('Control criteria always require a reviewed boolean judgment')
                    if value is None and not label.get('not_applicable_reasons',{}).get(k):
                        raise ValueError('Missing criterion needs a reason')
        else:
            if label[name] is not None: raise ValueError('Criterion supplied for the wrong task')
            result[name]=None
    complete = reviewed and claims is not None and not result['claims']['pending_claims']
    if qid in rubric['factual_questions']:
        complete = complete and label['retrieval_coverage'] is not None and label['answer_coverage'] is not None
    if citation_verdicts is not None and 'pending' in citation_verdicts: complete=False
    result['complete_review']=bool(complete)
    return result


def score_study(freeze_path,run_path,review_directory):
    spec,registry,case_id,case,corpus,metadata,rows=validate_runset(freeze_path,run_path)
    review=Path(review_directory); key=read_json(review/'key.private.json')
    if key['freeze_sha256']!=digest_file(freeze_path) or key['case_id']!=case_id or key['run_sha256']!=digest_file(run_path) or key['metadata_sha256']!=digest_file(Path(run_path).with_name('metadata.json')):
        raise ValueError('Review key belongs to another run/freeze')
    for name in ['blind','reference']:
        if digest_file(review/f'{name}.private.json')!=key[f'{name}_sha256']: raise ValueError('Blind packet or reference changed')
    frames=read_json(review/'blind.private.json'); annotations=read_json(review/'annotations.private.json')
    by_id={a['annotation_id']:a for a in annotations}
    if len(by_id)!=len(annotations) or set(by_id)!=set(key['key']): raise ValueError('Missing/unknown/duplicate annotation ID')
    if {f['annotation_id'] for f in frames}!=set(by_id): raise ValueError('Blind packet ID mismatch')
    units=[u for u in registry['units'] if u['cohort_id']==case['study']['cohort_id']]
    scores={}; used_rows=set()
    for frame in frames:
        identifier=frame['annotation_id']; payload={k:v for k,v in frame.items() if k!='annotation_id'}
        if canonical_digest(payload)!=key['key'][identifier]['frame_sha256']: raise ValueError('Review frame changed')
        score=score_label(by_id[identifier],frame,units,[r['id'] for r in corpus],registry['rubric'])
        for index in key['key'][identifier]['run_rows']:
            if type(index) is not int or not 0<=index<len(rows) or index in used_rows: raise ValueError('Invalid/duplicate run mapping')
            if canonical_digest(review_frame(rows[index],case_id))!=key['key'][identifier]['frame_sha256']:
                raise ValueError('Review key maps to a different response')
            used_rows.add(index); scores[index]=score
    if used_rows!=set(range(len(rows))): raise ValueError('A run attempt was dropped')
    complete=all(s['complete_review'] for s in scores.values()) and metadata['status']=='complete'
    outcomes=[]
    for index,row in enumerate(rows):
        outcomes.append({'question_id':row['question_id'],'method':row['method'],'repeat':row['repeat'],
                         'generation_failed':bool(row.get('generation_error')),
                         'format_valid':row.get('structured_validation',{}).get('valid'),**scores[index]})
    paired={}
    if complete:
        from .experiments import paired_bootstrap
        for metric in ['answer_coverage','retrieval_coverage','faithfulness'] + ['proposal/'+k for k in registry['rubric']['proposal_criteria']] + ['control/'+k for k in registry['rubric']['control_criteria']]:
            values={}
            for i,row in enumerate(rows):
                score=scores[i]
                if metric=='faithfulness': value=score['claims']['faithfulness']
                elif '/' in metric:
                    role,criterion=metric.split('/',1); value=(score[role+'_criteria'] or {}).get(criterion)
                else: value=(score[metric] or {}).get('family_macro_coverage')
                if value is not None: values.setdefault((row['question_id'],row['repeat']),{})[row['method']]=value
            pairs={}
            for (q,repeat),pair in values.items():
                if set(pair)=={'traditional','thematic'}: pairs.setdefault(q,[]).append(pair['thematic']-pair['traditional'])
            paired[metric]=paired_bootstrap(pairs)
    operational={}
    for method in ['traditional','thematic']:
        selected_rows=[r for r in rows if r['method']==method]
        durations=[r['total_seconds'] for r in selected_rows]
        successful=[r['total_seconds'] for r in selected_rows if not r.get('generation_error')]
        operational[method]={'attempts':len(selected_rows),'generation_errors':sum(bool(r.get('generation_error')) for r in selected_rows),
                             'all_attempts_seconds_median':statistics.median(durations) if durations else None,
                             'non_api_error_seconds_median':statistics.median(successful) if successful else None,
                             'resources':{}}
        for metric in ['retrieval_seconds','generation_seconds']:
            observed=[r[metric] for r in selected_rows if r.get(metric) is not None]
            operational[method]['resources'][metric]={'observed':len(observed),'missing':len(selected_rows)-len(observed),
                                                     'median':statistics.median(observed) if observed else None,
                                                     'max':max(observed) if observed else None}
        for field in ['prompt_eval_count','eval_count']:
            counts=[r.get('ollama',{}).get(field) for r in selected_rows]
            observed=[n for n in counts if isinstance(n,int)]
            operational[method]['resources'][field]={'observed':len(observed),'missing':len(counts)-len(observed),
                                                     'total':sum(observed) if observed else None}
    return {'operational':operational,'case_id':case_id,'freeze_sha256':digest_file(freeze_path),'annotations_sha256':digest_file(review/'annotations.private.json'),
            'attempts':len(rows),'unique_review_items':len(frames),'reviewed_attempts':sum(s['complete_review'] for s in scores.values()),
            'quality_results_complete':complete,'generation_failures':sum(bool(r.get('generation_error')) for r in rows),
            'invalid_structured_responses':sum(r.get('structured_validation',{}).get('valid') is False for r in rows),
            'paired_quality_comparisons':paired if complete else None,'outcomes':outcomes,
            'note':'No comparative quality summary while reviews or runset are incomplete. Invalid/nonempty outputs remain reviewable; blanks require explicit failed-task annotation, never silent exclusion.'}


def freeze_evaluation(manifest_path,private_root,index_root):
    """Lock inputs now; do not generate answers or invent annotations."""
    manifest_path,private_root,index_root=map(Path,[manifest_path,private_root,index_root])
    if manifest_path.exists() or private_root.exists() or index_root.exists():
        raise FileExistsError('Freeze and index destinations must be new')
    corpus_pointer=read_json('configs/corpus-current.json'); scoring_pointer=read_json('configs/scoring-current.draft.json')
    progress=read_json('docs/family-reference-matrix-progress.json')
    development=read_json('configs/development-current.json')
    if progress.get('approved_packets')!=[1,2,3]: raise ValueError('Three reference packets must be approved')
    if digest_file(scoring_pointer['reference_file'])!=scoring_pointer['reference_units_sha256']:
        raise ValueError('Scoring reference changed')
    scoring_reference=read_json(scoring_pointer['reference_file'])
    if scoring_reference['provenance']['rubric_sha256']!=digest_file(scoring_pointer['rubric']):
        raise ValueError('Rubric changed since scoring-unit preparation')
    if scoring_reference['provenance']['scoring_code_sha256']!=digest_file('src/product_review_insights/scoring.py'):
        raise ValueError('Scoring-unit implementation changed')
    for entry in progress['packets']:
        if digest_file(entry['private_file'])!=entry['packet_sha256']:
            raise ValueError('Approved reference packet changed')
        packet=read_json(entry['private_file'])
        if packet['questions_sha256']!=digest_file('configs/questions.eval.14.draft.json'):
            raise ValueError('Questions changed after reference review')
        approval=read_json(Path(entry['private_file']).parent/f"approval-packet-{entry['packet']}.private.json")
        if approval['decision']!='user_approved' or approval['packet_sha256']!=entry['packet_sha256']:
            raise ValueError('Reference approval does not match packet')
    units=scoring_reference['units']
    if len({u['id'] for u in units})!=len(units): raise ValueError('Duplicate scoring units')
    config=read_json(development['configuration']); config['configuration_role']='frozen_evaluation_v1'
    if digest_file('src/product_review_insights/generation.py')!=development['generation_code_sha256']:
        raise ValueError('Generation contract changed after development selection')
    questions=read_json('configs/questions.eval.14.draft.json')
    if len(questions)!=14 or {q['id'] for q in questions}!={f'Q{i:02d}' for i in range(1,15)}: raise ValueError('Expected fourteen questions')
    for q in questions: q['status']='frozen_evaluation_v1'
    rubric=read_json(scoring_pointer['rubric']); rubric['status']='technically_frozen_v1_not_independent_validation'
    rubric['failure_policy']='All attempts retained. No final paired quality comparison with incomplete reviews. Blank failed answers require explicit zero-coverage/task-failure review; nonempty invalid format remains reviewable.'
    rubric['availability_amendments']='No per-method denominator edits. New known-support eligibility requires a versioned case-level amendment applied symmetrically before method disclosure.'
    private_root.mkdir(parents=True); index_root.mkdir(parents=True)
    questions_path=private_root/'questions.json'; write_json(questions_path,questions)
    encoder_path=Path(config['embedding_model'])
    encoder_files={str(p):digest_file(p) for p in sorted(encoder_path.rglob('*')) if p.is_file()}
    registry={'units':units,'rubric':rubric,'cases':{}}
    cases={}; source_root=Path(corpus_pointer['snapshot'])
    from .retrieval import build
    expected_encoder=None
    paths=sorted(source_root.glob('main/*/corpus.jsonl'))+sorted(source_root.glob('sensitivity/*/*/*/corpus.jsonl'))
    if len(paths)!=30: raise ValueError('Expected three main and 27 sensitivity corpora')
    for path in paths:
        rows=read_corpus(path); corpus_manifest=read_json(path.with_name('manifest.json')); validate_corpus(rows,corpus_manifest,path)
        if corpus_manifest['study']['split']!='evaluation': raise ValueError('Evaluation freeze cannot contain development corpus')
        case_id=str(path.parent.relative_to(source_root)); cid=corpus_manifest['study']['cohort_id']
        relevant=[u for u in units if u['cohort_id']==cid]
        if any(u['product_id'] not in corpus_manifest['allowed_parent_asins'] for u in relevant): raise ValueError('Reference family not in case')
        availability=known_support_availability(relevant,[r['id'] for r in rows])
        is_main=case_id.startswith('main/')
        entry={'study':corpus_manifest['study'],'corpus':str(path),'corpus_sha256':digest_file(path),
               'reviews':len(rows),'repetitions':3 if is_main else 1,'index':None,
               'eligible_unit_counts':{q:sum(u['question_id']==q and availability[u['id']] for u in relevant) for q in sorted(FACTUAL_QUESTIONS)}}
        if is_main:
            artifact=index_root/cid
            meta=build(path,artifact,config)
            if expected_encoder is None: expected_encoder=meta['encoder_files_sha256']
            if meta['encoder_files_sha256']!=expected_encoder: raise ValueError('Primary encoders differ')
            entry.update(index=str(artifact),index_metadata_sha256=digest_file(artifact/'metadata.json'))
        cases[case_id]=entry
        registry['cases'][case_id]={'corpus_sha256':entry['corpus_sha256'],'review_ids':sorted(r['id'] for r in rows),
                                   'available_unit_ids':[uid for uid,present in availability.items() if present]}
    registry_path=private_root/'registry.private.json'; write_json(registry_path,registry)
    bound_files={'requirements.lock.txt':digest_file('requirements.lock.txt'),str(questions_path):digest_file(questions_path),**encoder_files}
    for entry in cases.values():
        bound_files[entry['corpus']]=entry['corpus_sha256']
        manifest=Path(entry['corpus']).with_name('manifest.json'); bound_files[str(manifest)]=digest_file(manifest)
        if entry['index']:
            metadata_path=Path(entry['index'])/'metadata.json'; bound_files[str(metadata_path)]=digest_file(metadata_path)
    empty_secondary=sum(n==0 for name,entry in cases.items() if name.startswith('sensitivity/') for n in entry['eligible_unit_counts'].values())
    spec={'schema':'evaluation_freeze_v1','status':'inputs_technically_frozen_no_final_answers_generated',
          'model_digest':development['tested_model_digest'],'ollama_version':read_json(development['summary'])['ollama_version']['version'],'config':config,'questions_file':str(questions_path),
          'registry_file':str(registry_path),'registry_sha256':digest_file(registry_path),'cases':cases,
          'source_files_sha256':source_fingerprints(),'runtime':runtime_fingerprint(),
          'files_sha256':bound_files,'index_encoder_files_sha256':expected_encoder,
          'reference_type':'audited_non_exhaustive','reference_units':len(units),
          'reference_interpretations_user_approved':True,'independent_annotation':False,
          'scoring_authority':'Technical decomposition and rule lock after user authorization to proceed; not a claim of separate human approval of every scoring facet.',
          'execution_policy':{'primary_repetitions':3,'sensitivity_repetitions':1,'methods':['traditional','thematic'],
                              'rationale':'Three main repetitions for operational variability; single secondary pass limits compute. Same seed/settings for both methods. Exact duplicate response/context frames may share annotation, never timing observations.',
                              'primary_planned_responses':252,'sensitivity_planned_responses':756,
                              'automatic_retries':0,'abort_after_consecutive_generation_errors':3,
                              'resource_measurements':['wall_clock_times','ollama_prompt_tokens','ollama_output_tokens'],
                              'memory_and_process_monitoring':False},
          'limitations':[f'{empty_secondary} sensitivity question/corpus combinations have no known reference anchors; report unavailable coverage, not automatic failure. Other evidence may exist.',
                         'Reference annotations are human judgments, not lexical matching or model-generated grades.',
                         'Same-seed repetitions are not independent tasks. Three cohorts do not isolate a causal heterogeneity effect.',
                         'No final model answer was generated by the freeze process.']}
    manifest_path.parent.mkdir(parents=True,exist_ok=True); write_json(manifest_path,spec)
    load_freeze(manifest_path)
    return {'freeze':str(manifest_path),'cases':len(cases),'primary_indexes':3,'reference_units':len(units),
            'answers_generated':0,'freeze_sha256':digest_file(manifest_path)}
