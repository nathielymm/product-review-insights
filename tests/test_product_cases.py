"""Identity boundary: never silently combine child ASINs or certify historical versions."""
import importlib.util
import json
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('product_cases',Path(__file__).resolve().parents[1]/'scripts/prepare_product_cases.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_split_children_and_quarantine_ambiguous_identity(tmp_path):
    source=tmp_path/'source'/'cohort';source.mkdir(parents=True)
    rows=[{'id':'a','product_id':'parent','item_asins':['child-a'],'rating':5},
          {'id':'b','product_id':'parent','item_asins':['child-b'],'rating':1},
          {'id':'c','product_id':'parent','item_asins':['child-a','child-b'],'rating':3}]
    (source/'corpus.jsonl').write_text('\n'.join(map(json.dumps,rows)))
    output=tmp_path/'output';s=module.prepare(source.parent,output)
    assert s['input_reviews']==3 and s['output_reviews']==2 and s['quarantined_reviews']==1
    for child in ['child-a','child-b']:
        row=json.loads((output/'items'/child/'corpus.jsonl').read_text())
        assert row['product_id']==child and row['parent_product_id']=='parent'
        m=json.loads((output/'items'/child/'manifest.json').read_text())
        assert not m['version_purity_confirmed'] and not m['topics_rebuilt']
    with pytest.raises(FileExistsError):module.prepare(source.parent,output)
    assert json.loads((source/'corpus.jsonl').read_text().splitlines()[0])==rows[0]
