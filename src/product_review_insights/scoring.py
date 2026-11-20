"""Aspect-level audited-reference scoring; missing judgments never imply success."""
import collections
import hashlib
import statistics

FACTUAL_QUESTIONS = {'Q01','Q02','Q03','Q04','Q05','Q06','Q07','Q08','Q11'}
THEME_ALIASES = {'wear_long':'wear','wear_short':'wear','wear_no_chips':'wear','wear_chips':'wear',
                 'perceived_volume':'volume','perceived_length':'length'}


def compile_units(packet, facet_cases):
    """Split approved E cells using explicit facets, not punctuation or model output."""
    if set(facet_cases) != FACTUAL_QUESTIONS:
        raise ValueError('Need explicit facets for all nine factual questions')
    units, keys = [], set()
    for case in packet['cases']:
        qid = case['question_id']
        if qid not in FACTUAL_QUESTIONS:
            continue
        specs = facet_cases[qid]
        if len(specs) != len(case['cells']):
            raise ValueError('Facet plan must represent every family cell')
        for cell, spec in zip(case['cells'], specs):
            if cell['status'] != 'E':
                if spec is not None:
                    raise ValueError('P/N/H/C cells cannot become factual coverage targets')
                continue
            if not spec:
                raise ValueError('An evidence cell needs explicit scoring facets')
            for item in spec.split(';'):
                aspect, rest = item.split('~', 1)
                label, expression = rest.rsplit('@', 1)
                key = packet['cohort_id'], qid, cell['product_id'], aspect
                if key in keys:
                    raise ValueError('Duplicate family/aspect within a question')
                keys.add(key)
                groups = []
                for group in expression.split('&'):
                    indices = [int(i) for i in group.split(',')]
                    if not indices or min(indices) < 0 or max(indices) >= len(cell['evidence']):
                        raise ValueError('Supporting evidence index outside cell')
                    evidence = [cell['evidence'][i] for i in indices]
                    if any(r['product_id'] != cell['product_id'] for r in evidence):
                        raise ValueError('Supporting evidence belongs to another family')
                    groups.append(sorted({r['id'] for r in evidence}))
                uid = hashlib.sha256('\0'.join(key).encode()).hexdigest()[:20]
                units.append({'id':uid,'cohort_id':key[0],'question_id':qid,'product_id':key[2],
                              'family_key':cell['family_key'],'aspect':aspect,
                              'theme_key':THEME_ALIASES.get(aspect,aspect),
                              'expectation_pt':label,'support_groups':groups,
                              'parent_interpretation_pt':cell['note_pt'],
                              'reference_type':'audited_non_exhaustive','source_status':'E'})
    return units


def known_support_availability(units, review_ids):
    """Known anchors retained, NOT proof of all answerability or exhaustive recall."""
    if any(not u['support_groups'] or any(not group for group in u['support_groups']) for u in units):
        raise ValueError('Every unit requires nonempty supporting groups')
    review_ids = set(review_ids)
    return {u['id']: all(bool(set(group) & review_ids) for group in u['support_groups']) for u in units}


def coverage_metrics(units, covered_unit_ids, available_review_ids):
    """One cohort/question, manually judged coverage, eligible known-support units."""
    ids = [u['id'] for u in units]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate reference unit IDs')
    if len({(u['cohort_id'],u['question_id']) for u in units}) > 1:
        raise ValueError('Score one cohort/question at a time')
    reviewed = covered_unit_ids is not None
    covered = set(covered_unit_ids or [])
    if not covered <= set(ids):
        raise ValueError('Unknown covered unit')
    availability = known_support_availability(units, available_review_ids)
    eligible = {uid for uid, present in availability.items() if present}
    if not covered <= eligible:
        raise ValueError('Known support unavailable; adjudicate additional evidence before crediting coverage')
    families = collections.defaultdict(set)
    themes = collections.defaultdict(set)
    for unit in units:
        if unit['id'] in eligible:
            families[unit['product_id']].add(unit['id'])
            themes[unit['theme_key']].add(unit['id'])
    family_scores = {pid:len(group & covered)/len(group) if reviewed else None for pid,group in families.items()}
    return {'eligible_reference_units':len(eligible),'covered_reference_units':len(covered) if reviewed else None,
            'reference_unit_coverage':len(covered)/len(eligible) if eligible and reviewed else None,
            'family_macro_coverage':statistics.mean(family_scores.values()) if family_scores and reviewed else None,
            'per_family_coverage':family_scores,
            'reference_aspect_coverage':sum(bool(group & covered) for group in themes.values())/len(themes) if themes and reviewed else None,
            'eligible_reference_aspects':len(themes),
            'known_support_retention':len(eligible)/len(units) if units else None,
            'note':'Audited reference only. Aspect covered in one family is not coverage of every family. Missing known anchors do not prove corpus absence.'}


def claim_metrics(statuses):
    """Human labels for factual assertions, including correct family attribution."""
    if statuses is None:
        return {key:None for key in ['factual_claims','supported_claims','contradicted_claims','unsupported_claims','pending_claims','faithfulness','contradiction_rate']}
    valid = {'supported','contradicted','unsupported','pending'}
    if any(s not in valid for s in statuses):
        raise ValueError('Unknown factual-claim label')
    counts = collections.Counter(statuses)
    complete = bool(statuses) and not counts['pending']
    return {'factual_claims':len(statuses),'supported_claims':counts['supported'],
            'contradicted_claims':counts['contradicted'],'unsupported_claims':counts['unsupported'],
            'pending_claims':counts['pending'],
            'faithfulness':counts['supported']/len(statuses) if complete else None,
            'contradiction_rate':counts['contradicted']/len(statuses) if complete else None}


def binary_profile(judgments, criteria):
    """Separate criteria; do not invent composite weights or completed annotations."""
    if set(judgments) != set(criteria) or any(v is not None and type(v) is not bool for v in judgments.values()):
        raise ValueError('Need exactly the expected boolean-or-missing judgments')
    return {key:None if value is None else int(value) for key,value in judgments.items()}
