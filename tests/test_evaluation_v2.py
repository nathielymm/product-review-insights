import copy
import json
from pathlib import Path
import pytest
from product_review_insights import evaluation_v2 as execution
from product_review_insights import scoring_v2 as scoring


def schedule():
    rows=[]
    for pid in ['p','q','r']:
        for q in range(1,7):
            methods=['traditional','thematic'] if (len(rows)//2)%2==0 else ['thematic','traditional']
            for m in methods:rows.append(dict(phase='primary',product_id=pid,question_id=f'Q{q}',method=m,repetition=1,translate_for_presentation=True))
    for rep in [2,3]:
        for pid in ['p','q','r']:
            for q in ['Q1','Q5']:
                for m in ['traditional','thematic']:rows.append(dict(phase='stability',product_id=pid,question_id=q,method=m,repetition=rep,translate_for_presentation=False))
    for i,r in enumerate(rows,1):r['attempt_order']=i
    return {'english_attempts':rows}


def row(qid='Q1',pid='p',method='traditional',text='The brush fits.'):
    data={'groups':{'G1':[{'citations':['E1'],'observation':text,'proposal':'','uncertainty':''}]},'limits':''}
    r=dict(phase='primary',product_id=pid,question_id=qid,method=method,repetition=1,
           evidence=[dict(citation_id='E1',review_id='r1',product_id=pid,text='It fits.'),dict(citation_id='E2',review_id='r2',product_id=pid,text='Another report.')],
           english={'raw_model_output':json.dumps(data),'structured_output':data},generation_error=None,retrieval_error=None)
    r['attempt_id']=execution.attempt_id(r)
    return r


def unit_case(pid='p',qid='Q1',n=1):
    return {'product_id':pid,'question_id':qid,**{a:[{'id':f'{pid}/{qid}/{a}/{i}','support_review_groups':[['r1']]} for i in range(n)] for a in scoring.AXES}}


def location(text='The brush fits.'):
    return {'path':['groups','G1',0,'observation'],'start':0,'end':len(text),'text':text}


def annotation(r,case=None):
    return dict(status='complete',row_sha256=execution.fingerprint(r),readable=True,
                claim_inventory_complete=True,proposal_inventory_complete=True,deduplication_complete=True,
                claims=[],proposals=[],control={k:False for k in scoring.CONTROL_CRITERIA} if r['question_id']=='Q6' else None,
                coverage={a:{u['id']:dict(context=False,answer=False,answer_in_context=False,context_support_ids=[],answer_support_ids=[],answer_locations=[],additional_support_note='',rationale='Not covered.') for u in case[a]} for a in scoring.AXES} if case else {})


def test_schedule_keeps_stability_separate_and_rejects_dropped_or_wrong_repetitions():
    s=schedule();assert len(execution.validate_schedule(s,['p','q','r']))==60
    for mutate in [lambda x:x['english_attempts'].pop(),lambda x:x['english_attempts'][-1].update(repetition=1),lambda x:x['english_attempts'][0].update(translate_for_presentation=False)]:
        broken=copy.deepcopy(s);mutate(broken)
        with pytest.raises(ValueError):execution.validate_schedule(broken,['p','q','r'])


def test_no_model_calls_or_output_before_explicit_freeze(tmp_path,monkeypatch):
    config=tmp_path/'config.json';config.write_text('{}');output=tmp_path/'new'
    monkeypatch.setattr(execution,'load_configuration',lambda p:({},None,None,None,{}))
    monkeypatch.setattr(execution.generation,'api',lambda *a,**k:pytest.fail('No model call'))
    with pytest.raises(ValueError,match='No authorized'):execution.execute(config,None,output,'unused')
    assert not output.exists()


def test_freeze_requires_both_authorizations_and_exact_code_inputs(tmp_path):
    p=tmp_path/'input';p.write_text('v1');h={str(p):execution.digest_file(p)}
    f={'status':'frozen_user_authorized','user_authorized_freeze':True,'user_authorized_final_generation':True,
       'configuration_sha256':'c','file_hashes':h,'technical_checks':{k:True for k in ['runtime','token_budget','reference_applicability','cluster_inspection','calibration','tests']}}
    execution.validate_freeze(f,'c',h)
    broken=copy.deepcopy(f);broken['user_authorized_final_generation']=False
    with pytest.raises(ValueError):execution.validate_freeze(broken,'c',h)
    p.write_text('changed')
    with pytest.raises(ValueError):execution.validate_freeze(f,'c',h)


def test_existing_run_is_never_overwritten_before_config_loading(tmp_path,monkeypatch):
    output=tmp_path/'old';output.mkdir();(output/'runs.private.jsonl').write_text('keep')
    monkeypatch.setattr(execution,'load_configuration',lambda p:pytest.fail('No input/model loading'))
    with pytest.raises(FileExistsError):execution.execute('unused','unused',output,'unused')
    assert (output/'runs.private.jsonl').read_text()=='keep'


def test_budget_probe_is_separate_and_final_payload_unchanged():
    calls=[];payload={'model':'local','messages':[{'role':'user','content':'input'}],'format':{},'options':{'num_ctx':8192,'num_predict':1536}}
    before=copy.deepcopy(payload)
    def api(path,p,**kw):calls.append(copy.deepcopy(p));return {'prompt_eval_count':100,'eval_count':1,'message':{'content':'{'}}
    transport=execution.BudgetTransport(api)
    transport('/api/chat',payload);transport('/api/chat',payload)
    assert payload==before and len(calls)==3
    assert calls[0]['options']=={'num_ctx':32768,'num_predict':1}
    assert calls[1]==calls[2]==before and len(transport.calls)==2
    with pytest.raises(ValueError):execution.require_budget(7000,payload)


def test_budget_rejects_oversize_before_final_model_call_and_unknown_english():
    calls=[];payload={'model':'local','messages':[],'format':{},'options':{'num_ctx':8192,'num_predict':1536}}
    def api(path,p,**kw):calls.append(p);return {'prompt_eval_count':7000,'eval_count':1}
    transport=execution.BudgetTransport(api)
    with pytest.raises(ValueError):transport('/api/chat',payload)
    assert len(calls)==1 and calls[0]['options']['num_predict']==1
    transport.allow_probe=False
    with pytest.raises(ValueError,match='ledger'):transport('/api/chat',payload)
    assert len(calls)==1


def test_budget_mismatch_retains_actual_raw_response():
    payload={'model':'local','messages':[],'format':{},'options':{'num_ctx':8192,'num_predict':1536}}
    transport=execution.BudgetTransport(lambda *a,**k:{'prompt_eval_count':99,'message':{'content':'retain me'}},
        {execution.input_fingerprint(payload):100})
    with pytest.raises(ValueError,match='differs'):transport('/api/chat',payload)
    assert transport.calls[0]['response']['message']['content']=='retain me'


def test_claim_fidelity_and_original_citation_support_are_distinct():
    r=row();claim={'id':'c','location':location(),'context_label':'supported','support_evidence_ids':['E2'],
                   'citation_supported':False,'rationale':'Supported elsewhere, not by original E1.'}
    m=scoring.claim_metrics(r,[claim]);assert m['context_fidelity']==1 and m['citation_support']==0
    claim['citation_supported']=True
    with pytest.raises(ValueError):scoring.claim_metrics(r,[claim])
    claim.update(context_label='unsupported',support_evidence_ids=[])
    with pytest.raises(ValueError):scoring.claim_metrics(r,[claim])


def test_claim_cannot_rewrite_source_text_or_accept_missing_counterevidence():
    r=row();claim={'id':'c','location':location('Changed text!!'),'context_label':'supported','support_evidence_ids':['E1'],
                   'citation_supported':True,'rationale':'test'}
    with pytest.raises(ValueError):scoring.claim_metrics(r,[claim])
    claim.update(location=location(),context_label='contradicted',support_evidence_ids=[],citation_supported=False)
    with pytest.raises(ValueError):scoring.claim_metrics(r,[claim])


def test_coverage_keeps_fixed_denominator_and_conditional_diagnostic_separate():
    r=row();c=unit_case(n=2);a=annotation(r,c)
    for axis in scoring.AXES:
        j=next(iter(a['coverage'][axis].values()));j.update(context=True,answer=True,answer_in_context=True,
            context_support_ids=['E1'],answer_support_ids=['E1'],answer_locations=[location()],rationale='Supported point.')
    result=scoring.score_case(r,a,c)
    assert result['coverage']['content']['denominator']==2
    assert result['coverage']['content']['answer_rate']==.5
    assert result['coverage']['content']['conditional_context_utilization']==1
    assert all(v==0 for v in result['proposals']['criterion_task_scores'].values())
    assert all(v is None for v in result['proposals']['criterion_precision'].values())
    del a['coverage']['content'][next(iter(a['coverage']['content']))]
    with pytest.raises(ValueError,match='denominator'):scoring.score_case(r,a,c)


def test_alternative_evidence_requires_documented_adjudication():
    r=row();c=unit_case();a=annotation(r,c)
    for axis in scoring.AXES:
        j=next(iter(a['coverage'][axis].values()));j.update(context=True,context_support_ids=['E2'])
    with pytest.raises(ValueError,match='adjudication'):scoring.score_case(r,a,c)
    for axis in scoring.AXES:next(iter(a['coverage'][axis].values()))['additional_support_note']='Verified alternative report supports this same target.'
    assert scoring.score_case(r,a,c)['coverage']['content']['context_rate']==1


def test_proposals_preserve_all_objectives_and_q5_limit_not_choose_best():
    r=row(qid='Q5');a=annotation(r)
    for n in range(3):a['proposals'].append({'id':str(n),'locations':[location()],
        'criteria':{k:True for k in scoring.PROPOSAL_CRITERIA},'problem_support_ids':['E1'],
        'quality_support_ids':['E1'],'rationale':'Synthetic validation of accounting, not semantics.'})
    result=scoring.score_case(r,a,None)
    assert result['proposals']['objectives']==3 and result['proposals']['q5_up_to_two'] is False
    a['proposals'][2]['criteria'][scoring.PROPOSAL_CRITERIA[0]]=False
    assert scoring.score_case(r,a,None)['proposals']['criterion_task_scores'][scoring.PROPOSAL_CRITERIA[0]]==pytest.approx(2/3)


def test_empty_control_cannot_receive_perfect_score_or_factual_precision():
    r=row(qid='Q6');r['english']=None;a=annotation(r);a.update(readable=False,row_sha256=execution.fingerprint(r))
    result=scoring.score_case(r,a,None)
    assert result['factual']['context_fidelity'] is None and not any(result['control'].values())
    a['control'][scoring.CONTROL_CRITERIA[0]]=True
    with pytest.raises(ValueError):scoring.score_case(r,a,None)


def test_pending_inventory_and_changed_run_block_metric_export():
    r=row();c=unit_case();a=annotation(r,c);a['deduplication_complete']=False
    with pytest.raises(ValueError):scoring.score_case(r,a,c)
    a['deduplication_complete']=True;r['english']['raw_model_output']='changed'
    with pytest.raises(ValueError,match='changed'):scoring.score_case(r,a,c)


def test_macro_aggregation_keeps_empty_failures_and_equal_product_weights():
    cases=[]
    for pid in ['p','q','r']:
        for q in range(1,7):
            for m in ['traditional','thematic']:
                r=row(f'Q{q}',pid,m);r['english']=None;c=unit_case(pid,f'Q{q}',1 if pid=='p' else 9) if q<=4 else None
                a=annotation(r,c);a['readable']=False
                result=scoring.score_case(r,a,c)
                if pid=='p' and q<=4:result['coverage']['content']['answer_rate']=1.0
                cases.append(result)
    result=scoring.aggregate_cases(cases)
    assert result['overall'][0]['coverage']['content']['answer_rate']==pytest.approx(1/3)
    assert result['overall'][0]['scheduled_answers']==18 and result['overall'][0]['proposal_task_denominator']==15
    assert result['overall'][0]['control_denominator']==3
    assert result['overall'][0]['context_fidelity_conditional_product_macro'] is None
    with pytest.raises(ValueError):scoring.aggregate_cases(cases[:-1])


def test_annotation_templates_are_pending_blinded_and_bound_to_unchanged_rows():
    r=row();r['english']['private_method_label']='traditional';units={'cases':[unit_case()]}
    templates,key,worksheets=scoring.annotation_templates([r],units)
    assert templates[0]['status']=='pending' and not templates[0]['claim_inventory_complete']
    assert key[templates[0]['review_id']]==r['attempt_id']
    assert 'method' not in worksheets[0] and 'private_method_label' not in worksheets[0]['english']
    assert templates[0]['row_sha256']==execution.fingerprint(r)


def test_full_scheduled_execution_preserves_failed_attempt_and_defers_translations(tmp_path,monkeypatch):
    """Synthetic transport only: no project freeze or real model request is created."""
    monkeypatch.chdir(tmp_path)
    config_path=tmp_path/'config.json';config_path.write_text('{}')
    settings={'generation':{'config':{}},'presentation':dict(model='mock',num_ctx=8192,num_predict=1536,temperature=0,seed=42),
              'products':[{'product_id':p,'index':'unused'} for p in ['p','q','r']]}
    sched=schedule();ledger=tmp_path/'tokens.jsonl';ledger.write_text('')
    freeze={'status':'frozen_user_authorized','user_authorized_freeze':True,'user_authorized_final_generation':True,
            'configuration_sha256':execution.digest_file(config_path),'file_hashes':{},
            'technical_checks':{k:True for k in ['runtime','token_budget','reference_applicability','cluster_inspection','calibration','tests']},
            'token_ledger_sha256':execution.digest_file(ledger)}
    freeze_path=tmp_path/'synthetic-freeze.json';freeze_path.write_text(json.dumps(freeze))
    monkeypatch.setattr(execution,'load_configuration',lambda p:(settings,{},sched,{},{}))
    monkeypatch.setattr(execution,'verify_runtime',lambda c:{'runtime_version':'mock','model_digest':'mock'})
    import product_review_insights.retrieval as retrieval
    monkeypatch.setattr(retrieval,'Retriever',lambda p:object())
    evidence=row()['evidence'][:1]
    monkeypatch.setattr(execution,'prepare_attempt',lambda *a:({'generation_question_en':'Synthetic question'},evidence,evidence,{'retrieval_seconds':.01,'candidate_pool_sha256':'same'}))
    events=[]
    def generate(*args):
        events.append('English')
        if len(events)==1:raise RuntimeError('Synthetic failure, preserve it')
        return {**row()['english'],'evidence':copy.deepcopy(evidence)}
    monkeypatch.setattr(execution.generation,'generate',generate)
    class Original:
        @staticmethod
        def translate_presentation(*args):
            assert events.count('English')==60
            events.append('translation');return {'valid':True,'total_seconds':.01}
    monkeypatch.setattr(execution,'helpers',lambda:(None,Original))
    result=execution.execute(config_path,freeze_path,Path('results')/'synthetic',ledger)
    assert result=={'english_records':60,'translation_records':36}
    records=[json.loads(l) for l in Path('results/synthetic/runs.private.jsonl').read_text().splitlines()]
    translations=[json.loads(l) for l in Path('results/synthetic/translations.private.jsonl').read_text().splitlines()]
    assert records[0]['generation_error'] and records[0]['english'] is None
    assert events.count('English')==60 and events.count('translation')==35
    assert len(translations)==36 and not translations[0]['translation']['attempted']
    status=json.loads(Path('results/synthetic/status.private.json').read_text())
    assert status['runs_sha256']==execution.digest_file('results/synthetic/runs.private.jsonl')
    assert status['translations_sha256']==execution.digest_file('results/synthetic/translations.private.jsonl')


def test_stability_does_not_count_matching_empty_failures_as_success():
    rows=[]
    for spec in schedule()['english_attempts']:
        r=row(spec['question_id'],spec['product_id'],spec['method']);r.update(spec);r['attempt_id']=execution.attempt_id(r)
        r['evidence']=[dict(id='chunk',text='Evidence',citation_id='E1')]
        r['english']=None;rows.append(r)
    summary=scoring.stability_summary(rows)
    assert all(g['comparable_outputs']==g['identical_original_English']==0 for g in summary['groups'])
    assert all(g['missing_or_failed_not_counted_as_identical']==6 for g in summary['groups'])


def test_blind_export_requires_complete_grid_and_never_leaks_annotations():
    rows=[];cases=[]
    for pid in ['p','q','r']:
        for q in range(1,7):
            if q<=4:cases.append(unit_case(pid,f'Q{q}'))
            for m in ['traditional','thematic']:
                r=row(f'Q{q}',pid,m);r['english']=None;rows.append(r)
    units={'cases':cases};templates,key,_=scoring.annotation_templates(rows,units)
    with pytest.raises(ValueError):scoring.export_metrics(rows,templates,key,units)
    byid={r['attempt_id']:r for r in rows};bycase={(c['product_id'],c['question_id']):c for c in cases}
    annotations=[]
    for t in templates:
        r=byid[key[t['review_id']]];a=annotation(r,bycase.get((r['product_id'],r['question_id'])));a.update(review_id=t['review_id'],readable=False);annotations.append(a)
    public,private=scoring.export_metrics(rows,annotations,key,units)
    assert len(private)==36 and len(public['overall'])==2
    serialized=json.dumps(public)
    assert 'The brush fits.' not in serialized and 'rationale' not in serialized and 'row_sha256' not in serialized


def test_aggregate_json_is_stable_across_python_hash_seeds():
    import os
    import subprocess
    import sys
    code='from product_review_insights.scoring_v2 import claim_metrics; import json; print(json.dumps(claim_metrics({}, [])))'
    outputs=[]
    for seed in ['1','2']:
        env={**os.environ,'PYTHONHASHSEED':seed,'PYTHONPATH':str(Path(__file__).resolve().parents[1]/'src')}
        outputs.append(subprocess.check_output([sys.executable,'-c',code],env=env,text=True))
    assert outputs[0]==outputs[1]


def test_changed_technical_evidence_is_rejected_before_any_network_or_data_loading(tmp_path,monkeypatch):
    report=tmp_path/'report.json';report.write_text('{}')
    config=tmp_path/'config.json';config.write_text(json.dumps({'technical_evidence':{'runtime':{'path':str(report),'sha256':'not-the-approved-hash'}}}))
    monkeypatch.setattr(execution.generation,'api',lambda *a,**k:pytest.fail('No network check before input integrity'))
    with pytest.raises(ValueError,match='checksum'):execution.load_configuration(config)


def test_missing_resource_measurement_is_not_fabricated_as_zero_latency():
    r=row();r.update(english=None,retrieval_seconds=None,generation_seconds=None,transport=[],generation_error='missing response')
    summary=scoring.resource_summary([r],[])
    main=next(g for g in summary['groups'] if g['phase']=='primary' and g['method']=='traditional')
    assert main['scheduled']==1 and main['retrieval']['measured']==0
    assert main['retrieval']['median_seconds'] is None and main['retrieval']['missing']==1
    assert main['prompt_eval_count']=={'sum_known':0,'measured':0,'missing':1}
    assert main['presentation']['attempted']==0
    assert main['presentation']['attempted_total_with_guards']['median_seconds'] is None
