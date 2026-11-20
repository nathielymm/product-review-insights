"""Materialize proposed, non-exhaustive reference packets; never generate RAG answers."""
import argparse
import json
from pathlib import Path
from product_review_insights.data import digest_file, read_corpus
from product_review_insights.study import validate_corpus


def resolve_prefix(rows, prefix):
    matches = [r for r in rows if r['id'].startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f'Evidence prefix must resolve uniquely: {prefix}')
    return matches[0]


def prepare(plan_path, output):
    output = Path(output)
    if output.exists():
        raise FileExistsError('Use a new packet destination; preserve review history')
    plan = json.loads(Path(plan_path).read_text())
    pointer = json.loads(Path('configs/corpus-current.json').read_text())
    questions_path = Path('configs/benchmark-plan.draft.json')
    benchmark = json.loads(questions_path.read_text())
    questions = json.loads(Path(benchmark['questions']).read_text())
    if {q['id'] for q in questions} != {f'Q{i:02d}' for i in range(1,15)}:
        raise ValueError('Unexpected question schema')
    previous = json.loads(Path('results/benchmark-reference-14-draft/reference.private.json').read_text())
    prior = next(r for r in previous if r['question_id']=='Q01' and r['cohort_id']=='compact_mascaras')
    approved = [r for r in prior['reference_units'] if r['status']=='user_approved']
    if len(approved) != 10:
        raise ValueError('Expected ten previously approved units')
    packets = []
    for cid, cases in plan['cohorts'].items():
        path = Path(pointer['snapshot'])/'main'/cid/'corpus.jsonl'
        rows = read_corpus(path)
        manifest = json.loads(path.with_name('manifest.json').read_text())
        validate_corpus(rows,manifest,path)
        if set(cases) != {f'Q{i:02d}' for i in range(1,13)}:
            raise ValueError('Missing analysis question')
        packet = {'schema':'consolidated_reference_draft_v1','cohort_id':cid,
                  'status':'assistant_draft_pending_user_packet_review',
                  'corpus_sha256':digest_file(path),'questions_sha256':digest_file(benchmark['questions']),
                  'plan_sha256':digest_file(plan_path),'script_sha256':digest_file(__file__),
                  'reference_is_exhaustive':False,'scoring_denominator_frozen':False,
                  'independent_human_annotation':False,'cases':[],
                  'prior_approved_units':approved if cid=='compact_mascaras' else []}
        for q in questions:
            case = {'question_id':q['id'],'question_pt':q['question_pt'],'role':q['evaluation_role'],
                    'status':'proposed_pending_user_review','expectations':[]}
            if q['id'] in cases:
                for index,(description,prefixes,kind) in enumerate(cases[q['id']],1):
                    evidence=[resolve_prefix(rows,prefix) for prefix in prefixes]
                    case['expectations'].append({'id':f'{cid}-{q["id"]}-{index}',
                        'description_pt':description,'kind':kind,'evidence':evidence,
                        'not_a_frozen_scoring_unit':True})
            else:
                case['expectations'].append({'description_pt':plan['control_expected'][q['id']],
                                             'kind':'epistemic_limit_control','evidence':[],
                                             'note':'Rubric criterion; not an observed product fact or verified corpus-absent factual question.'})
            packet['cases'].append(case)
        packets.append(packet)
    output.mkdir(parents=True)
    ledger=[]
    names={'compact_mascaras':'Máscaras para cílios','intermediate_hair_disjoint':'Rotina capilar','varied_disjoint':'Funções variadas de cuidado pessoal'}
    for number,packet in enumerate(packets,1):
        cid=packet['cohort_id']; path=output/f'{cid}.private.json'
        path.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
        text=f'# Pacote {number} — {names[cid]}\n\nReferência proposta para revisão, baseada em evidências auditadas não exaustivas. Nenhuma resposta de RAG foi usada para definir estes pontos. A aprovação do pacote não representa leitura humana integral do corpus. As descrições abaixo são paráfrases; evidências completas e IDs ficam no pacote privado local.\n\n'
        for case in packet['cases']:
            text+=f'## {case["question_id"]}\n\n{case["question_pt"]}\n\n'
            for expectation in case['expectations']:
                text+=expectation['description_pt']+'\n\n'
                families=sorted({r['product_id'] for r in expectation['evidence']})
                if families: text+='Famílias de apoio: '+', '.join(families)+'.\n\n'
        text+='## Limites da revisão\n\nA referência é parcial e pode admitir outras evidências válidas. Não usar ausência na referência como prova de ausência no corpus. Não exigir uma solução única nas propostas. Ainda é necessário separar/deduplicar aspectos por família, verificar cobertura em cada subconjunto e congelar denominadores antes de medir cobertura. Controles são reportados separadamente. Os dez itens R001–R010 previamente aprovados foram preservados no pacote de máscaras; os novos pontos aguardam aprovação. Não foram geradas respostas finais dos métodos.\n'
        public=Path(f'docs/reference-packet-{number}.md'); public.write_text(text)
        Path(f'../outputs/pacote-referencias-{number}.md').write_text(text)
        ledger.append({'packet':number,'cohort_id':cid,'question_cases':len(packet['cases']),
                       'unique_evidence_reviews':len({r['id'] for c in packet['cases'] for e in c['expectations'] for r in e['evidence']}),
                       'packet_sha256':digest_file(path),'corpus_sha256':packet['corpus_sha256'],
                       'previous_user_approved_units':len(packet['prior_approved_units']),
                       'status':packet['status'],'private_file':str(path),'review_document':str(public)})
    summary={'status':'three_draft_packets_prepared_pending_user_review','packets':ledger,
             'case_count':sum(x['question_cases'] for x in ledger),'reference_exhaustive':False,
             'gold_reference_frozen':False,'final_rag_runs':0,
             'selection_limitation':'Keyword candidate discovery and targeted assistant inspection; not exhaustive annotation. Family-aspect deduplication and sensitivity evidence availability pending.'}
    (output/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    Path('docs/consolidated-reference-progress.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--plan',default='configs/consolidated-reference-plan.draft.json'); parser.add_argument('--output',default='results/benchmark-consolidated/packets-v1'); args=parser.parse_args()
    print(json.dumps(prepare(args.plan,args.output),indent=2))
