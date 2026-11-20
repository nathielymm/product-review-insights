import json
import runpy
from pathlib import Path

import pytest

from product_review_insights.data import read_corpus
from product_review_insights.study import materialize_corpus, validate_corpus

finalize = runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/finalize_corpus_qa.py'))['finalize']


def test_qa_revision_preserves_source_and_rebuilds_nested_samples(tmp_path):
    source=tmp_path/'v1'; output=tmp_path/'v2'; report=tmp_path/'report'
    common={k:'test' for k in ['scope_config_sha256','source_sha256','eligible_pool_sha256','audit_exclusion_sha256']}
    common['audited_reviews_reserved']=0
    rows=[{'id':f'r{i:03d}','product_id':'family','text':'A useful synthetic review with enough words to describe a personal care product experience.', 'words':16,'rating':5,'item_asins':['item'],'timestamps_ms':[1500000000000],'duplicate_rating_conflict':False} for i in range(62)]
    rows[1]['text'] += ' -Synthetic Person AMZ reviewer Product Tester'
    manifest=materialize_corpus(rows,source/'main/case',{'cohort_id':'case','scope_id':'test','split':'evaluation','analysis_kind':'primary'},common)
    (source/'preparation-summary.json').write_text(json.dumps({'primary_reviews':62,'development':[]}))
    decisions=tmp_path/'decisions.json'
    decisions.write_text(json.dumps({'exclude_review_ids':['r000'],'redact_signature_review_ids':['r001']}))
    result=finalize(source,output,report,decisions)
    assert result['primary_reviews_after_qa']==61
    original=read_corpus(source/'main/case/corpus.jsonl')
    validate_corpus(original,manifest,source/'main/case/corpus.jsonl')
    revised=read_corpus(output/'main/case/corpus.jsonl')
    assert 'r000' not in {r['id'] for r in revised}
    assert 'Synthetic Person' not in next(r['text'] for r in revised if r['id']=='r001')
    assert '[REDACTED_SIGNATURE]' in next(r['text'] for r in revised if r['id']=='r001')
    for seed in [11,23,37]:
        smaller=set()
        for n in [20,40,60]:
            path=output/f'sensitivity/n{n}/seed{seed}/case/corpus.jsonl'
            subset=read_corpus(path); m=json.loads(path.with_name('manifest.json').read_text())
            validate_corpus(subset,m,path)
            ids={r['id'] for r in subset}
            assert len(ids)==n and smaller<=ids and 'r000' not in ids
            smaller=ids
    with pytest.raises(FileExistsError): finalize(source,output,report,decisions)
