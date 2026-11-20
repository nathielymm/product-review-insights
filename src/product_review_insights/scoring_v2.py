"""Human/assistant judgments in, reproducible v2 aggregates out. No entailment model."""
import copy
import json
from pathlib import Path
import random
import re
import statistics

from .evaluation_v2 import attempt_id, fingerprint

AXES = ('content', 'qualification', 'contrast')
PROPOSAL_CRITERIA = ('linked_to_supported_problem_with_source',
    'clearly_labeled_as_investigation_not_proven_remedy', 'relevant_to_question',
    'relevant_valued_quality_preserved_with_support', 'specific_validation_needed_identified')
CONTROL_CRITERIA = ('recognizes_insufficient_sales_evidence',
    'distinguishes_investigation_priority_from_commercial_prediction',
    'identifies_relevant_additional_information_or_validation',
    'no_unsupported_numbers_majority_or_product_premises')
LABELS = {'supported', 'contradicted', 'unsupported'}
ERROR_TAGS = ('wrong_person','wrong_product_or_version','wrong_part','condition_or_negation_changed',
              'certainty_increased','unsupported_generalization','wrong_or_missing_citation')


def boolean(value):
    if type(value) is not bool:
        raise ValueError('A completed judgment requires bool, not null/number/pending')
    return value


def supported_ids(ids, evidence, required=False):
    known = {h['citation_id'] for h in evidence}
    if not isinstance(ids, list) or len(ids) != len(set(ids)) or not set(ids) <= known or (required and not ids):
        raise ValueError('Missing, invented or duplicated evidence support')
    return set(ids)


def location_text(row, location):
    """Exact original spans; citations are inherited, never repaired by the annotation."""
    english = row.get('english') or {}
    path = location['path']
    if path == ['raw']:
        text = english.get('raw_model_output', '')
        citations = []
        for anchor in location.get('citation_anchors', []):
            a, b, eid = anchor['start'], anchor['end'], anchor['text']
            if type(a) is not int or type(b) is not int or a < 0 or b <= a or b > len(text) or text[a:b] != eid or not re.fullmatch(r'E\d+', eid):
                raise ValueError('Citation anchor not in original raw output')
            citations.append(eid)
    else:
        data = english.get('structured_output')
        if not data:
            raise ValueError('Structured locator used without a valid structure')
        if path == ['limits']:
            text, citations = data['limits'], []
        elif len(path) == 4 and path[0] == 'groups' and type(path[2]) is int and path[2]>=0 and path[3] in ['observation','proposal','uncertainty']:
            finding = data['groups'][path[1]][path[2]]
            text, citations = finding[path[3]], finding['citations']
        else:
            raise ValueError('Locator must refer to an original text field')
    start, end = location['start'], location['end']
    if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(text) or text[start:end] != location['text']:
        raise ValueError('Annotation rewrote or mislocated original text')
    return location['text'], set(citations)


def location_citations(row, locations):
    if not locations:
        raise ValueError('Positive answer judgment needs original text locations')
    citations = set()
    for loc in locations:
        _, ids = location_text(row, loc)
        citations |= ids
    return citations


def known_groups_met(unit, ids, evidence):
    reviews = {h['review_id'] for h in evidence if h['citation_id'] in ids}
    return all(set(group) & reviews for group in unit['support_review_groups'])


def validate_unit_support(unit, ids, row, note):
    actual = supported_ids(ids, row['evidence'], required=True)
    if not known_groups_met(unit, actual, row['evidence']) and not str(note or '').strip():
        raise ValueError('Alternative evidence needs documented adjudication, not an invented anchor')
    return actual


