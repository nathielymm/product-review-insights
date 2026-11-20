import json
import runpy
from pathlib import Path
import pytest

module=runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/select_development_parameters.py'))


def test_selection_uses_prespecified_unsupervised_ranking_not_thematic_advantage():
    rows=[{'clusters':6,'nondegenerate_all_seeds':True,'mean_cosine_silhouette':.3,'mean_adjusted_rand':.7},
          {'clusters':12,'nondegenerate_all_seeds':True,'mean_cosine_silhouette':.4,'mean_adjusted_rand':.5},
          {'clusters':20,'nondegenerate_all_seeds':False,'mean_cosine_silhouette':.9,'mean_adjusted_rand':.9}]
    assert module['choose_cluster'](rows)==12
    rows[1]['nondegenerate_all_seeds']=False
    assert module['choose_cluster'](rows)==6
    with pytest.raises(ValueError): module['choose_cluster']([rows[2]])


def test_evaluation_and_global_inputs_rejected_before_loading_models(tmp_path):
    index=tmp_path/'index'; index.mkdir(); corpus=tmp_path/'corpus.jsonl'; corpus.write_text('')
    metadata=index/'metadata.json'; manifest=corpus.with_name('manifest.json')
    plan={'allowed_split':'development','allowed_cohort':'development_disjoint'}
    for study in [{},{'split':'evaluation','cohort_id':'compact_mascaras'}]:
        metadata.write_text(json.dumps({'study':study})); manifest.write_text(json.dumps({'study':study}))
        with pytest.raises(ValueError,match='separate development'):
            module['validate_development_source'](index,corpus,plan)


def test_generation_selected_cap_must_remain_feasible_for_both_methods():
    checks=[{'top_k':6,'all_complete':True},{'top_k':8,'all_complete':True},{'top_k':12,'all_complete':False}]
    assert module['choose_top_k'](checks)==8
    assert module['choose_top_k'](checks,6)==6
    with pytest.raises(ValueError,match='fit both'): module['choose_top_k'](checks,12)
    with pytest.raises(ValueError): module['choose_top_k']([],8)
