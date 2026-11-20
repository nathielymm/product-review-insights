"""Downloadable application assets; never modifies the frozen experimental inputs."""
import copy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import urllib.request

from . import generation
from .data import digest_file, redact
from .demo_v2 import Demo
from .evaluation_v2 import fingerprint, verify_runtime
from .retrieval import build

ROOT = Path(__file__).resolve().parents[2]
APP = Path('artifacts/local-app')
RECIPE = Path('configs/local-app.json')
TEMPLATE = Path('configs/product-evaluation.v2.approved-not-frozen.json')


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def download_dataset(spec, destination):
    """Only the pinned public source, with atomic publication and a bounded download."""
    destination = Path(destination)
    if destination.exists():
        if digest_file(destination) != spec['sha256']:
            raise ValueError('Dataset local alterado; remova apenas o download local-app e tente novamente.')
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix('.part')
    url = (f"https://huggingface.co/datasets/{spec['repository']}/resolve/"
           f"{spec['revision']}/{spec['filename']}")
    try:
        with urllib.request.urlopen(url, timeout=120) as response, partial.open('wb') as output:
            size = 0
            while block := response.read(1024 * 1024):
                size += len(block)
                if size > spec['bytes']:
                    raise ValueError('Download maior que o arquivo registrado.')
                output.write(block)
        if size != spec['bytes'] or digest_file(partial) != spec['sha256']:
            raise ValueError('Download incompleto ou checksum do dataset diferente.')
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)
    return destination


