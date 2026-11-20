"""Obtain public data, local model and per-product indices for a fresh installation."""
import os

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

from product_review_insights.local_app import prepare

if __name__ == '__main__':
    try:
        prepare()
    except Exception as error:
        raise SystemExit('Preparação não concluída: '+str(error)) from error
