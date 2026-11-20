"""Aggregate the complete frozen sensitivity grid; never turn missing quality into zero."""
import argparse,hashlib,json,statistics
from pathlib import Path
from product_review_insights.frozen_evaluation import load_freeze,score_study
from report_primary_evaluation import question_macro


def mean(values):
    values=[x for x in values if x is not None]
    return statistics.mean(values) if values else None


def observed_sum(values):
    values=[v for v in values if v is not None]
    return sum(values) if values else None


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',default='results/sensitivity-v1-execution')
    p.add_argument('--freeze',default='configs/evaluation-freeze.v1.json')
    p.add_argument('--output',required=True)
    a=p.parse_args(); root=Path(a.root); output=Path(a.output)
    if output.exists():raise FileExistsError('Preserve existing report; use a new destination')
    spec,registry=load_freeze(a.freeze)
    state=json.loads((root/'execution-status.private.json').read_text())
    if state['status']!='complete':raise ValueError('Sensitivity generation is incomplete; do not publish final comparison')
    plan=json.loads((root/'plan.private.json').read_text())['cases']
    assert {x['case_id'] for x in plan}=={x for x in spec['cases'] if x.startswith('sensitivity/')}
    # Require every annotation first, before extracting any comparative aggregates.
    scores=[]
    for item in plan:
        review=Path(item['review']); run=Path(item['run'])/'runs.jsonl'
        score=score_study(a.freeze,run,review)
        if not score['quality_results_complete'] or score['attempts']!=28 or score['reviewed_attempts']!=28:
            raise ValueError('Sensitivity annotation/runset incomplete; keep quality metrics absent')
        scores.append((item,score))
    cases=[]
    timings={}
    for item,score in scores:
        _,size,seed,cohort=item['case_id'].split('/')
        available=registry['cases'][item['case_id']]['available_unit_ids']
        units=[u for u in registry['units'] if u['cohort_id']==cohort]
        availability={q:sum(u['id'] in available for u in units if u['question_id']==q) for q in registry['rubric']['factual_questions']}
        index_metadata=Path(item['index'])/'metadata.json'
        build=json.loads(index_metadata.read_text())
        run_rows=[json.loads(line) for line in (Path(item['run'])/'runs.jsonl').read_text().splitlines()]
        timings[item['case_id']]={m:[r['total_seconds'] for r in run_rows if r['method']==m] for m in ['traditional','thematic']}
        case={'case_id':item['case_id'],'cohort':cohort,'reviews_per_family':int(size[1:]),'sample_seed':int(seed[4:]),'attempts':28,'repetitions':1,'complete':True,
              'run_sha256':hashlib.sha256((Path(item['run'])/'runs.jsonl').read_bytes()).hexdigest(),'annotations_sha256':score['annotations_sha256'],
              'eligible_units':len(available),'total_reference_units':len(units),'eligible_units_by_question':availability,
              'questions_without_known_support':[q for q,n in availability.items() if not n],
              'index_metadata_sha256':hashlib.sha256(index_metadata.read_bytes()).hexdigest(),
              'index_build_seconds':build['build_seconds'],'index_chunks':build['chunks'],
              'output_cuts':sum(r.get('ollama',{}).get('done_reason')=='length' for r in run_rows),
              'unique_factual_claims':sum(len(label['claims']) for label in json.loads((Path(item['review'])/'annotations.private.json').read_text())),
              'unique_review_items':score['unique_review_items'],'generation_failures':score['generation_failures'],
              'invalid_structured_responses':score['invalid_structured_responses'],'methods':{},'paired_comparisons':score['paired_quality_comparisons']}
        for method in ['traditional','thematic']:
            rows=[r for r in score['outcomes'] if r['method']==method]; metrics={}
            for field in ['retrieval_coverage','answer_coverage']:
                metrics[field]=question_macro(rows,lambda r,f=field:(r[f] or {}).get('family_macro_coverage'))
            metrics['faithfulness']=question_macro(rows,lambda r:r['claims']['faithfulness'])
            metrics['contradiction_rate']=question_macro(rows,lambda r:r['claims']['contradiction_rate'])
            metrics['citation_support_rate']=question_macro(rows,lambda r:r['citation_support_rate'])
            for field in ['proposal_criteria','control_criteria']:
                keys=registry['rubric']['proposal_criteria'] if field=='proposal_criteria' else registry['rubric']['control_criteria']
                metrics[field]={k:question_macro(rows,lambda r,f=field,k=k:(r[f] or {}).get(k)) for k in keys}
            metrics['operational']=score['operational'][method]
            metrics['output_cuts']=sum(r.get('ollama',{}).get('done_reason')=='length' for r in run_rows if r['method']==method)
            metrics['format_failures']=sum(r['format_valid'] is False for r in rows)
            case['methods'][method]=metrics
        cases.append(case)
    summary=[]
    for cohort in sorted({c['cohort'] for c in cases}):
        for size in [20,40,60]:
            selected=[c for c in cases if c['cohort']==cohort and c['reviews_per_family']==size]
            assert len(selected)==3 and {c['sample_seed'] for c in selected}=={11,23,37}
            group={'cohort':cohort,'reviews_per_family':size,'sample_seeds':[11,23,37],'methods':{},'differences':{},
                   'eligible_unit_range':[min(c['eligible_units'] for c in selected),max(c['eligible_units'] for c in selected)]}
            for method in ['traditional','thematic']:
                group['methods'][method]={'latency_seconds_median_all_attempts':statistics.median([v for c in selected for v in timings[c['case_id']][method]]),
                    'attempts':sum(c['methods'][method]['operational']['attempts'] for c in selected),
                    'generation_errors':sum(c['methods'][method]['operational']['generation_errors'] for c in selected),
                    'format_failures':sum(c['methods'][method]['format_failures'] for c in selected),
                    'output_cuts':sum(c['methods'][method]['output_cuts'] for c in selected),
                    'tokens':{f:observed_sum(c['methods'][method]['operational']['resources'][f]['total'] for c in selected) for f in ['prompt_eval_count','eval_count']},
                    'tokens_missing':{f:sum(c['methods'][method]['operational']['resources'][f]['missing'] for c in selected) for f in ['prompt_eval_count','eval_count']}}
                for field in ['retrieval_coverage','answer_coverage','faithfulness','contradiction_rate','citation_support_rate']:
                    values=[c['methods'][method][field]['mean'] for c in selected]; observed=[v for v in values if v is not None]
                    group['methods'][method][field]={'seed_mean':mean(values),'seed_range':[min(observed),max(observed)] if observed else None,'observed_seeds':len(observed)}
            for method in ['traditional','thematic']:
                for role in ['proposal_criteria','control_criteria']:
                    keys=registry['rubric'][role]
                    group['methods'][method][role]={}
                    for key in keys:
                        values=[c['methods'][method][role][key]['mean'] for c in selected]
                        observed=[v for v in values if v is not None]
                        group['methods'][method][role][key]={'seed_mean':mean(values),'seed_range':[min(observed),max(observed)] if observed else None,'observed_seeds':len(observed)}
            for field in ['retrieval_coverage','answer_coverage','faithfulness']:
                deltas=[c['methods']['thematic'][field]['mean']-c['methods']['traditional'][field]['mean'] for c in selected if all(c['methods'][m][field]['mean'] is not None for m in ['traditional','thematic'])]
                group['differences'][field]={'mean_thematic_minus_traditional':mean(deltas),'seed_range':[min(deltas),max(deltas)] if deltas else None,'observed_seeds':len(deltas),'positive_seeds':sum(v>0 for v in deltas),'negative_seeds':sum(v<0 for v in deltas),'zero_seeds':sum(v==0 for v in deltas)}
            summary.append(group)
    report={'schema':'sensitivity_aggregates_v1','freeze_sha256':hashlib.sha256(Path(a.freeze).read_bytes()).hexdigest(),
            'cases':cases,'summary_by_cohort_and_size':summary,'attempts':sum(c['attempts'] for c in cases),
            'unique_review_items':sum(c['unique_review_items'] for c in cases),
            'unique_factual_claims':sum(c['unique_factual_claims'] for c in cases),
            'output_cuts':sum(c['output_cuts'] for c in cases),'reference_gap_cases':sum(len(c['questions_without_known_support']) for c in cases),
            'annotation_provenance':'Assistant semantic annotation applying frozen rubric and human-approved interpretation conventions; no independent human validation of sensitivity items.',
            'interpretation':'All 27 cases retained, no selected seeds, one repetition. Coverage denominators vary with known-support availability. Missing denominators remain null. Across-seed ranges are descriptive, not confidence intervals; sizes nested within seed and questions dependent.',
            'resource_policy':'Wall time and Ollama tokens only, no memory/process monitoring.'}
    assert report['attempts']==756 and report['reference_gap_cases']==58
    output.parent.mkdir(parents=True,exist_ok=True); output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'cases':27,'attempts':756,'items':report['unique_review_items'],'output':str(output)}))
if __name__=='__main__':main()
