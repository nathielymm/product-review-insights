"""Separate original English generation metrics from presentation translation metrics."""
import argparse
import hashlib
import json
from pathlib import Path
from product_review_insights import generation
from run_product_original_pilot import translation_fields


def check_translation_structure(english, translated):
    if set(english)!=set(translated) or set(english['groups'])!=set(translated['groups']):return False
    for group,findings in english['groups'].items():
        other=translated['groups'][group]
        if len(findings)!=len(other):return False
        for a,b in zip(findings,other):
            if set(a)!=set(b) or a['citations']!=b['citations']:return False
            for key in ['observation','proposal','uncertainty']:
                if not a[key] and b[key]:return False
    return True


def report(spec_path):
    spec=json.loads(Path(spec_path).read_text());root=Path(spec['results']);base=Path(spec['baseline_results'])
    if json.loads((root/'status.private.json').read_text())['status']!='complete':raise ValueError('Incomplete run')
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()];old=[json.loads(l) for l in (base/'runs.private.jsonl').read_text().splitlines()]
    expected={(q['id'],m) for q in spec['questions'] for m in ['traditional','thematic']}
    if len(rows)!=4 or len(old)!=4 or {(r['question_id'],r['method']) for r in rows}!=expected or {(r['question_id'],r['method']) for r in old}!=expected:raise ValueError('Incomplete grid')
    prior={(r['question_id'],r['method']):r for r in old};outcomes=[]
    for row in rows:
        previous=prior[(row['question_id'],row['method'])]
        if row['candidate_pool_sha256']!=previous['candidate_pool_sha256'] or [(h['id'],h['text']) for h in row['evidence']]!=[(h['id'],h['text']) for h in previous['evidence']]:raise ValueError('Retrieval changed')
        english=row['english'];translation=row['translation'];data=english['structured_output'] if english else None
        citations={c for fs in data['groups'].values() for f in fs for c in f['citations']} if data else set()
        if english:
            if english['generation_contract']['system_prompt']!=generation.STRUCTURED_SYSTEM:raise ValueError('Original English prompt differs')
            if not row['english_preserved_after_translation']:raise ValueError('English mutated')
        preserved=None
        if translation and translation['valid']:
            preserved=check_translation_structure(data,translation['structured_pt'])
            if not preserved:raise ValueError('Presentation structure/citations changed')
        material=row['source_material']
        if material is not None:
            by_id={h['citation_id']:h for h in row['evidence']}
            if {m['evidence_id'] for m in material}!=citations:raise ValueError('Source set differs')
            for m in material:
                h=by_id[m['evidence_id']]
                if m!={'evidence_id':h['citation_id'],'product_id':h['product_id'],'review_id':h['review_id'],'text':h['text']}:raise ValueError('Source text changed')
        outcomes.append({'question_id':row['question_id'],'method':row['method'],'context_matches_round_5':True,
          'included_reviews':len({h['review_id'] for h in row['evidence']}),
          'cited_unique_reviews':len({h['review_id'] for h in row['evidence'] if h['citation_id'] in citations}) if data else None,
          'english_findings':sum(len(fs) for fs in data['groups'].values()) if data else None,
          'english_valid':(english or {}).get('structured_validation',{}).get('valid'),
          'english_cut':(english or {}).get('ollama',{}).get('done_reason')=='length','generation_error':bool(row['generation_error']),
          'translation_attempted':(translation or {}).get('attempted',False),'translation_valid':(translation or {}).get('valid',False),
          'translation_cut':(translation or {}).get('ollama',{}).get('done_reason')=='length','translation_error':bool((translation or {}).get('generation_error')),
          'translation_structure_and_citations_preserved':preserved,
          'retrieval_seconds':row['retrieval_seconds'],'generation_seconds':row['generation_seconds'],
          'translation_seconds':(translation or {}).get('total_seconds',0.),'total_seconds':row['total_seconds'],
          'generation_tokens':{k:(english or {}).get('ollama',{}).get(k) for k in ['prompt_eval_count','eval_count']},
          'translation_tokens':{k:(translation or {}).get('ollama',{}).get(k) for k in ['prompt_eval_count','eval_count']},
          'previous_generation_source_calls':previous['actual_source_calls'],'previous_total_seconds':previous['total_seconds']})
    p=json.loads((root/'provenance.private.json').read_text());p5=json.loads((base/'provenance.private.json').read_text())
    assert p['model_digest']==p5['model_digest'] and p['index_metadata_sha256']==p5['index_metadata_sha256']
    assert p['baseline_runs_sha256']==hashlib.sha256((base/'runs.private.jsonl').read_bytes()).hexdigest()
    return {'schema':'original_english_product_pilot_v6_aggregates','role':'development_only','product_id':spec['product_id'],
      'answers':4,'generation_calls':4,'translation_calls':sum(o['translation_attempted'] for o in outcomes),
      'spec_sha256':hashlib.sha256(Path(spec_path).read_bytes()).hexdigest(),'runs_sha256':hashlib.sha256((root/'runs.private.jsonl').read_bytes()).hexdigest(),
      'baseline_runs_sha256':p['baseline_runs_sha256'],'original_generation_code_sha256':p['original_generation_code_sha256'],
      'model_digest':p['model_digest'],'index_metadata_sha256':p['index_metadata_sha256'],'outcomes':outcomes,
      'restoration_scope':'Original English function/prompt/schema/options, not original multi-product corpus or entire retrieval design. Aspect retrieval and product-local groups retained.',
      'interpretation':'Translation syntax and citation preservation are not linguistic or semantic fidelity. English and translation reviewed separately by assistant after labels, no independent score or winner. Translation has its own output budget/cost. Earlier rounds preserved.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v6-original-english.json');p.add_argument('--output',required=True);a=p.parse_args()
    output=Path(a.output)
    if output.exists():raise FileExistsError('Preserve report; choose a new output')
    data=report(a.spec);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
