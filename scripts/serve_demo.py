"""Read-only local demonstration; never writes experiment artifacts."""
import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from product_review_insights.generation import (api, pack_context, response_schema,
    validate_and_render_structured, STRUCTURED_SYSTEM)
from product_review_insights.retrieval import Retriever, select_hits

ROOT = Path(__file__).resolve().parents[1]
PRODUCT_LABELS = json.loads((ROOT / 'demo/product-labels.json').read_text())


def product_label(product_id):
    return PRODUCT_LABELS.get(product_id, 'Família de produto não identificada')


COHORTS = {'compact_mascaras': 'Máscaras de cílios',
           'intermediate_hair_disjoint': 'Cuidados e ferramentas para cabelo',
           'varied_disjoint': 'Produtos de funções variadas'}


STUDY = json.loads((ROOT / 'configs/study-scope.json').read_text())
COHORT_PRODUCTS = {c['id']: [{'id': f['parent_asin'], 'name': product_label(f['parent_asin'])}
                            for f in c['families']] for c in STUDY['cohorts']}


DEMO_SYSTEM = STRUCTURED_SYSTEM.replace(
    'Use concise English sentences.',
    'Write observation, proposal, uncertainty and limits in Brazilian Portuguese, '
    'regardless of the question language. Keep JSON keys and citation IDs unchanged. '
    'Use concise sentences. Do not translate or invent source quotes.')


def generate(question, hits, config):
    """Portuguese demonstration contract, isolated from frozen generation code."""
    context, included = pack_context(hits, config['context_chars'])
    if not included:
        return {'answer': 'Evidências insuficientes para responder.', 'evidence': [],
                'ollama': {}, 'structured_validation': {'valid': True}}
    response = api('/api/chat', {
        'model': config['ollama_model'], 'stream': False, 'keep_alive': '10m',
        'messages': [{'role': 'system', 'content': DEMO_SYSTEM},
                     {'role': 'user', 'content': json.dumps({
                         'question': question, 'evidence_jsonl': context,
                         'response_language': 'pt-BR'}, ensure_ascii=False)}],
        'format': response_schema(included),
        'options': {key: config[key] for key in ('temperature', 'seed', 'num_ctx', 'num_predict')}})
    raw = response['message']['content']
    try:
        _, structured = validate_and_render_structured(raw, included)
        products = {h['group_alias']: h['product_id'] for h in included}
        lines = []
        for group, findings in structured['groups'].items():
            for finding in findings:
                lines.append(f"{product_label(products[group])} — {group} ({products[group]}): {finding['observation']} "
                             + ''.join(f'[{c}]' for c in finding['citations']))
                if finding['proposal']:
                    lines.append('Melhoria proposta: ' + finding['proposal'])
                if finding['uncertainty']:
                    lines.append('Incerteza: ' + finding['uncertainty'])
        if structured['limits']:
            lines.append('Limites das evidências: ' + structured['limits'])
        answer, valid = '\n'.join(lines), True
    except (ValueError, KeyError, TypeError):
        answer, valid, structured = raw, False, None
    return {'answer': answer, 'evidence': included, 'structured': structured,
            'structured_validation': {'valid': valid},
            'ollama': {'done_reason': response.get('done_reason')}}


def cited_scope(result):
    """Count cited reviews, deduplicating multiple chunks from the same review."""
    structured = result.get('structured')
    if structured is None:
        return None
    cited = {citation for findings in structured['groups'].values()
             for finding in findings for citation in finding['citations']}
    used = [h for h in result['evidence'] if h['citation_id'] in cited]
    reviews, products = set(), set()
    for hit in used:
        review_id = hit.get('review_id') or (hit.get('id', '').rsplit(':', 1)[0])
        if not review_id or not hit.get('product_id'):
            return None
        reviews.add((hit['product_id'], review_id))
        products.add(hit['product_id'])
    return {'reviews': len(reviews), 'products': len(products)}


class ProductSearch:
    """In-memory search restricted before ranking; existing vectors/clusters are read only."""
    def __init__(self, retriever, product_id):
        import faiss
        import numpy as np
        self.retriever = retriever
        self.indices = [i for i, d in enumerate(retriever.documents) if d['product_id'] == product_id]
        if not self.indices:
            raise ValueError('Não há avaliações disponíveis para este produto.')
        self.index = faiss.IndexFlatIP(retriever.index.d)
        self.index.add(retriever.index.reconstruct_batch(np.asarray(self.indices, dtype='int64')))

    def search(self, question, thematic=False):
        r = self.retriever
        vector = r.model.encode([question], normalize_embeddings=True).astype('float32')
        scores, local_indices = self.index.search(vector, min(r.config['candidate_pool'], len(self.indices)))
        ranked = [self.indices[i] for i in local_indices[0] if i >= 0]
        chosen = select_hits(ranked, r.clusters, r.config['top_k'], thematic)
        score_map = dict(zip(ranked, scores[0].tolist()))
        return [{**r.documents[i], 'cluster': int(r.clusters[i]), 'score': score_map[i]} for i in chosen]


