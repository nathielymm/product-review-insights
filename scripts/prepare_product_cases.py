"""Split existing eligible corpora into item-ASIN cases without claiming version purity."""
import argparse
from collections import Counter
import json
from pathlib import Path
from product_review_insights.data import digest_file


def prepare(source_root, output):
    output=Path(output)
    if output.exists():raise FileExistsError('Use a new destination; preserve previous corpora')
    paths=sorted(Path(source_root).glob('*/corpus.jsonl'))
    if not paths:raise ValueError('No source corpora')
    groups={};quarantine=[];seen=set()
    for path in paths:
        for line in path.read_text().splitlines():
            row=json.loads(line)
            if row['id'] in seen:raise ValueError('Duplicate source identity')
            seen.add(row['id'])
            items=row.get('item_asins',[])
            if len(items)!=1 or not items[0]:quarantine.append(row);continue
            item=items[0]
            groups.setdefault((row['product_id'],item),[]).append({**row,'parent_product_id':row['product_id'],'product_id':item})
    # Do not merge an item associated with multiple parent identities silently.
    if len({item for parent,item in groups})!=len(groups):raise ValueError('Item shared across parent identities')
    output.mkdir(parents=True)
    summaries=[]
    for (parent,item),rows in sorted(groups.items()):
        folder=output/'items'/item;folder.mkdir(parents=True)
        corpus=folder/'corpus.jsonl'
        corpus.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in sorted(rows,key=lambda r:r['id'])))
        manifest={'schema':'individual_item_draft_v1','status':'identity_split_not_version_validated_not_evaluation_frozen',
            'item_asin':item,'parent_asin':parent,'reviews':len(rows),'corpus_sha256':digest_file(corpus),
            'rating_counts':dict(sorted(Counter(r['rating'] for r in rows).items())),
            'version_purity_confirmed':False,'topics_rebuilt':False,
            'note':'Exact item identifier only. Historical formula, bundle, version and comparison ambiguity requires review.'}
        (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        summaries.append(manifest)
    if quarantine:(output/'ambiguous-lineage.private.json').write_text(json.dumps(quarantine,ensure_ascii=False,indent=2)+'\n')
    summary={'status':'draft_only','source_corpora_sha256':{str(p):digest_file(p) for p in paths},'input_reviews':len(seen),
        'output_reviews':sum(s['reviews'] for s in summaries),'quarantined_reviews':len(quarantine),'items':summaries}
    assert summary['output_reviews']+len(quarantine)==len(seen)
    (output/'preparation-summary.private.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root',default='data/processed/study-v2-qa-final/main');p.add_argument('--output',required=True)
    a=p.parse_args();s=prepare(a.source_root,a.output)
    print(json.dumps({'items':len(s['items']),'input':s['input_reviews'],'output':s['output_reviews'],'quarantined':s['quarantined_reviews']}))

if __name__=='__main__':main()
