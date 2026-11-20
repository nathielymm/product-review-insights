import copy
import pytest
from product_review_insights.scoring import (compile_units, known_support_availability,
    coverage_metrics, claim_metrics, binary_profile, FACTUAL_QUESTIONS)


def unit(uid,family='a',aspect='odor',groups=None):
    return {'id':uid,'cohort_id':'case','question_id':'Q03','product_id':family,
            'theme_key':aspect,'support_groups':groups if groups is not None else [[uid]]}


def test_joint_contrast_requires_both_sides_but_alternatives_need_only_one():
    units=[unit('contrast',groups=[['positive-a','positive-b'],['negative']])]
    assert not known_support_availability(units,['positive-a'])['contrast']
    assert known_support_availability(units,['positive-b','negative'])['contrast']
    with pytest.raises(ValueError,match='nonempty'): known_support_availability([unit('bad',groups=[])],[])


def test_family_macro_does_not_reward_a_family_with_more_reference_facets():
    units=[unit('one'),unit('two',aspect='discomfort'),unit('three',family='b')]
    scores=coverage_metrics(units,['one','two'],['one','two','three'])
    assert scores['reference_unit_coverage']==pytest.approx(2/3)
    assert scores['family_macro_coverage']==.5
    assert scores['reference_aspect_coverage']==1
    assert scores['per_family_coverage']['b']==0


def test_missing_annotation_empty_denominator_and_explicit_failure_are_distinct():
    units=[unit('one')]
    assert coverage_metrics(units,None,['one'])['reference_unit_coverage'] is None
    assert coverage_metrics(units,[],['one'])['reference_unit_coverage']==0
    scores=coverage_metrics(units,[],[])
    assert scores['reference_unit_coverage'] is None and scores['known_support_retention']==0
    assert claim_metrics(None)['factual_claims'] is None
    assert claim_metrics([])['factual_claims']==0 and claim_metrics([])['faithfulness'] is None
    assert claim_metrics(['supported','pending'])['faithfulness'] is None
    assert claim_metrics(['supported','unsupported','contradicted'])['faithfulness']==pytest.approx(1/3)


def test_coverage_rejects_wrong_scope_unknown_units_and_unavailable_known_support():
    units=[unit('one')]
    with pytest.raises(ValueError,match='Unknown'): coverage_metrics(units,['invented'],['one'])
    with pytest.raises(ValueError,match='adjudicate'): coverage_metrics(units,['one'],[])
    with pytest.raises(ValueError,match='one cohort'): coverage_metrics(units+[{**unit('two'),'question_id':'Q04'}],[],[])
    with pytest.raises(ValueError,match='Duplicate'): coverage_metrics(units+units,[],[])


def facet_fixture():
    cases=[]; specs={q:[None] for q in FACTUAL_QUESTIONS}
    for q in sorted(FACTUAL_QUESTIONS):
        cases.append({'question_id':q,'cells':[{'status':'N','family_key':'F1','product_id':'a','note_pt':'Insufficient','evidence':[]}]})
    cases[0]['cells'][0].update(status='E',note_pt='Reported difficulty',evidence=[{'id':'r1','product_id':'a'},{'id':'r2','product_id':'a'}])
    specs['Q01']=['handling~Reported difficulty@0,1']
    return {'cohort_id':'case','cases':cases},specs


def test_facets_are_explicit_and_deduplicated_with_alternative_anchors():
    packet,specs=facet_fixture(); units=compile_units(packet,specs)
    assert len(units)==1 and units[0]['support_groups']==[['r1','r2']]
    changed=copy.deepcopy(specs); changed['Q01'][0]+=';handling~Same facet repeated@1'
    with pytest.raises(ValueError,match='Duplicate family'): compile_units(packet,changed)
    wrong=copy.deepcopy(packet); wrong['cases'][0]['cells'][0]['evidence'][0]['product_id']='b'
    with pytest.raises(ValueError,match='another family'): compile_units(wrong,specs)
    wrong=copy.deepcopy(packet); wrong['cases'][0]['cells'][0]['status']='P'
    with pytest.raises(ValueError,match='cannot become'): compile_units(wrong,specs)
    wrong=copy.deepcopy(specs); wrong['Q01']=['handling~Wrong index@4']
    with pytest.raises(ValueError,match='outside cell'): compile_units(packet,wrong)


def test_criteria_keep_missing_values_and_do_not_accept_arbitrary_numeric_scores():
    assert binary_profile({'grounded':True,'uncertainty':None},['grounded','uncertainty'])=={'grounded':1,'uncertainty':None}
    with pytest.raises(ValueError): binary_profile({'grounded':1},['grounded'])
    with pytest.raises(ValueError): binary_profile({},['grounded'])
    with pytest.raises(ValueError): claim_metrics(['probably_true'])
