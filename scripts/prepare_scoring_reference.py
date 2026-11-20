"""Prepare aspect units and known-evidence availability; no model or answer scoring."""
import argparse
import collections
import json
from pathlib import Path

from product_review_insights.data import digest_file, read_corpus
from product_review_insights.scoring import compile_units, known_support_availability
from product_review_insights.study import validate_corpus


def prepare(destination):
    destination=Path(destination)
    if destination.exists():
        raise FileExistsError('Use a new destination to preserve scoring snapshots')
    progress_path=Path('docs/family-reference-matrix-progress.json')
    progress=json.loads(progress_path.read_text())
    facets_path=Path('configs/scoring-facets.v1.draft.json')
    facets=json.loads(facets_path.read_text())
    rubric_path=Path('configs/scoring-rubric.v1.draft.json')
    rubric=json.loads(rubric_path.read_text())
    pointer=json.loads(Path('configs/corpus-current.json').read_text())
    corpus_root=Path(pointer['snapshot'])
    units=[]; packet_hashes={}; cell_statuses=collections.Counter(); main={}
    if progress.get('approved_packets') != [1,2,3]:
        raise ValueError('All three revised packets must have recorded approval')
    for entry in progress['packets']:
        path=Path(entry['private_file'])
        if digest_file(path)!=entry['packet_sha256']:
            raise ValueError('Approved packet changed')
        approval=json.loads((path.parent/f"approval-packet-{entry['packet']}.private.json").read_text())
        if approval['decision']!='user_approved' or approval['packet_sha256']!=entry['packet_sha256']:
            raise ValueError('Approval does not bind current packet')
        packet=json.loads(path.read_text()); cid=entry['cohort_id']
        corpus=corpus_root/'main'/cid/'corpus.jsonl'; rows=read_corpus(corpus)
        manifest=json.loads(corpus.with_name('manifest.json').read_text()); validate_corpus(rows,manifest,corpus)
        if digest_file(corpus)!=packet['corpus_sha256']:
            raise ValueError('Reference and primary corpus differ')
        compiled=compile_units(packet,facets['cohorts'][cid])
        if not all(known_support_availability(compiled,[r['id'] for r in rows]).values()):
            raise ValueError('Reference supporting record absent from primary corpus')
        units.extend(compiled); main[cid]=manifest
        packet_hashes[cid]=entry['packet_sha256']
        cell_statuses.update(cell['status'] for case in packet['cases'] for cell in case['cells'])
    if len({u['id'] for u in units})!=len(units):
        raise ValueError('Duplicate scoring identity')
    availability=[]
    for path in sorted(corpus_root.glob('sensitivity/*/*/*/corpus.jsonl')):
        rows=read_corpus(path); manifest=json.loads(path.with_name('manifest.json').read_text()); validate_corpus(rows,manifest,path)
        cid=manifest['study']['cohort_id']; subset_ids={r['id'] for r in rows}
        allowed=set(main[cid]['allowed_parent_asins'])
        if set(manifest['allowed_parent_asins'])!=allowed:
            raise ValueError('Sensitivity families differ from primary')
        if not subset_ids <= set(r['id'] for r in read_corpus(corpus_root/'main'/cid/'corpus.jsonl')):
            raise ValueError('Sensitivity contains records outside main corpus')
        relevant=[u for u in units if u['cohort_id']==cid]
        present=known_support_availability(relevant,subset_ids)
        by_question={}
        for q in rubric['factual_questions']:
            qids=[u['id'] for u in relevant if u['question_id']==q]
            by_question[q]={'reference_units':len(qids),'known_support_retained':sum(present[i] for i in qids),
                            'known_support_unavailable':sum(not present[i] for i in qids)}
        availability.append({'study':manifest['study'],'corpus_sha256':manifest['corpus_sha256'],
                             'per_question':by_question,'available_unit_ids':[i for i,p in present.items() if p],
                             'known_support_retention':sum(present.values())/len(present) if present else None})
    if len(availability)!=27:
        raise ValueError('Expected 27 sensitivity corpora')
    provenance={'rubric_sha256':digest_file(rubric_path),'facets_sha256':digest_file(facets_path),
                'approved_packet_hashes':packet_hashes,'primary_corpus_hashes':{cid:m['corpus_sha256'] for cid,m in main.items()},
                'script_sha256':digest_file(__file__),'scoring_code_sha256':digest_file('src/product_review_insights/scoring.py')}
    template=[]
    for cid in main:
        for i in range(1,15):
            q=f'Q{i:02d}'; role='facts' if q in rubric['factual_questions'] else 'proposal' if q in rubric['proposal_questions'] else 'control'
            template.append({'cohort_id':cid,'question_id':q,'role':role,'annotation_status':'unreviewed_no_answer_generated',
                             'run_annotation_id':None,'reference_unit_ids':[u['id'] for u in units if u['cohort_id']==cid and u['question_id']==q],
                             'retrieval_covered_unit_ids':None,'answer_covered_unit_ids':None,'claim_labels':None,
                             'proposal_criteria':{k:None for k in rubric['proposal_criteria']} if role=='proposal' else None,
                             'control_criteria':{k:None for k in rubric['control_criteria']} if role=='control' else None})
    summary={'status':'rubric_and_units_prepared_for_review_not_final_evaluation_freeze',**provenance,
             'reference_unit_count':len(units),'cell_status_counts':dict(cell_statuses),
             'primary_denominators':{cid:{q:sum(u['cohort_id']==cid and u['question_id']==q for u in units) for q in rubric['factual_questions']} for cid in main},
             'availability_corpora':len(availability),'annotation_case_templates':len(template),
             'sensitivity_question_cases':sum(len(a['per_question']) for a in availability),
             'sensitivity_question_cases_without_known_support':sum(q['known_support_retained']==0 for a in availability for q in a['per_question'].values()),
             'known_support_retention_ranges':{},'rag_quality_metrics_computed':False,
             'limits':['Availability of known anchors only, not exhaustive theme recall or proof of answerability.',
                       'Units and rubric derived from approved interpretations; new scoring decomposition awaits methodological review.',
                       'Actual passage support must be judged separately from supporting review identity.',
                       'P/N/H/C cells excluded from factual coverage targets; hypotheses and controls have separate criteria.']}
    for cid in main:
        summary['known_support_retention_ranges'][cid]={}
        for n in [20,40,60]:
            values=[a['known_support_retention'] for a in availability if a['study']['cohort_id']==cid and a['study']['reviews_per_family']==n]
            summary['known_support_retention_ranges'][cid][str(n)]={'min':min(values),'max':max(values),'seeds':3}
    destination.mkdir(parents=True)
    files={'reference-units.private.json':{'provenance':provenance,'units':units},
           'availability.private.json':availability,'annotation-template.private.json':template,'summary.json':summary}
    for name,value in files.items(): (destination/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    Path('docs/scoring-preparation-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',default='results/scoring-reference/v1'); a=p.parse_args()
    print(json.dumps(prepare(a.output),indent=2))
