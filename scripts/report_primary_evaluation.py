"""Export aggregate primary results only; require complete, frozen-bound annotations."""
import argparse
import hashlib
import json
import statistics
from pathlib import Path
from product_review_insights.frozen_evaluation import score_study,load_freeze


def mean(values):
    values=[v for v in values if v is not None]
    return statistics.mean(values) if values else None


def question_macro(rows,extract):
    grouped={}
    for row in rows:
        value=extract(row)
        if value is not None: grouped.setdefault(row['question_id'],[]).append(value)
    return {'mean':mean([mean(v) for v in grouped.values()]),'questions':len(grouped)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',default='results/evaluation-v1')
    parser.add_argument('--freeze',default='configs/evaluation-freeze.v1.json')
    parser.add_argument('--output',required=True)
    args=parser.parse_args(); output=Path(args.output)
    if output.exists(): raise FileExistsError('Use a fresh aggregate destination; preserve previous reports')
    spec,registry=load_freeze(args.freeze)
    report={'schema':'primary_evaluation_aggregates_v1','freeze_sha256':hashlib.sha256(Path(args.freeze).read_bytes()).hexdigest(),
            'annotation_provenance':'Assistant semantic annotation; 18 sampled interpretations and 5 calibration items reviewed by user; not independent human ground truth.',
            'human_sample_qualitative_approvals':18,'calibration_qualitative_approvals':5,
            'aggregation':'Within question average repetitions, then equal-weight question mean; coverage additionally macro-averaged over eligible reference families by frozen scorer.',
            'uncertainty':'Frozen paired bootstrap: 2000 resamples of questions, seed 42; repetitions not independent samples; exploratory dependent questions and three case studies.',
            'resource_policy':'Wall time and Ollama token counts only; no memory/process/CPU monitoring; token counts are not monetary cost.',
            'sensitivity_executed':False,'cases':[]}
    for name in ['mascaras','capilar','variado']:
        root=Path(args.root); review=root/(name+'-review'); run=root/name/'runs.jsonl'
        score=score_study(args.freeze,run,review)
        if not score['quality_results_complete'] or score['reviewed_attempts']!=score['attempts']:
            raise ValueError('Cannot publish paired results with incomplete annotations/runset')
        frames=json.loads((review/'blind.private.json').read_text()); labels=json.loads((review/'annotations.private.json').read_text())
        case={'cohort':name,'case_id':score['case_id'],'attempts':score['attempts'],'unique_review_items':len(frames),
              'unique_factual_claims':sum(len(l['claims']) for l in labels),'annotations_sha256':score['annotations_sha256'],
              'run_sha256':hashlib.sha256(run.read_bytes()).hexdigest(),'complete':True,
              'generation_failures':score['generation_failures'],'invalid_structured_responses':score['invalid_structured_responses'],
              'eligible_reference_units':len(json.loads((review/'reference.private.json').read_text())['units']),
              'methods':{},'paired_comparisons':score['paired_quality_comparisons']}
        for method in ['traditional','thematic']:
            rows=[r for r in score['outcomes'] if r['method']==method]
            values={}
            for field in ['retrieval_coverage','answer_coverage']:
                for metric in ['family_macro_coverage','reference_unit_coverage','reference_aspect_coverage']:
                    values[field+'/'+metric]=question_macro(rows,lambda r,f=field,m=metric:(r[f] or {}).get(m))
            for metric in ['faithfulness','contradiction_rate']:
                values[metric]=question_macro(rows,lambda r,m=metric:r['claims'][m])
            values['citation_support_rate']=question_macro(rows,lambda r:r['citation_support_rate'])
            values['claims_without_citation_total_attempt_weighted']=sum(r['claims_without_citation'] or 0 for r in rows)
            for field in ['proposal_criteria','control_criteria']:
                criteria=registry['rubric']['proposal_criteria'] if field=='proposal_criteria' else registry['rubric']['control_criteria']
                values[field]={k:question_macro(rows,lambda r,k=k,f=field:(r[f] or {}).get(k)) for k in criteria}
            values['operational']=score['operational'][method]
            values['format_failures']=sum(r['format_valid'] is False for r in rows)
            case['methods'][method]=values
        report['cases'].append(case)
    report['attempts']=sum(c['attempts'] for c in report['cases'])
    report['unique_review_items']=sum(c['unique_review_items'] for c in report['cases'])
    report['unique_factual_claims']=sum(c['unique_factual_claims'] for c in report['cases'])
    assert report['attempts']==252 and report['unique_review_items']==102
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'attempts':report['attempts'],'items':report['unique_review_items'],'claims':report['unique_factual_claims'],'output':str(output)}))

if __name__=='__main__':main()
