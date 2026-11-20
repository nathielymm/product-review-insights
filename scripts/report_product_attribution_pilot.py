"""Aggregate fifth-round attribution/length diagnostics without semantic scoring."""
import argparse
from collections import Counter
import json
from pathlib import Path
from report_product_source_pilot import report as source_report


def report(spec_path):
    spec=json.loads(Path(spec_path).read_text());data=source_report(spec_path)
    data['schema']='product_attribution_pilot_v5_aggregates';data['baseline_round']=4;data['current_round']=5
    data['interpretation']='Same source-isolated retrieval and 32 calls/shared output caps as round 4. Character bounds and prompt/schema attribution changed. Declared attribution labels and valid JSON are not semantic proof. Unblinded assistant review only; no winner or independent quality score.'
    current=[json.loads(l) for l in (Path(spec['results'])/'runs.private.jsonl').read_text().splitlines()]
    previous=[json.loads(l) for l in (Path(spec['baseline_results'])/'runs.private.jsonl').read_text().splitlines()]
    old={(r['question_id'],r['method']):r for r in previous};now={(r['question_id'],r['method']):r for r in current}
    for item in data['outcomes']:
        key=(item['question_id'],item['method']);row=now[key];before=old[key]
        item['context_matches_round_4']=item.pop('context_matches_round_3')
        item['previous_source_calls']=before['actual_source_calls']
        item['declared_attribution_labels_not_validated']=dict(Counter(f['referente'] for f in row['structured']['achados']))
        item['current_reports_at_char_cap']=sum(len(f['relato'])==spec['generation']['max_report_chars'] for f in row['structured']['achados'])
        item['previous_reports_at_160_chars']=sum(len(f['relato'])==160 for f in before['structured']['achados'])
        item['max_current_report_length']=max((len(f['relato']) for f in row['structured']['achados']),default=0)
    return data


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',default='configs/curly-product-pilot.v5-attribution.json');p.add_argument('--output',required=True);a=p.parse_args()
    output=Path(a.output)
    if output.exists():raise FileExistsError('Preserve existing aggregate')
    data=report(a.spec);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