def claim_metrics(row, claims):
    context_supported = citation_supported = contradicted = unsupported = 0
    seen = set(); tag_counts={k:0 for k in ERROR_TAGS}
    for claim in claims:
        key = claim['id']
        if key in seen:
            raise ValueError('Duplicate claim identifier')
        seen.add(key)
        _, cited = location_text(row, claim['location'])
        if claim['context_label'] not in LABELS:
            raise ValueError('Pending/unknown factual claim label')
        if not str(claim.get('rationale','')).strip():
            raise ValueError('Claim judgment needs rationale')
        ids = supported_ids(claim['support_evidence_ids'], row['evidence'], claim['context_label'] in ['supported','contradicted'])
        correct = boolean(claim['citation_supported'])
        if correct:
            if claim['context_label'] != 'supported' or not cited or not cited <= {e['citation_id'] for e in row['evidence']} or not ids <= cited:
                raise ValueError('Citation success contradicts context label or original citations')
        tags=claim.get('error_tags',[])
        if not isinstance(tags,list) or len(tags)!=len(set(tags)) or not set(tags)<=set(ERROR_TAGS):
            raise ValueError('Invalid error tags')
        for tag in tags:tag_counts[tag]+=1
        context_supported += claim['context_label']=='supported'
        citation_supported += correct
        contradicted += claim['context_label']=='contradicted'
        unsupported += claim['context_label']=='unsupported'
    n = len(claims)
    return {'claims': n, 'supported': context_supported, 'contradicted': contradicted,
            'unsupported': unsupported, 'citation_supported': citation_supported,
            'contradiction_rate':contradicted/n if n else None,'unsupported_rate':unsupported/n if n else None,
            'error_tag_counts':tag_counts,
            'context_fidelity': context_supported/n if n else None,
            'citation_support': citation_supported/n if n else None}


