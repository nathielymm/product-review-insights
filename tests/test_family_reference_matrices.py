import copy
import runpy
from pathlib import Path
import pytest

validate = runpy.run_path(str(Path(__file__).resolve().parents[1]/'scripts/prepare_family_reference_matrices.py'))['validate_cells']


def fixture():
    families=['a','b','c','d','e']
    rows=[{'id':f'{p}123','product_id':p,'text':'Synthetic evidence'} for p in families]
    cells=[{'status':'E','note_pt':'Observed claim','evidence_prefixes':[r['id']]} for r in rows]
    return families,rows,{'Q01':cells}


def test_same_family_evidence_is_required_and_all_cells_present():
    families,rows,cases=fixture()
    assert len(validate(cases,families,rows,['Q01']))==5
    wrong=copy.deepcopy(cases); wrong['Q01'][0]['evidence_prefixes']=['b123']
    with pytest.raises(ValueError,match='different family'): validate(wrong,families,rows,['Q01'])
    with pytest.raises(ValueError,match='every question'): validate(cases,families,rows,['Q01','Q02'])
    missing=copy.deepcopy(cases); missing['Q01'].pop()
    with pytest.raises(ValueError,match='Missing family'): validate(missing,families,rows,['Q01'])


def test_absence_context_hypotheses_and_controls_are_not_conflated():
    families,rows,cases=fixture()
    cases['Q01'][0]={'status':'N','note_pt':'Insufficient evidence, not corpus absence','evidence_prefixes':[]}
    cases['Q01'][1]['status']='P'
    cases['Q01'][2]['status']='H'
    cases['Q13']=[{'status':'C','note_pt':'Cannot establish causal sales increase','evidence_prefixes':[]} for _ in families]
    resolved=validate(cases,families,rows,['Q01','Q13'])
    assert resolved['Q01','a']==[] and resolved['Q13','a']==[]
    bad=copy.deepcopy(cases); bad['Q01'][2]['evidence_prefixes']=[]
    with pytest.raises(ValueError,match='requires supporting'): validate(bad,families,rows,['Q01','Q13'])
    bad=copy.deepcopy(cases); bad['Q13'][0]['status']='N'
    with pytest.raises(ValueError,match='Controls'): validate(bad,families,rows,['Q01','Q13'])
    with pytest.raises(ValueError,match='uniquely'): validate(cases,families,rows+[rows[1]],['Q01','Q13'])
