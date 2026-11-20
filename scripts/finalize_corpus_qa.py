"""Reproducible rule-based screening and traceable corpus QA revision.
Run from repository root. This is assistant QA, not independent human annotation.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from product_review_insights.data import digest_file, read_corpus
from product_review_insights.diversity import deterministic_sample, word_count
from product_review_insights.study import materialize_corpus, validate_corpus

RULES = {
    'animal': r'\b(dog|dogs|cat|cats|pet|pets|horse|horses|puppy)\b',
    'contact': r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|https?://|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b',
    'incentive_candidate': r'(received|provided|sent).{0,50}(free|discount|complimentary)|(free|discount|complimentary).{0,50}(review|exchange)',
    'product_mismatch_candidate': r'\b(wrong (item|product)|not (a |the )?(shampoo|mascara|toothbrush|diffuser)|different product)\b',
    'signature_candidate': r'\b(product tester|amz reviewer)\b',
}

def finalize(source, output, report, decisions_path):
    source, output, report = map(Path, (source, output, report))
    decisions = json.loads(Path(decisions_path).read_text())
    if output.exists() or report.exists():
        raise FileExistsError('Use new output/report paths; preserve prior snapshots')
    old = json.loads((source/'preparation-summary.json').read_text())
    full_paths = sorted(source.glob('main/*/corpus.jsonl')) + sorted(source.glob('development/*/corpus.jsonl'))
    manifests, groups, flagged, all_ids = {}, {}, [], set()
    for path in full_paths:
        manifest = json.loads(path.with_name('manifest.json').read_text())
        rows = read_corpus(path)
        validate_corpus(rows, manifest, path)
        cid = manifest['study']['cohort_id']
        manifests[cid] = manifest
        groups[cid] = rows
        for r in rows:
            all_ids.add(r['id'])
            flags = [k for k,pattern in RULES.items() if re.search(pattern, r['text'], re.I)]
            if flags: flagged.append({'cohort':cid,'review_id':r['id'],'flags':flags,'text':r['text']})
    exclusions = decisions['exclude_review_ids']
    redactions = decisions['redact_signature_review_ids']
    if not (set(exclusions)|set(redactions)) <= all_ids:
        raise ValueError('QA decisions refer to absent records')
    summary = {'status':'corpus_qa_revision_prepared_benchmark_pending','primary':[],'sensitivity':[],'development':[]}
    for cid, rows in groups.items():
        parent = manifests[cid]
        changed = []
        for row in rows:
            if row['id'] in exclusions: continue
            row = dict(row)
            if row['id'] in redactions:
                # Remove the entire trailing signature, not a particular person's name.
                text, n = re.subn(r'\s+-[^.\n]*\bAMZ reviewer\s+Product Tester\s*$', ' [REDACTED_SIGNATURE]', row['text'], flags=re.I)
                if n != 1: raise ValueError('Signature pattern changed')
                row.update(text=text, words=word_count(text), qa_redaction=True)
            changed.append(row)
        common = {k:parent[k] for k in ['scope_config_sha256','source_sha256','eligible_pool_sha256','audit_exclusion_sha256','audited_reviews_reserved']}
        common.update(qa_decisions_sha256=digest_file(decisions_path),qa_script_sha256=digest_file(__file__),parent_corpus_sha256=parent['corpus_sha256'],qa_revision='qa_v2',qa_note='Automated screening plus targeted assistant inspection and 20 user-reviewed records; not exhaustive human validation. Review IDs preserve source identity after signature redaction.')
        study = {**parent['study'],'scope_id':parent['study']['scope_id']+'_qa_v2'}
        split = study['split']; section='main' if split=='evaluation' else 'development'
        full=materialize_corpus(changed,output/section/cid,study,common)
        summary['primary' if split=='evaluation' else 'development'].append(full)
        families=sorted({r['product_id'] for r in changed})
        for seed in [11,23,37]:
            for n in [20,40,60]:
                if any(sum(r['product_id']==pid for r in changed)<n for pid in families): raise ValueError('Insufficient family capacity')
                sampled=[r for pid in families for r in deterministic_sample([r for r in changed if r['product_id']==pid],n,seed,pid)]
                kind='sensitivity' if split=='evaluation' else 'development_curve'
                m=materialize_corpus(sampled,output/kind/f'n{n}'/f'seed{seed}'/cid,{**study,'analysis_kind':kind,'reviews_per_family':n,'seed':seed},common)
                summary['sensitivity' if split=='evaluation' else 'development'].append(m)
    for path in output.rglob('manifest.json'):
        manifest = json.loads(path.read_text())
        manifest['qc_status'] = 'targeted_qa_completed_not_exhaustive_human_validation'
        path.write_text(json.dumps(manifest,indent=2)+'\n')
    for section in ['primary','sensitivity','development']:
        for manifest in summary[section]:
            manifest['qc_status'] = 'targeted_qa_completed_not_exhaustive_human_validation'
    summary['primary_reviews']=sum(m['reviews'] for m in summary['primary'])
    summary['qa_decisions_sha256']=digest_file(decisions_path)
    (output/'preparation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    report.mkdir(parents=True)
    (report/'flags.private.json').write_text(json.dumps(flagged,ensure_ascii=False,indent=2)+'\n')
    public={'status':'targeted_corpus_qa_completed_benchmark_pending','screened_primary_reviews':old['primary_reviews'],'screened_development_reviews':sum(m['reviews'] for m in old['development'] if m['study']['analysis_kind']=='development_full'),'flag_counts_primary':{k:sum(k in r['flags'] and r['cohort']!='development_disjoint' for r in flagged) for k in RULES},'excluded_animal_only_reviews':len(exclusions),'signature_redactions':len(redactions),'primary_reviews_after_qa':summary['primary_reviews'],'primary_counts':{m['study']['cohort_id']:m['reviews'] for m in summary['primary']},'qa_decisions_sha256':digest_file(decisions_path),'limits':['Regex screening is not exhaustive privacy, language or product validation.','Incentive candidates include false positives; retained, not evidence of fraud.','Mixed human/animal reviews retained; animal outcomes must not support human benefits.','20 records user-reviewed, covering 15 families; other flagged cases inspected by assistant.','No independent gold annotation or final RAG evaluation.']}
    (report/'summary.json').write_text(json.dumps(public,indent=2)+'\n')
    return public

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--source',default='data/processed/study-v1'); p.add_argument('--output',default='data/processed/study-v2-qa'); p.add_argument('--report',default='results/final-corpus-qa'); p.add_argument('--decisions',default='configs/corpus-qa-decisions.json'); a=p.parse_args()
    print(json.dumps(finalize(a.source,a.output,a.report,a.decisions),indent=2))