def score_case(row, annotation, unit_case):
    if annotation.get('status') != 'complete' or annotation.get('row_sha256') != fingerprint(row):
        raise ValueError('Incomplete annotation or changed run record')
    if annotation.get('claim_inventory_complete') is not True or annotation.get('proposal_inventory_complete') is not True or annotation.get('deduplication_complete') is not True:
        raise ValueError('Complete inventories must be explicitly confirmed')
    readable = boolean(annotation['readable'])
    raw = (row.get('english') or {}).get('raw_model_output', '')
    if readable and not str(raw).strip():
        raise ValueError('Empty output cannot be marked readable')
    factual = claim_metrics(row, annotation['claims'])
    if not readable and (annotation['claims'] or annotation['proposals']):
        raise ValueError('Unreadable answer cannot have asserted complete claims/proposals')
    result = {'product_id':row['product_id'],'question_id':row['question_id'],'method':row['method'],
              'readable':readable,'factual':factual, 'coverage':{},'proposals':None,'control':None}
    if row['question_id'] in ['Q1','Q2','Q3','Q4']:
        if unit_case is None or (unit_case['product_id'],unit_case['question_id']) != (row['product_id'],row['question_id']):
            raise ValueError('Missing or foreign fixed reference case')
        if set(annotation['coverage']) != set(AXES):
            raise ValueError('Coverage axes incomplete')
        for axis in AXES:
            units = {u['id']:u for u in unit_case[axis]}
            judgments = annotation['coverage'][axis]
            if set(judgments) != set(units):
                raise ValueError('Unknown or omitted denominator unit')
            counts = {'context':0,'answer':0,'answer_in_context':0}
            for uid, j in judgments.items():
                for key in counts:
                    boolean(j[key])
                if not str(j.get('rationale','')).strip():
                    raise ValueError('Coverage judgment needs rationale')
                if j['context']:
                    validate_unit_support(units[uid],j['context_support_ids'],row,j.get('additional_support_note'))
                if j['answer_in_context']:
                    if not j['context'] or not readable:
                        raise ValueError('Answer support cannot exist outside readable answer/context')
                    location_citations(row,j['answer_locations'])
                if j['answer']:
                    if not j['answer_in_context']:
                        raise ValueError('Primary coverage cannot exceed context-grounded answer coverage')
                    ids=validate_unit_support(units[uid],j['answer_support_ids'],row,j.get('additional_support_note'))
                    cited=location_citations(row,j['answer_locations'])
                    if not ids <= cited or not cited <= {e['citation_id'] for e in row['evidence']}:
                        raise ValueError('Coverage citation was repaired/invented')
                for key in counts:
                    counts[key]+=j[key]
            n=len(units)
            result['coverage'][axis]={'denominator':n,**counts,
                'context_rate':counts['context']/n if n else None,
                'answer_rate':counts['answer']/n if n else None,
                'conditional_context_utilization':counts['answer_in_context']/counts['context'] if counts['context'] else None}
    elif annotation['coverage']:
        raise ValueError('Q5/Q6 cannot acquire factual-coverage denominators')
    if row['question_id']!='Q6':
        sums={k:0 for k in PROPOSAL_CRITERIA};seen=set()
        for proposal in annotation['proposals']:
            if proposal['id'] in seen:
                raise ValueError('Duplicate proposal objective identifier')
            seen.add(proposal['id'])
            cited=location_citations(row,proposal['locations'])
            if set(proposal['criteria']) != set(PROPOSAL_CRITERIA) or not str(proposal.get('rationale','')).strip():
                raise ValueError('Proposal criteria/rationale incomplete')
            for k,v in proposal['criteria'].items():
                sums[k]+=boolean(v)
            for k,field in [(PROPOSAL_CRITERIA[0],'problem_support_ids'),(PROPOSAL_CRITERIA[3],'quality_support_ids')]:
                if proposal['criteria'][k]:
                    ids=supported_ids(proposal[field],row['evidence'],required=True)
                    if not ids <= cited:
                        raise ValueError('Proposal support is not in its original cited locations')
        n=len(seen)
        result['proposals']={'objectives':n,'criterion_task_scores':{k:sums[k]/n if n else 0. for k in sums},
            'criterion_precision':{k:sums[k]/n if n else None for k in sums},
            'q5_up_to_two':n<=2 if row['question_id']=='Q5' else None,
            'q5_task_fulfilled':1<=n<=2 if row['question_id']=='Q5' else None}
        if annotation['control'] is not None:
            raise ValueError('Control criteria only apply to Q6')
    else:
        if annotation['proposals']:
            raise ValueError('Control does not create a new proposal metric case')
        control=annotation['control']
        if not isinstance(control,dict) or set(control)!=set(CONTROL_CRITERIA):
            raise ValueError('Control criteria incomplete')
        for v in control.values():boolean(v)
        if not readable and any(control.values()):
            raise ValueError('Unreadable control cannot succeed')
        if control[CONTROL_CRITERIA[3]] and (factual['claims']!=factual['supported'] or factual['claims']!=factual['citation_supported']):
            raise ValueError('Control source-use success contradicts concrete factual errors')
        result['control']=copy.deepcopy(control)
    return result


def annotation_templates(rows, units, seed=20261119):
    primary=[r for r in rows if r['phase']=='primary'];primary=copy.deepcopy(primary)
    random.Random(seed).shuffle(primary)
    cases={(c['product_id'],c['question_id']):c for c in units['cases']}
    templates=[];key={};worksheets=[]
    for n,row in enumerate(primary,1):
        vid=f'V{n:03d}';key[vid]=row['attempt_id'];case=cases.get((row['product_id'],row['question_id']))
        coverage={axis:{u['id']:{'context':None,'answer':None,'answer_in_context':None,
            'context_support_ids':[],'answer_support_ids':[],'answer_locations':[],
            'additional_support_note':'','rationale':''} for u in case[axis]} for axis in AXES} if case else {}
        templates.append({'review_id':vid,'row_sha256':fingerprint(row),'status':'pending','readable':None,
            'claim_inventory_complete':False,'proposal_inventory_complete':False,'deduplication_complete':False,'coverage':coverage,
            'claims':[],'proposals':[],'control':{k:None for k in CONTROL_CRITERIA} if row['question_id']=='Q6' else None,
            'incomplete_fragments':[]})
        worksheets.append({'review_id':vid,'product_id':row['product_id'],'question_id':row['question_id'],
            'question_en':row.get('question_en'),
            'english':{k:v for k,v in (row.get('english') or {}).items() if k in ['raw_model_output','structured_output']},
            'evidence':[{k:v for k,v in e.items() if k in ['citation_id','text','review_id','product_id']} for e in row['evidence']]})
    return templates,key,worksheets


