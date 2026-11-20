"""The public export must not publish a partial sensitivity comparison."""
import importlib.util
import json
import sys
from pathlib import Path
import pytest


def load_report(monkeypatch):
    scripts=Path(__file__).resolve().parents[1]/'scripts'
    monkeypatch.syspath_prepend(str(scripts))
    spec=importlib.util.spec_from_file_location('sensitivity_report',scripts/'report_sensitivity_evaluation.py')
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_incomplete_generation_cannot_publish(tmp_path,monkeypatch):
    module=load_report(monkeypatch)
    (tmp_path/'execution-status.private.json').write_text(json.dumps({'status':'generating'}))
    output=tmp_path/'report.json'
    monkeypatch.setattr(module,'load_freeze',lambda _:({},{}))
    monkeypatch.setattr(sys,'argv',['report','--root',str(tmp_path),'--output',str(output)])
    with pytest.raises(ValueError,match='generation is incomplete'):
        module.main()
    assert not output.exists()


def test_incomplete_annotations_cannot_publish(tmp_path,monkeypatch):
    module=load_report(monkeypatch)
    case={'case_id':'sensitivity/n20/seed11/test','run':str(tmp_path/'run'),'review':str(tmp_path/'review')}
    (tmp_path/'execution-status.private.json').write_text(json.dumps({'status':'complete'}))
    (tmp_path/'plan.private.json').write_text(json.dumps({'cases':[case]}))
    monkeypatch.setattr(module,'load_freeze',lambda _:({'cases':[case['case_id']]},{}))
    monkeypatch.setattr(module,'score_study',lambda *args:{'quality_results_complete':False,'attempts':28,'reviewed_attempts':27})
    output=tmp_path/'report.json'
    monkeypatch.setattr(sys,'argv',['report','--root',str(tmp_path),'--output',str(output)])
    with pytest.raises(ValueError,match='annotation/runset incomplete'):
        module.main()
    assert not output.exists()


def test_export_preserves_existing_report(tmp_path,monkeypatch):
    module=load_report(monkeypatch)
    output=tmp_path/'report.json';output.write_text('original')
    monkeypatch.setattr(sys,'argv',['report','--output',str(output)])
    with pytest.raises(FileExistsError):module.main()
    assert output.read_text()=='original'


def test_complete_export_retains_grid_and_missing_measurements(tmp_path,monkeypatch):
    """Synthetic 27-case export: no private data, model, or real comparison."""
    module=load_report(monkeypatch)
    cohorts=['compact_mascaras','intermediate_hair_disjoint','varied_disjoint']
    questions=[f'Q{n:02d}' for n in range(1,15)]
    factual=questions[:9]
    units=[{'id':c+'/'+q,'cohort_id':c,'question_id':q} for c in cohorts for q in factual]
    rubric={'factual_questions':factual,'proposal_criteria':['proposal'],'control_criteria':['control']}
    plan=[];registry_cases={};scores={}
    for cohort in cohorts:
        for size in [20,40,60]:
            for seed in [11,23,37]:
                n=len(plan);cid=f'sensitivity/n{size}/seed{seed}/{cohort}'
                folder=tmp_path/str(n);folder.mkdir()
                index=folder/'index';index.mkdir()
                (index/'metadata.json').write_text(json.dumps({'build_seconds':.1,'chunks':size*5}))
                review=folder/'review';review.mkdir()
                (review/'annotations.private.json').write_text(json.dumps([{'claims':[{'id':'synthetic'}]}]*28))
                methods=['traditional','thematic']
                rows=[{'method':m,'total_seconds':float(mi+1),'ollama':{'done_reason':'stop'}} for mi,m in enumerate(methods) for q in questions]
                (folder/'runs.jsonl').write_text('\n'.join(json.dumps(r) for r in rows)+'\n')
                selected=[] if n<6 else factual[4:] if n==6 else factual
                registry_cases[cid]={'available_unit_ids':[cohort+'/'+q for q in selected]}
                outcomes=[]
                for m in methods:
                    for q in questions:
                        coverage={'family_macro_coverage':.5} if q in selected else None
                        outcomes.append({'method':m,'question_id':q,'retrieval_coverage':coverage,'answer_coverage':coverage,
                            'claims':{'faithfulness':1.,'contradiction_rate':0.},'citation_support_rate':1.,'format_valid':True,
                            'proposal_criteria':{'proposal':True} if q in questions[9:12] else None,
                            'control_criteria':{'control':True} if q in questions[12:] else None})
                ops={m:{'attempts':14,'generation_errors':0,'resources':{f:{'total':None,'missing':14} for f in ['prompt_eval_count','eval_count']}} for m in methods}
                scores[str(folder/'runs.jsonl')]={'quality_results_complete':True,'attempts':28,'reviewed_attempts':28,
                    'annotations_sha256':'synthetic','unique_review_items':28,'generation_failures':0,'invalid_structured_responses':0,
                    'paired_quality_comparisons':{},'outcomes':outcomes,'operational':ops}
                plan.append({'case_id':cid,'index':str(index),'run':str(folder),'review':str(review)})
    (tmp_path/'execution-status.private.json').write_text(json.dumps({'status':'complete'}))
    (tmp_path/'plan.private.json').write_text(json.dumps({'cases':plan}))
    freeze=tmp_path/'freeze.json';freeze.write_text('{}')
    registry={'cases':registry_cases,'units':units,'rubric':rubric}
    monkeypatch.setattr(module,'load_freeze',lambda _:({'cases':registry_cases},registry))
    monkeypatch.setattr(module,'score_study',lambda freeze,run,review:scores[str(run)])
    output=tmp_path/'aggregate.json'
    monkeypatch.setattr(sys,'argv',['report','--root',str(tmp_path),'--freeze',str(freeze),'--output',str(output)])
    module.main()
    result=json.loads(output.read_text())
    assert len(result['cases'])==27 and result['attempts']==756
    assert result['reference_gap_cases']==58
    group=next(g for g in result['summary_by_cohort_and_size'] if g['cohort']==cohorts[0] and g['reviews_per_family']==20)
    for i,m in enumerate(['traditional','thematic'],1):
        observed=group['methods'][m]
        assert observed['answer_coverage']=={'seed_mean':None,'seed_range':None,'observed_seeds':0}
        assert observed['tokens']=={'prompt_eval_count':None,'eval_count':None}
        assert observed['tokens_missing']=={'prompt_eval_count':42,'eval_count':42}
        assert observed['latency_seconds_median_all_attempts']==i
        assert observed['proposal_criteria']['proposal']['seed_mean']==1
