"""Prepare blinded manual annotations or export completed v2 metrics; never label semantically by ID."""
import argparse
import json
from pathlib import Path
from product_review_insights.data import digest_file
from product_review_insights.evaluation_v2 import load_configuration, write_json, attempt_id
from product_review_insights.scoring_v2 import annotation_templates, export_metrics, resource_summary, stability_summary, technical_resource_summary


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--config',required=True)
    parser.add_argument('--runs',required=True);parser.add_argument('--output',required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare-annotations',action='store_true');group.add_argument('--export',action='store_true')
    parser.add_argument('--annotations');parser.add_argument('--blind-key');parser.add_argument('--public-output')
    args=parser.parse_args();output=Path(args.output)
    if output.exists():raise FileExistsError('Preserve existing annotations/metrics')
    if not output.resolve().is_relative_to(Path('results').resolve()):raise ValueError('Individual artifacts must stay under ignored results/')
    config,_,schedule,units,_=load_configuration(args.config);root=Path(args.runs)
    status=json.loads((root/'status.private.json').read_text());provenance=json.loads((root/'provenance.private.json').read_text())
    if status.get('status')!='complete' or provenance['configuration_sha256']!=digest_file(args.config):raise ValueError('Run incomplete or configuration differs')
    if status.get('runs_sha256')!=digest_file(root/'runs.private.jsonl') or status.get('translations_sha256')!=digest_file(root/'translations.private.jsonl'):
        raise ValueError('Completed output changed after execution')
    probes_path=root/'technical-probes.private.jsonl'
    if status.get('technical_probes_sha256')!=(digest_file(probes_path) if probes_path.exists() else None):
        raise ValueError('Technical cost log changed after execution')
    rows=[json.loads(l) for l in (root/'runs.private.jsonl').read_text().splitlines()]
    if len(rows)!=60 or [r['attempt_id'] for r in rows]!=[attempt_id(r) for r in schedule['english_attempts']]:raise ValueError('Full scheduled run required')
    binding={'runs_sha256':digest_file(root/'runs.private.jsonl'),'units_sha256':config['scoring']['units_sha256']}
    if args.prepare_annotations:
        templates,key,worksheets=annotation_templates(rows,units)
        output.mkdir(parents=True)
        write_json(output/'annotations.private.json',{**binding,'annotations':templates})
        write_json(output/'blinding-key.private.json',{**binding,'key':key})
        write_json(output/'worksheets.private.json',{'method_labels_hidden':True,'worksheets':worksheets})
        print(json.dumps({'pending_annotations':len(templates),'semantic_labels_generated':0}))
    else:
        if not args.annotations or not args.blind_key:parser.error('--export requires --annotations and --blind-key')
        ann=json.loads(Path(args.annotations).read_text());key=json.loads(Path(args.blind_key).read_text())
        if any(a.get(k)!=v for a in [ann,key] for k,v in binding.items()):raise ValueError('Annotation source binding differs')
        public,cases=export_metrics(rows,ann['annotations'],key['key'],units)
        translations=[json.loads(l) for l in (root/'translations.private.jsonl').read_text().splitlines()]
        if len(translations)!=36 or {t['attempt_id'] for t in translations}!={r['attempt_id'] for r in rows if r['phase']=='primary'}:raise ValueError('Translation accounting incomplete')
        public['resources']=resource_summary(rows,translations)
        public['preparation']=[{'product_id':p['product_id'],'reviews':p['expected_reviews'],'chunks':p['chunks'],
            'index_build_seconds':json.loads((Path(p['index'])/'metadata.json').read_text()).get('build_seconds')} for p in config['products']]
        public['stability']=stability_summary(rows)
        probe_file=root/'technical-probes.private.jsonl'
        probes=[json.loads(l) for l in probe_file.read_text().splitlines()] if probe_file.exists() else []
        public['technical_budget_resources']=technical_resource_summary(probes)
        public['provenance']={**binding,'configuration_sha256':digest_file(args.config),'annotations_sha256':digest_file(args.annotations),'role':'v2_metrics_from_completed_judgments'}
        if args.public_output and Path(args.public_output).exists():raise FileExistsError('Preserve previous public export')
        output.mkdir(parents=True);write_json(output/'case-metrics.private.json',cases);write_json(output/'aggregates.json',public)
        if args.public_output:write_json(args.public_output,public)
        print(json.dumps({'primary_cases':len(cases),'public_export_contains_source_text':False}))

if __name__=='__main__':main()