def mean(values):
    return statistics.mean(values) if values else None


def aggregate_cases(cases):
    """Equal question then product weights, not review/claim/target pooling."""
    if len(cases)!=36 or len({(c['product_id'],c['question_id'],c['method']) for c in cases})!=36:
        raise ValueError('Need all 36 primary cases, no stability copies or dropped failures')
    products=sorted({c['product_id'] for c in cases});methods=['traditional','thematic']
    if len(products)!=3 or {(c['product_id'],c['question_id'],c['method']) for c in cases}!={(p,f'Q{q}',m) for p in products for q in range(1,7) for m in methods}:
        raise ValueError('Primary grid differs')
    per_product=[]
    for pid in products:
        for method in methods:
            subset=[c for c in cases if c['product_id']==pid and c['method']==method]
            content=[c for c in subset if c['coverage']];prop=[c for c in subset if c['proposals'] is not None]
            factual=[c['factual'] for c in subset if c['question_id']!='Q6']
            per_product.append({'product_id':pid,'method':method,'scheduled_answers':6,
                'readable_answers':sum(c['readable'] for c in subset),
                'coverage':{a:{metric:mean([c['coverage'][a][metric] for c in content if c['coverage'][a][metric] is not None])
                    for metric in ['context_rate','answer_rate','conditional_context_utilization']} for a in AXES},
                'proposal_task_scores':{k:mean([c['proposals']['criterion_task_scores'][k] for c in prop]) for k in PROPOSAL_CRITERIA},
                'proposal_task_denominator':len(prop),
                'factual_eligible_answers':sum(f['claims']>0 for f in factual),
                'context_fidelity':mean([f['context_fidelity'] for f in factual if f['claims']]),
                'citation_support':mean([f['citation_support'] for f in factual if f['claims']]),
                'contradiction_rate':mean([f['contradiction_rate'] for f in factual if f['claims']]),
                'unsupported_rate':mean([f['unsupported_rate'] for f in factual if f['claims']]),
                'error_tag_counts':{k:sum(f['error_tag_counts'][k] for f in factual) for k in ERROR_TAGS},
                'unique_claims':sum(f['claims'] for f in factual)})
    overall=[]
    for method in methods:
        ps=[p for p in per_product if p['method']==method];controls=[c['control'] for c in cases if c['method']==method and c['control'] is not None]
        selected=[c for c in cases if c['method']==method];q5=[c['proposals'] for c in selected if c['question_id']=='Q5']
        overall.append({'method':method,'scheduled_answers':18,'products':3,
            'coverage':{a:{m:mean([p['coverage'][a][m] for p in ps if p['coverage'][a][m] is not None])
                for m in ['context_rate','answer_rate','conditional_context_utilization']} for a in AXES},
            'proposal_task_scores':{k:mean([p['proposal_task_scores'][k] for p in ps]) for k in PROPOSAL_CRITERIA},
            'proposal_task_denominator':15,
            'context_fidelity_conditional_product_macro':mean([p['context_fidelity'] for p in ps if p['context_fidelity'] is not None]),
            'citation_support_conditional_product_macro':mean([p['citation_support'] for p in ps if p['citation_support'] is not None]),
            'contradiction_rate_conditional_product_macro':mean([p['contradiction_rate'] for p in ps if p['contradiction_rate'] is not None]),
            'unsupported_rate_conditional_product_macro':mean([p['unsupported_rate'] for p in ps if p['unsupported_rate'] is not None]),
            'error_tag_counts':{k:sum(p['error_tag_counts'][k] for p in ps) for k in ERROR_TAGS},
            'factual_eligible_answers':sum(p['factual_eligible_answers'] for p in ps),'factual_task_answers':15,
            'control_denominator':3,'control_pass_counts':{k:sum(c[k] for c in controls) for k in CONTROL_CRITERIA},
            'all_control_criteria_passed':sum(all(c.values()) for c in controls),
            'q5_task_denominator':3,'q5_up_to_two_count':sum(p['q5_up_to_two'] for p in q5),
            'q5_task_fulfilled_count':sum(p['q5_task_fulfilled'] for p in q5),
            'readable_answers':sum(c['readable'] for c in selected)})
    for p in per_product:
        matching=[c for c in cases if c['product_id']==p['product_id'] and c['method']==p['method'] and c['coverage']]
        for axis in AXES:
            p['coverage'][axis]['case_denominator']=len(matching)
            p['coverage'][axis]['reference_targets']=sum(c['coverage'][axis]['denominator'] for c in matching)
            p['coverage'][axis]['conditional_eligible_cases']=sum(c['coverage'][axis]['context']>0 for c in matching)
    for item in overall:
        ps=[p for p in per_product if p['method']==item['method']]
        item['factual_eligible_products']=sum(p['context_fidelity'] is not None for p in ps)
        for axis in AXES:
            item['coverage'][axis]['case_denominator']=12
            item['coverage'][axis]['reference_targets']=sum(p['coverage'][axis]['reference_targets'] for p in ps)
            item['coverage'][axis]['conditional_eligible_cases']=sum(p['coverage'][axis]['conditional_eligible_cases'] for p in ps)
            item['coverage'][axis]['conditional_eligible_products']=sum(p['coverage'][axis]['conditional_context_utilization'] is not None for p in ps)
    return {'role':'descriptive_product_case_study_not_population_inference','per_product':per_product,
            'overall':overall,'no_overall_quality_score':True,
            'fidelity_conditioning':'Null precisions stay null; eligible/failed answers disclosed, never empty=perfect.'}


