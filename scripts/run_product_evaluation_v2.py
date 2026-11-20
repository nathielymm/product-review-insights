"""Validate a v2 configuration or execute only with a separate authorized freeze."""
import argparse
import json
import os
from product_review_insights.evaluation_v2 import load_configuration, verify_runtime, execute


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true');group.add_argument('--run-frozen',action='store_true')
    parser.add_argument('--runtime',action='store_true');parser.add_argument('--freeze')
    parser.add_argument('--output');parser.add_argument('--token-ledger')
    args=parser.parse_args()
    os.environ['OMP_NUM_THREADS']='1'
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    os.environ['TOKENIZERS_PARALLELISM']='false'
    if args.check:
        config,questions,schedule,units,files=load_configuration(args.config)
        result={'status':'inputs_verified_not_frozen','products':len(config['products']),
                'questions':sum(len(p['questions']) for p in questions['products']),
                'scheduled_English':len(schedule['english_attempts']),'coverage_cases':len(units['cases']),
                'verified_files':len(files),'final_generations':0}
        if args.runtime:result['runtime']=verify_runtime(config)
    else:
        if not all([args.freeze,args.output,args.token_ledger]):parser.error('--run-frozen requires --freeze --output --token-ledger')
        result=execute(args.config,args.freeze,args.output,args.token_ledger)
    print(json.dumps(result))

if __name__=='__main__':main()
