"""Aggregate parent/item identity; lexical flags are screening, never variant proof."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import pyarrow.parquet as pq
from product_review_insights.data import digest_file

PATTERNS = {
 'version_or_formula_change': r'\b(?:new|old|original|changed|different|previous|reformulat\w*)\b.{0,45}\b(?:formula|formulation|version|applicator|brush|design|packag\w*)\b|\b(?:formula|formulation|applicator|design)\b.{0,45}\b(?:changed|different|new|old)\b',
 'waterproof_variant': r'\b(?:waterproof|water.proof|water.resistant|non.waterproof)\b',
 'size_or_bundle': r'\b(?:mini|travel.size|full.size|sample|pack of|two.pack|three.pack|different sizes)\b',
 'multiple_products_or_comparison': r'\b(?:other|previous|old|different)\b.{0,30}\b(?:model|brand|product|shampoo|mascara|toothbrush)\b',
}


def audit(corpus_root, source, metadata):
    rows = []
    for path in sorted(Path(corpus_root).glob('*/corpus.jsonl')):
        rows += [json.loads(line) for line in path.read_text().splitlines()]
    parents = {r['product_id'] for r in rows}
    raw = Counter(); raw_years = {}; parent_by_item = {}
    parquet = pq.ParquetFile(source)
    for batch in parquet.iter_batches(columns=['parent_asin','asin','timestamp']):
        for row in batch.to_pylist():
            if row['parent_asin'] not in parents: continue
            key = (row['parent_asin'],row['asin']); raw[key] += 1
            parent_by_item.setdefault(row['asin'],set()).add(row['parent_asin'])
            if row['timestamp'] is not None:
                year = datetime.fromtimestamp(row['timestamp']/1000,timezone.utc).year
                raw_years.setdefault(key,[]).append(year)
    meta = {}
    for batch in pq.ParquetFile(metadata).iter_batches(columns=['parent_asin','title','details']):
        for row in batch.to_pylist():
            if row['parent_asin'] in parents: meta.setdefault(row['parent_asin'],[]).append(row)
    items=[];flags=[]
    for parent in sorted(parents):
        family=[r for r in rows if r['product_id']==parent]
        children=sorted({a for r in family for a in r['item_asins']})
        for child in children:
            exact=[r for r in family if r['item_asins']==[child]]
            uncertain=[r for r in family if child in r['item_asins'] and len(r['item_asins'])!=1]
            counts={name:sum(bool(re.search(pattern,r['title']+' '+r['text'],re.I)) for r in exact) for name,pattern in PATTERNS.items()}
            years=raw_years.get((parent,child),[])
            items.append({'parent_asin':parent,'item_asin':child,'eligible_exact_item_reviews':len(exact),
                'ambiguous_lineage_reviews':len(uncertain),'raw_occurrences_not_deduplicated':raw[(parent,child)],
                'raw_year_range':[min(years),max(years)] if years else None,
                'parent_metadata_records':len(meta.get(parent,[])),
                'screening_flag_counts':counts,
                'metadata_granularity':'parent_only_not_historical_item_version',
                'item_shared_across_audited_parents':len(parent_by_item.get(child,set()))>1})
            for r in exact:
                hits=[name for name,pattern in PATTERNS.items() if re.search(pattern,r['title']+' '+r['text'],re.I)]
                if hits: flags.append({'parent_asin':parent,'item_asin':child,'review_id':r['id'],'flags':hits,'text':r['text']})
    report={'schema':'product_identity_audit_v1','source_sha256':digest_file(source),'metadata_sha256':digest_file(metadata),
        'corpora_sha256':{str(p):digest_file(p) for p in sorted(Path(corpus_root).glob('*/corpus.jsonl'))},
        'parents':len(parents),'items':items,'eligible_reviews':len(rows),
        'interpretation':'Exact item ASIN separates observed catalog identities, not historical formula/version. Parent metadata cannot label child variants or all past reviews. Lexical flags may refer to comparisons; no automatic exclusion or homogeneity certification.'}
    return report,flags


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',required=True);p.add_argument('--private-output',required=True)
    args=p.parse_args()
    outputs=[Path(args.output),Path(args.private_output)]
    if any(x.exists() for x in outputs):raise FileExistsError('Preserve earlier audit')
    report,flags=audit('data/processed/study-v2-qa-final/main','data/raw/all_beauty.supplied.parquet','data/raw/meta_all_beauty.parquet')
    for dest,data in zip(outputs,[report,flags]):
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'parents':report['parents'],'item_candidates':len(report['items']),'reviews':report['eligible_reviews'],'screened_flagged_reviews':len(flags)}))

if __name__=='__main__':main()