def export_metrics(rows, annotations, key, units):
    primary=[r for r in rows if r['phase']=='primary'];ids={r['attempt_id']:r for r in primary}
    if len(primary)!=36 or len(ids)!=36 or set(key.values())!=set(ids) or len(key)!=36:
        raise ValueError('Primary run or blind key incomplete')
    if len(annotations)!=36 or {a['review_id'] for a in annotations}!=set(key):
        raise ValueError('Need all 36 primary annotations, including failures')
    unit_cases={(c['product_id'],c['question_id']):c for c in units['cases']}
    cases=[]
    for a in annotations:
        row=ids[key[a['review_id']]]
        cases.append(score_case(row,a,unit_cases.get((row['product_id'],row['question_id']))))
    return aggregate_cases(cases),cases


def resource_summary(rows, translations):
    """Measured times/tokens only. Diagnostic repeats never pool with primary quality."""
    output=[]
    for phase in ['primary','stability']:
        for method in ['traditional','thematic']:
            selected=[r for r in rows if r['phase']==phase and r['method']==method]
            def timing(values):
                measured=[v for v in values if isinstance(v,(int,float)) and not isinstance(v,bool)]
                return {'measured':len(measured),'missing':len(values)-len(measured),
                        'median_seconds':statistics.median(measured) if measured else None,
                        'min_seconds':min(measured) if measured else None,'max_seconds':max(measured) if measured else None}
            item={'phase':phase,'method':method,'scheduled':len(selected),
                  'retrieval':timing([r.get('retrieval_seconds') for r in selected]),
                  'generation_with_guards':timing([r.get('generation_seconds') for r in selected]),
                  'attempt_total':timing([r.get('total_seconds') for r in selected]),
                  'client_index_load':timing([r.get('index_load_seconds') for r in selected]),
                  'model_calls':timing([c.get('wall_seconds') for r in selected for c in r.get('transport',[])]),
                  'retrieval_failures':sum(bool(r.get('retrieval_error')) for r in selected),
                  'generation_errors':sum(bool(r.get('generation_error')) for r in selected),
                  'format_failures':sum(bool(r.get('english')) and not r['english'].get('structured_validation',{}).get('valid',False) for r in selected),
                  'cut_answers':sum((r.get('english') or {}).get('ollama',{}).get('done_reason')=='length' for r in selected)}
            for key in ['prompt_eval_count','eval_count']:
                values=[(r.get('english') or {}).get('ollama',{}).get(key) for r in selected]
                measured=[v for v in values if type(v) is int]
                item[key]={'sum_known':sum(measured),'measured':len(measured),'missing':len(values)-len(measured)}
            if phase=='primary':
                ids={r['attempt_id'] for r in selected};tr=[t for t in translations if t['attempt_id'] in ids]
                item['presentation']={'records':len(tr),'valid':sum(t['translation'].get('valid',False) for t in tr),
                    'attempted':sum(t['translation'].get('attempted',False) for t in tr),
                    'attempted_total_with_guards':timing([t['translation'].get('total_seconds') for t in tr if t['translation'].get('attempted')]),
                    'total_including_budget_guards':timing([t['translation'].get('total_seconds') for t in tr]),
                    'actual_model_calls':timing([c.get('wall_seconds') for t in tr for c in t.get('transport',[])])}
                for key in ['prompt_eval_count','eval_count']:
                    values=[t['translation'].get('ollama',{}).get(key) for t in tr]
                    measured=[v for v in values if type(v) is int]
                    item['presentation'][key]={'sum_known':sum(measured),'measured':len(measured),'missing':len(values)-len(measured)}
            output.append(item)
    return {'groups':output,'technical_probe_costs_are_separate':True,
            'no_cpu_memory_energy_or_monetary_estimates':True}


