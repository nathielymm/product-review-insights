import runpy
from pathlib import Path
module=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/probe_development_generation.py'))


def test_truncation_and_id_checks_do_not_claim_semantic_faithfulness():
    result={'answer':'A reply [E1]','evidence':[{}],
            'citations':{'invalid_citations':[],'has_valid_citations':True},
            'ollama':{'done_reason':'length','prompt_eval_count':100,'eval_count':1500}}
    checks=module['mechanical_check'](result,'DS05',8192,1)
    assert not checks['not_output_truncated']
    assert checks['no_invalid_citation_ids'] and not checks['semantic_faithfulness_judged']
    result['ollama']['done_reason']='stop'; result['citations']['invalid_citations']=['E1,E2']
    checks=module['mechanical_check'](result,'DS05',1000,1)
    assert not checks['no_invalid_citation_ids'] and not checks['token_counts_within_window']
    result['citations']['has_valid_citations']=False
    assert module['mechanical_check'](result,'DS06',8192,1)['factual_task_has_citation'] is None
