"""Local v2 demonstration; experimental artifacts are read only."""
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from product_review_insights.demo_v2 import Demo, DemoInputError
from product_review_insights.generation import STRUCTURED_SYSTEM
# Compatibility export for archived pilots only; the v2 UI never uses this prompt.
DEMO_SYSTEM = STRUCTURED_SYSTEM.replace(
    'Use concise English sentences.',
    'Write observation, proposal, uncertainty and limits in Brazilian Portuguese, '
    'regardless of the question language. Keep JSON keys and citation IDs unchanged. '
    'Use concise sentences. Do not translate or invent source quotes.')
ROOT = Path(__file__).resolve().parents[1]


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
                self.reply(200, demo.options())
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
                # Parsing errors are user input errors, not model failures.
            except (ValueError, TypeError):
                self.reply(400, {'error': 'Pedido inválido. Confira a pergunta e as opções.'})
                return
            try:
                self.reply(200, demo.answer(request))
            except DemoInputError as error:
                self.reply(400, {'error': str(error)})
            except Exception:
                self.reply(503, {'error': 'Não foi possível consultar o RAG. Confira os índices locais e o Ollama com gemma3:4b disponível. Nenhuma resposta foi inventada; não houve nova tentativa automática.'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8501)
    parser.add_argument('--frozen', action='store_true', help='Use the original experimental assets instead of the downloadable application.')
    args = parser.parse_args()
    os.environ.setdefault('OMP_NUM_THREADS', '1')
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    from product_review_insights.local_app import application
    try:
        demo = Demo() if args.frozen else application()
    except (ValueError, FileNotFoundError) as error:
        parser.exit(1, str(error)+'\n')
    server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(demo))
    print(f'Demonstração local: http://127.0.0.1:{args.port} — Ctrl+C para encerrar.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