def stability_summary(rows):
    primary={(r['product_id'],r['question_id'],r['method']):r for r in rows if r['phase']=='primary'}
    results=[]
    for method in ['traditional','thematic']:
        for repetition in [2,3]:
            repeated=[r for r in rows if r['phase']=='stability' and r['method']==method and r['repetition']==repetition]
            if len(repeated)!=6:
                raise ValueError('Diagnostic repeat accounting incomplete')
            comparable=identical=context_same=0
            for r in repeated:
                original=primary[(r['product_id'],r['question_id'],r['method'])]
                a=(original.get('english') or {}).get('raw_model_output','')
                b=(r.get('english') or {}).get('raw_model_output','')
                context_same += [(e['id'],e['text'],e['citation_id']) for e in original['evidence']]==[(e['id'],e['text'],e['citation_id']) for e in r['evidence']]
                if a.strip() and b.strip() and not original.get('generation_error') and not r.get('generation_error'):
                    comparable+=1;identical+=a==b
            results.append({'method':method,'repetition':repetition,'scheduled':6,'comparable_outputs':comparable,
                'identical_original_English':identical,'changed_outputs_requiring_separate_review':comparable-identical,
                'same_context_in_order':context_same,'missing_or_failed_not_counted_as_identical':6-comparable})
    return {'role':'diagnostic_not_independent_quality_cases','groups':results}


def technical_resource_summary(entries):
    def counts(key):
        values=[(e.get('response') or {}).get(key) for e in entries]
        measured=[v for v in values if type(v) is int]
        return {'sum_known':sum(measured),'measured':len(measured),'missing':len(values)-len(measured)}
    measured=[e['wall_seconds'] for e in entries if isinstance(e.get('wall_seconds'),(int,float))]
    return {'role':'technical_checks_not_quality_answers','calls':len(entries),
            'total_measured_wall_seconds':sum(measured),'timing_missing':len(entries)-len(measured),
            'prompt_eval_count':counts('prompt_eval_count'),'eval_count':counts('eval_count')}
