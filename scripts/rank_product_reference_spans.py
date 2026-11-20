"""Inspect sentence/source similarity without certifying or rewriting RAG claims."""
import argparse
import json
from pathlib import Path
import re
import numpy as np
from product_review_insights.data import digest_file

HEDGE=re.compile(r'\b(?:seems?|think|believe|maybe|perhaps|probably|suspect|appears?)\b',re.I)


def rank_candidates(statements,units,statement_vectors,unit_vectors,top_k=3):
    result=[]
    for statement,vector in zip(statements,statement_vectors):
        scores=unit_vectors@vector;order=sorted(range(len(units)),key=lambda i:(-float(scores[i]),i));hits=[];seen=set()
        for i in order:
            unit=units[i]
            if unit['review_id'] in seen:continue
            seen.add(unit['review_id'])
            hits.append({'source_unit_id':unit['id'],'evidence_id':unit['evidence_id'],'similarity':float(scores[i]),
                'in_original_citations':unit['evidence_id'] in statement['original_citations'],
                'source_has_uncertainty_word':bool(HEDGE.search(unit['text']))})
            if len(hits)==top_k:break
        result.append({**statement,'candidate_spans':hits,
            'possible_qualification_loss_not_verified':bool(statement['role']=='observation' and hits and hits[0]['source_has_uncertainty_word'] and not HEDGE.search(statement['text']))})
    return result


def run(spec_path,output):
    output=Path(output)
    if output.exists():raise FileExistsError('Preserve existing alignment')
    spec=json.loads(Path(spec_path).read_text());root=Path(spec['results'])
    if json.loads((root/'reference-audit-status.private.json').read_text())['status']!='complete':raise ValueError('Audit round incomplete')
    rows=[json.loads(l) for l in (root/'reference-audits.private.jsonl').read_text().splitlines()]
    from sentence_transformers import SentenceTransformer
    model=SentenceTransformer(str(Path(spec['index'])/'encoder'),device='cpu',local_files_only=True)
    results=[]
    for row in rows:
        statements=[{**s,'block_id':c['block']['block_id'],'original_citations':c['block']['original_citations']} for c in row['calls'] for s in c['block']['statements']]
        unit_vectors=model.encode([u['text'] for u in row['source_units']],normalize_embeddings=True).astype('float32')
        vectors=model.encode([s['text'] for s in statements],normalize_embeddings=True).astype('float32')
        results.append({'question_id':row['question_id'],'method':row['method'],'source_units':row['source_units'],
           'statements':rank_candidates(statements,row['source_units'],vectors,unit_vectors)})
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps({'role':'similarity_candidates_not_verified_support',
      'script_sha256':digest_file(__file__),'audit_rows_sha256':digest_file(root/'reference-audits.private.jsonl'),
      'encoder_files_sha256':json.loads((Path(spec['index'])/'metadata.json').read_text())['encoder_files_sha256'],
      'policy':'Top sentence per distinct review, three review candidates. Similarity is not entailment or confidence. Hedging flag is lexical, may miss errors or flag valid wording. No rewriting/deletion/replacement of original citations.',
      'rows':results},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'answers':len(results),'statements':sum(len(r['statements']) for r in results),'new_generation_calls':0}))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v7-reference-audit.json');p.add_argument('--output',required=True);a=p.parse_args();run(a.spec,a.output)

if __name__=='__main__':main()
