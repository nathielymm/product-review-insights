"""End-to-end synthetic run/export/annotation tests; no Ollama calls."""
import copy
import json
from pathlib import Path
import pytest
from product_review_insights import experiments
from product_review_insights.data import digest_file,read_corpus
from product_review_insights.study import materialize_corpus
from product_review_insights.frozen_evaluation import (blind_study,load_freeze,read_json,run_frozen,
    runtime_fingerprint,score_study,source_fingerprints,write_json)


def fixture(tmp_path,monkeypatch,fail=False,wrong_model=False):
    root=tmp_path/'case'; study={'scope_id':'synthetic','cohort_id':'case','split':'evaluation','analysis_kind':'primary'}
    rows=[{'id':'ra','product_id':'a','text':'Reported difficulty with removal.','rating':1,'words':5,
           'title':'','functional_class':'test','item_asins':['a-item'],'timestamps_ms':[1500000000000],'duplicate_rating_conflict':False},
          {'id':'rb','product_id':'b','text':'A different product experience.','rating':5,'words':4,
           'title':'','functional_class':'test','item_asins':['b-item'],'timestamps_ms':[1500000000000],'duplicate_rating_conflict':False}]
    manifest=materialize_corpus(rows,root,study,{})
    config={'seed':42,'context_chars':2000,'ollama_model':'gemma3:4b','structured_output':True}
    index=tmp_path/'index'; index.mkdir()
    chunks=[{**r,'id':r['id']+':0','review_id':r['id']} for r in rows]
    (index/'chunks.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in chunks))
    (index/'index.faiss').write_text('synthetic index'); (index/'clusters.npy').write_text('synthetic clusters')
    meta={'study':study,'config':config,'corpus_sha256':manifest['corpus_sha256'],'corpus_manifest':manifest,
          'encoder_files_sha256':{'synthetic':'fixed'},
          **{k:digest_file(index/f) for f,k in [('index.faiss','index_sha256'),('chunks.jsonl','chunks_sha256'),('clusters.npy','clusters_sha256')]}}
    write_json(index/'metadata.json',meta)
    questions=[{'id':'Q01','question':'Use question','scope_required':True},{'id':'Q13','question':'Sales question','scope_required':True}]
    qp=tmp_path/'questions.json'; write_json(qp,questions)
    rubric=read_json('configs/scoring-rubric.v1.draft.json')
    registry={'units':[{'id':'unit-a','cohort_id':'case','question_id':'Q01','product_id':'a','family_key':'F1',
                         'theme_key':'removal','support_groups':[['ra']],'expectation_pt':'Reported difficulty'}],
              'rubric':rubric,'cases':{'main/case':{'corpus_sha256':manifest['corpus_sha256'],'review_ids':['ra','rb'],'available_unit_ids':['unit-a']}}}
    rp=tmp_path/'registry.private.json'; write_json(rp,registry)
    spec={'schema':'evaluation_freeze_v1','registry_file':str(rp),'registry_sha256':digest_file(rp),
          'source_files_sha256':source_fingerprints(),'runtime':runtime_fingerprint(),
          'files_sha256':{str(qp):digest_file(qp)},'config':config,'questions_file':str(qp),
          'index_encoder_files_sha256':meta['encoder_files_sha256'],'model_digest':'fixed-model','ollama_version':'test-version',
          'cases':{'main/case':{'corpus':str(root/'corpus.jsonl'),'corpus_sha256':manifest['corpus_sha256'],
                                'study':study,'repetitions':2,'index':str(index),'index_metadata_sha256':digest_file(index/'metadata.json')}}}
    freeze=tmp_path/'freeze.json'; write_json(freeze,spec)
    class FakeRetriever:
        def __init__(self,path): self.metadata=meta; self.config=config
        def search(self,*args,**kwargs): return chunks
    def fake_api(path,payload=None):
        if path=='/api/tags': return {'models':[{'name':'gemma3:4b','digest':'wrong' if wrong_model else 'fixed-model'}]}
        if path=='/api/version': return {'version':'test-version'}
        return {}
    def fake_generate(q,hits,config):
        if fail and q=='Use question': raise TimeoutError('Synthetic model timeout')
        answer='Reported difficulty [E1].' if q=='Use question' else 'Reviews cannot establish sales.'
        return {'answer':answer,'raw_model_output':answer,
                'evidence':[{**h,'citation_id':f'E{i+1}','group_alias':f'G{i+1}'} for i,h in enumerate(hits)],
                'ollama':{'done_reason':'stop'},'structured_validation':{'valid':True}}
    monkeypatch.setattr(experiments,'Retriever',FakeRetriever); monkeypatch.setattr(experiments,'api',fake_api); monkeypatch.setattr(experiments,'generate',fake_generate)
    return freeze,tmp_path/'run',tmp_path/'review'


def reviewed_labels(review):
    labels=read_json(review/'annotations.private.json'); frames={r['annotation_id']:r for r in read_json(review/'blind.private.json')}
    for label in labels:
        frame=frames[label['annotation_id']]; label['status']='reviewed'
        if frame['question_id']=='Q01':
            support=[{'evidence_id':'E1','quote':'Reported difficulty'}]
            label['retrieval_coverage']=[{'unit_id':'unit-a','support':support}]
            label['answer_coverage']=[{'unit_id':'unit-a','support':support,'answer_quote':'Reported difficulty'}]
            label['claims']=[{'id':'C1','text':'Reported difficulty','label':'supported','support':support,'citation_verdict':'supports'}]
        else:
            label['claims']=[]; label['control_criteria']={k:True for k in label['control_criteria']}
    write_json(review/'annotations.private.json',labels)
    return labels


def test_end_to_end_deduplicates_review_not_attempts_and_missing_scores_stay_absent(tmp_path,monkeypatch):
    freeze,run,review=fixture(tmp_path,monkeypatch)
    assert run_frozen(freeze,'main/case',run)['runs']==8
    exported=blind_study(freeze,run/'runs.jsonl',review)
    assert exported['attempts']==8 and exported['unique_review_items']==2
    frames=read_json(review/'blind.private.json')
    assert all('method' not in f and 'repeat' not in f and 'total_seconds' not in f for f in frames)
    assert all('cluster' not in h and 'score' not in h for f in frames for h in f['evidence'])
    incomplete=score_study(freeze,run/'runs.jsonl',review)
    assert not incomplete['quality_results_complete'] and incomplete['paired_quality_comparisons'] is None
    assert all(r['claims']['faithfulness'] is None for r in incomplete['outcomes'])
    reviewed_labels(review)
    report=score_study(freeze,run/'runs.jsonl',review)
    assert report['quality_results_complete'] and report['reviewed_attempts']==8
    assert report['paired_quality_comparisons']['answer_coverage']['mean_delta_thematic_minus_traditional']==0


def test_review_rejects_fake_quotes_wrong_family_and_swapped_run_mapping(tmp_path,monkeypatch):
    freeze,run,review=fixture(tmp_path,monkeypatch); run_frozen(freeze,'main/case',run); blind_study(freeze,run/'runs.jsonl',review)
    labels=reviewed_labels(review); actual=copy.deepcopy(labels)
    fact=next(a for a in labels if a['answer_coverage'] is not None)
    fact['answer_coverage'][0]['support'][0]['evidence_id']='E2'
    write_json(review/'annotations.private.json',labels)
    with pytest.raises(ValueError,match='another family'): score_study(freeze,run/'runs.jsonl',review)
    labels=copy.deepcopy(actual); fact=next(a for a in labels if a['answer_coverage'] is not None)
    fact['answer_coverage'][0]['answer_quote']='Invented answer quote'
    write_json(review/'annotations.private.json',labels)
    with pytest.raises(ValueError,match='not present in answer'): score_study(freeze,run/'runs.jsonl',review)
    write_json(review/'annotations.private.json',actual)
    key=read_json(review/'key.private.json'); ids=list(key['key']); a,b=ids
    key['key'][a]['run_rows'],key['key'][b]['run_rows']=key['key'][b]['run_rows'],key['key'][a]['run_rows']
    write_json(review/'key.private.json',key)
    with pytest.raises(ValueError,match='different response'): score_study(freeze,run/'runs.jsonl',review)


def test_generation_failures_preserved_and_never_silently_scored_as_success(tmp_path,monkeypatch):
    freeze,run,review=fixture(tmp_path,monkeypatch,fail=True)
    try: run_frozen(freeze,'main/case',run)
    except RuntimeError as error: assert 'three consecutive' in str(error)
    rows=read_corpus(run/'runs.jsonl'); failed=[r for r in rows if r.get('generation_error')]
    assert failed and all(not r['answer'] and r['evidence'] for r in failed)
    exported=blind_study(freeze,run/'runs.jsonl',review)
    assert exported['attempts']==len(rows)
    report=score_study(freeze,run/'runs.jsonl',review)
    assert report['generation_failures']==len(failed) and report['paired_quality_comparisons'] is None


def test_frozen_inputs_and_model_mismatch_stop_before_generation(tmp_path,monkeypatch):
    freeze,run,review=fixture(tmp_path,monkeypatch,wrong_model=True)
    with pytest.raises(ValueError,match='model digest'): run_frozen(freeze,'main/case',run)
    assert not run.exists()
    spec=read_json(freeze); Path(spec['questions_file']).write_text('[]')
    with pytest.raises(ValueError,match='Frozen input changed'): load_freeze(freeze)



def test_runner_never_lists_processes_or_collects_memory(tmp_path,monkeypatch):
    import psutil
    def forbidden(*args,**kwargs): raise AssertionError('Process/memory inspection is out of scope')
    monkeypatch.setattr(psutil,'process_iter',forbidden)
    monkeypatch.setattr(psutil,'Process',forbidden)
    freeze,run,review=fixture(tmp_path,monkeypatch)
    run_frozen(freeze,'main/case',run)
    metadata=read_json(run/'metadata.json')
    assert 'No process enumeration' in metadata['resource_policy']
    assert all(not any('rss' in key or 'cpu_seconds' in key for key in row) for row in read_corpus(run/'runs.jsonl'))