class Demo:
    def __init__(self):
        self.freeze = json.loads((ROOT / 'configs/evaluation-freeze.v1.json').read_text())
        self.retrievers = {}
        self.product_searches = {}
        self.lock = threading.Lock()

    def answer(self, request):
        question = request.get('question', '')
        cohort, method = request.get('cohort'), request.get('method')
        product_id = request.get('product_id', '')
        if not isinstance(question, str) or not question.strip() or len(question) > 2000:
            raise ValueError('Escreva uma pergunta com até 2.000 caracteres.')
        if cohort not in COHORTS or method not in ('traditional', 'thematic'):
            raise ValueError('Escolha um conjunto e um método válidos.')
        if not isinstance(product_id, str) or (product_id and product_id not in {p['id'] for p in COHORT_PRODUCTS[cohort]}):
            raise ValueError('Escolha um produto pertencente ao conjunto selecionado.')
        if not self.lock.acquire(blocking=False):
            raise ValueError('Há uma consulta em andamento. Aguarde e tente novamente.')
        try:
            started = time.perf_counter()
            if cohort not in self.retrievers:
                self.retrievers[cohort] = Retriever(ROOT / self.freeze['cases']['main/' + cohort]['index'])
            searcher = self.retrievers[cohort]
            if product_id:
                key = (cohort, product_id)
                if key not in self.product_searches:
                    self.product_searches[key] = ProductSearch(searcher, product_id)
                searcher = self.product_searches[key]
            hits = searcher.search(question.strip(), thematic=method == 'thematic')
            if product_id:
                assert all(h['product_id'] == product_id for h in hits)
            result = generate(question.strip(), hits, self.freeze['config'])
            # Return only the passages actually included in the model context.
            return {'answer': result['answer'], 'cited_scope': cited_scope(result),
                'products': [
                    {'group': group, 'product_id': next(h['product_id'] for h in result['evidence'] if h['group_alias'] == group),
                     'name': product_label(next(h['product_id'] for h in result['evidence'] if h['group_alias'] == group)),
                     'findings': findings}
                    for group, findings in (result.get('structured') or {}).get('groups', {}).items() if findings],
                'limits': (result.get('structured') or {}).get('limits', ''),
                'evidence': [
                {**{k: h.get(k) for k in ('citation_id', 'group_alias', 'product_id', 'functional_class', 'text')},
                 'product_label': product_label(h.get('product_id'))}
                for h in result['evidence']],
                'seconds': time.perf_counter() - started,
                'format_valid': result.get('structured_validation', {}).get('valid'),
                'cut': result['ollama'].get('done_reason') == 'length',
                'demo_only': True}
        finally:
            self.lock.release()


def make_handler(demo):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not persist questions or consumer text in access logs.

        def reply(self, status, payload, kind='application/json; charset=utf-8'):
            body = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == '/':
                self.reply(200, (ROOT / 'demo/index.html').read_bytes(), 'text/html; charset=utf-8')
            elif self.path == '/api/options':
                self.reply(200, {'cohorts': COHORTS, 'products': COHORT_PRODUCTS})
            else:
                self.reply(404, {'error': 'Página não encontrada.'})

        def do_POST(self):
            if self.path != '/api/ask':
                self.reply(404, {'error': 'Página não encontrada.'})
                return
            # Reject cross-origin requests, including hostile websites targeting localhost.
            origin = self.headers.get('Origin')
            if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}' or (origin and origin != f'http://127.0.0.1:{self.server.server_port}'):
                self.reply(403, {'error': 'Origem não autorizada.'})
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 16000:
                    raise ValueError('Pedido vazio ou muito grande.')
                request = json.loads(self.rfile.read(length))
                if not isinstance(request, dict):
                    raise ValueError('Pedido inválido.')
                self.reply(200, demo.answer(request))
            except (ValueError, TypeError):
                self.reply(400, {'error': 'Confira a pergunta e as opções. Se houver outra consulta em andamento, aguarde.'})
            except Exception:
                self.reply(503, {'error': 'Não foi possível consultar o RAG. Confira os índices locais e o Ollama com gemma3:4b disponível. Nenhuma resposta foi inventada; não houve nova tentativa automática.'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8501)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(Demo()))
    print(f'Demonstração local: http://127.0.0.1:{args.port} — Ctrl+C para encerrar.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