def product_corpora(source, product_ids, recipe):
    """Exact item ASIN, English text, deterministic deduplication; no user identifiers."""
    from langdetect import DetectorFactory, detect_langs
    from langdetect.lang_detect_exception import LangDetectException
    DetectorFactory.seed = recipe['language_seed']
    documents = {pid: {} for pid in product_ids}
    with Path(source).open(encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            pid = row.get('asin')
            if pid not in documents or row.get('rating') not in (1, 2, 3, 4, 5):
                continue
            text = redact(' '.join(str(row.get('text') or '').split()))
            title = redact(' '.join(str(row.get('title') or '').split()))
            if len(text.split()) < recipe['min_words']:
                continue
            identity = hashlib.sha256((pid+'\0'+text.casefold()).encode()).hexdigest()
            candidate = {'id': identity, 'product_id': pid, 'text': text,
                         'title': title, 'rating': int(row['rating'])}
            old = documents[pid].get(identity)
            if old:
                candidate = {**candidate, 'text': min(old['text'], text),
                             'title': min(old['title'], title),
                             'rating': min(old['rating'], candidate['rating'])}
            documents[pid][identity] = candidate
    result = {}
    for pid, rows in documents.items():
        selected = []
        for identity in sorted(rows):
            document = rows[identity]
            try:
                languages = detect_langs(document['text'])
            except LangDetectException:
                continue
            if languages and languages[0].lang == recipe['language']:
                selected.append(document)
            if len(selected) == recipe['max_reviews_per_product']:
                break
        if len(selected) < 4:
            raise ValueError('Menos de quatro avaliações elegíveis para '+pid)
        result[pid] = selected
    return result


def local_model(name, pull=True):
    try:
        version = generation.api('/api/version', timeout=10)['version']
        models = generation.api('/api/tags', timeout=10)['models']
    except Exception as error:
        raise RuntimeError('Inicie o Ollama local (ollama serve) e execute a preparação novamente.') from error
    model = next((m for m in models if m['name'] == name), None)
    if model is None and pull:
        print('Baixando '+name+' pelo Ollama local...', flush=True)
        result = generation.api('/api/pull', {'model': name, 'stream': False}, timeout=3600)
        if result.get('status') != 'success':
            raise RuntimeError('Ollama não concluiu o download do modelo.')
        model = next((m for m in generation.api('/api/tags')['models'] if m['name'] == name), None)
    if model is None:
        raise RuntimeError('Modelo local não encontrado: '+name)
    return {'name': name, 'expected_digest': model['digest'],
            'expected_runtime_version': version, 'cloud_allowed': False}


def load_application(root=ROOT):
    root = Path(root)
    manifest = root/APP/'application.json'
    if not manifest.exists():
        raise ValueError('Prepare os arquivos com python scripts/setup_demo.py antes de iniciar.')
    config = read_json(manifest)
    if config.get('schema') != 'local_application_v1':
        raise ValueError('Manifesto local inválido.')
    for path, expected in config['file_hashes'].items():
        target = (root/path).resolve()
        if not target.is_relative_to(root.resolve()) or digest_file(target) != expected:
            raise ValueError('Arquivo da aplicação alterado: '+path)
    if fingerprint(config['build_recipe']) != fingerprint(read_json(root/RECIPE)):
        raise ValueError('Receita alterada; prepare em um clone novo para manter os arquivos existentes.')
    for package, expected in config['library_versions'].items():
        if importlib.metadata.version(package) != expected:
            raise ValueError('Biblioteca mudou desde a preparação: '+package)
    return config, read_json(root/config['questions']['path'])


def application(root=ROOT):
    config, questions = load_application(root)
    return Demo(config=config, questions=questions, root=Path(root))


def prepare(root=ROOT):
    root = Path(root).resolve()
    if Path.cwd().resolve() != root:
        raise ValueError('Execute na raiz do repositório.')
    if (root/APP/'application.json').exists():
        config, _ = load_application(root)
        verify_runtime(config)
        print('Preparação existente conferida; nenhum arquivo experimental foi alterado.')
        return config
    recipe = read_json(root/RECIPE)
    model = local_model(recipe['model'])
    print('Obtendo All_Beauty (327 MB; checksum verificado)...', flush=True)
    source = download_dataset(recipe['dataset'], root/'data/raw/local-app/All_Beauty.jsonl')
    template = read_json(root/TEMPLATE)
    print('Selecionando avaliações dos três produtos...', flush=True)
    corpora = product_corpora(source, [p['product_id'] for p in template['products']], recipe)
    from huggingface_hub import snapshot_download
    from sentence_transformers import SentenceTransformer
    print('Obtendo encoder MiniLM em revisão fixa...', flush=True)
    snapshot = snapshot_download(recipe['encoder']['repository'], revision=recipe['encoder']['revision'],
        allow_patterns=['*.json', '*.safetensors', 'vocab.txt', '1_Pooling/*'])
    encoder = root/APP/'encoder'
    if encoder.exists():
        shutil.rmtree(encoder)
    SentenceTransformer(snapshot, device='cpu', local_files_only=True).save(str(encoder))
    config = {key: copy.deepcopy(template[key]) for key in
              ['generation', 'presentation', 'retrieval', 'clustering', 'questions']}
    config.update(schema='local_application_v1', local_model=model, products=[],
                  embedding_and_index={'encoder_snapshot': str(APP/'encoder')},
                  build_recipe=recipe, experimental_results_reproduced=False)
    settings = {k: v for k, v in config['generation']['config'].items() if k != 'structured_output'}
    settings.update(embedding_model=str(APP/'encoder'), clusters=4, candidate_pool=80, top_k=8)
    for product in template['products']:
        pid = product['product_id']
        folder = root/APP/'corpora'/pid
        folder.mkdir(parents=True, exist_ok=True)
        corpus = folder/'corpus.jsonl'
        corpus.write_text(''.join(json.dumps(d, ensure_ascii=False)+'\n' for d in corpora[pid]), encoding='utf-8')
        index = APP/'indices'/pid
        if (root/index).exists():
            shutil.rmtree(root/index)
        print(f"Indexando {product['label']}: {len(corpora[pid])} avaliações...", flush=True)
        metadata = build(corpus, root/index, settings)
        config['products'].append({'product_id': pid, 'label': product['label'],
            'expected_reviews': len(corpora[pid]), 'chunks': metadata['chunks'],
            'index': str(index), 'corpus_sha256': digest_file(corpus),
            'index_metadata_sha256': digest_file(root/index/'metadata.json')})
    packages = ['numpy', 'scikit-learn', 'faiss-cpu', 'sentence-transformers', 'torch', 'transformers', 'langdetect']
    config['library_versions'] = {name: importlib.metadata.version(name) for name in packages}
    files = [root/RECIPE, root/TEMPLATE, root/config['questions']['path']]
    files += [p for p in (root/APP).rglob('*') if p.is_file()]
    files += list((root/'src/product_review_insights').glob('*.py'))
    files += [root/'scripts'/p for p in ['run_product_pilot.py','run_product_aspect_pilot.py',
                                      'run_product_original_pilot.py','serve_demo.py']]
    config['file_hashes'] = {str(p.relative_to(root)): digest_file(p) for p in sorted(files)}
    # Publish the ready manifest last, after all indices have been built and verified.
    manifest = root/APP/'application.json'
    temporary = manifest.with_suffix('.tmp')
    temporary.write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temporary.replace(manifest)
    load_application(root)
    print('Preparação concluída. Inicie: python scripts/serve_demo.py', flush=True)
    return config
