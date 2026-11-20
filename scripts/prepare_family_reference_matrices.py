"""Build immutable reference proposals with an explicit question x family matrix."""
import argparse
import collections
import json
from pathlib import Path

from product_review_insights.data import digest_file, read_corpus
from product_review_insights.study import validate_corpus


def validate_cells(cases, families, rows, question_ids):
    if set(cases) != set(question_ids) or len(families) != 5 or len(set(families)) != 5:
        raise ValueError('Require every question and exactly five unique families')
    resolved = {}
    for qid, cells in cases.items():
        if len(cells) != len(families):
            raise ValueError('Missing family cell')
        for pid, cell in zip(families, cells):
            status = cell['status']
            if status not in {'E','P','N','H','C'} or not cell['note_pt'].strip():
                raise ValueError('Invalid cell status or missing interpretation')
            if status in {'E','P','H'} and not cell['evidence_prefixes']:
                raise ValueError('Evidence or hypothesis requires supporting records')
            if (qid in {'Q13','Q14'}) != (status == 'C'):
                raise ValueError('Controls are rubric criteria, not empirical findings')
            evidence = []
            for prefix in cell['evidence_prefixes']:
                matches = [r for r in rows if r['id'].startswith(prefix)]
                if len(matches) != 1:
                    raise ValueError('Evidence prefix must resolve uniquely')
                if matches[0]['product_id'] != pid:
                    raise ValueError('Evidence belongs to a different family')
                evidence.append(matches[0])
            resolved[qid,pid] = evidence
    return resolved


def prepare(plan_path, output):
    output=Path(output)
    if output.exists():
        raise FileExistsError('Use new destination; keep earlier review packets')
    plan=json.loads(Path(plan_path).read_text())
    scope=json.loads(Path('configs/study-scope.json').read_text())
    pointer=json.loads(Path('configs/corpus-current.json').read_text())
    benchmark=json.loads(Path('configs/benchmark-plan.draft.json').read_text())
    questions=json.loads(Path(benchmark['questions']).read_text())
    qids=[q['id'] for q in questions]
    if len(qids)!=14 or len(set(qids))!=14:
        raise ValueError('Unexpected benchmark questions')
    packets=[]
    for number,cohort in enumerate(scope['cohorts'],1):
        cid=cohort['id']; path=Path(pointer['snapshot'])/'main'/cid/'corpus.jsonl'
        rows=read_corpus(path); corpus_manifest=json.loads(path.with_name('manifest.json').read_text())
        validate_corpus(rows,corpus_manifest,path)
        families=[f['parent_asin'] for f in cohort['families']]
        resolved=validate_cells(plan['cohorts'][cid],families,rows,qids)
        packet={'schema':'family_question_reference_matrix_v2','packet':number,'cohort_id':cid,
                'status':'revised_matrix_pending_user_approval','corpus_sha256':digest_file(path),
                'questions_sha256':digest_file(benchmark['questions']),'plan_sha256':digest_file(plan_path),
                'script_sha256':digest_file(__file__),'statuses':plan['statuses'],'limits':plan['limits'],
                'reference_exhaustive':False,'scoring_denominator_frozen':False,
                'earlier_approvals_scope':'Previous interpretations remain approved, not new cells or complete family coverage.',
                'preserved_prior_approved_unit_ids':plan.get('preserved_prior_approved_units',[]) if cid=='compact_mascaras' else [],
                'family_keys':[{'key':f'F{i+1}','product_id':f['parent_asin'],'functional_class':f['functional_label'],
                                'corpus_reviews':sum(r['product_id']==f['parent_asin'] for r in rows)} for i,f in enumerate(cohort['families'])],
                'cases':[]}
        for q in questions:
            cells=[]
            for i,(pid,cell) in enumerate(zip(families,plan['cohorts'][cid][q['id']])):
                cells.append({'family_key':f'F{i+1}','product_id':pid,'status':cell['status'],
                              'note_pt':cell['note_pt'],'evidence':resolved[q['id'],pid],
                              'user_approved_revision':False})
            packet['cases'].append({'question_id':q['id'],'question_pt':q['question_pt'],'cells':cells})
        packets.append(packet)
    output.mkdir(parents=True)
    summary={'status':'three_revised_matrices_pending_user_review','question_family_cells':0,
             'reference_exhaustive':False,'scoring_denominator_frozen':False,'packets':[]}
    for packet in packets:
        cid=packet['cohort_id']; number=packet['packet']; private=output/f'{cid}.private.json'
        private.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n')
        text=f'# Pacote {number} revisado — matriz por família\n\nCada uma das 14 perguntas foi conferida nas cinco famílias. Isso significa varredura de candidatos e inspeção dirigida de evidências por célula, não leitura humana integral de todas as avaliações. A referência é auditada e não exaustiva. As matrizes revisadas aguardam aprovação; interpretações anteriores aprovadas foram preservadas no histórico. Não houve respostas finais de RAG.\n\n'
        text+='## Famílias\n\n| Chave | Família (parent_asin) | Classe funcional | Avaliações |\n|---|---|---|---:|\n'
        for f in packet['family_keys']: text+=f"| {f['key']} | {f['product_id']} | {f['functional_class']} | {f['corpus_reviews']} |\n"
        text+='\n## Como ler\n\n'
        for status,label in packet['statuses'].items(): text+=f'- {status}: {label}\n'
        text+='\nE não significa comprovação técnica; P não conta como problema encontrado; N não prova ausência no corpus; H é uma possibilidade, não a única solução correta. C é critério de controle. Em Q04, autonomia de pilhas não se aplica a cosméticos e ferramentas passivas, mas rendimento, duração do efeito ou vida útil podem se aplicar; não marcamos a pergunta inteira como não aplicável por esse motivo.\n\n'
        for case in packet['cases']:
            text+=f"## {case['question_id']}\n\n{case['question_pt']}\n\n| Família | Situação | Interpretação proposta |\n|---|---|---|\n"
            for cell in case['cells']: text+=f"| {cell['family_key']} | {cell['status']} | {cell['note_pt']} |\n"
            text+='\n'
        text+='## Antes de pontuar\n\nA pergunta abrange o conjunto; uma resposta não precisa mencionar artificialmente todas as famílias, mas não deve omitir achados pertinentes da referência aprovada nem transferir resultados entre elas. Cada evidência privada resolve para uma única avaliação da família correta e para o hash do corpus atual.\n\nAs células são propostas de expectativas, não unidades já congeladas de pontuação. Separar e deduplicar aspectos por família, aceitar evidências válidas adicionais e verificar a disponibilidade em cada subconjunto antes de definir denominadores. Não somar células repetidas como temas independentes. Controles são avaliados separadamente. Propostas de melhoria admitem alternativas fundamentadas.\n'
        doc=Path(f'docs/reference-packet-{number}-revised.md'); doc.write_text(text)
        Path(f'../outputs/pacote-referencias-{number}-revisado.md').write_text(text)
        counts=dict(collections.Counter(cell['status'] for case in packet['cases'] for cell in case['cells']))
        entry={'packet':number,'cohort_id':cid,'family_count':5,'question_count':14,'cells':70,'statuses':counts,
               'status':packet['status'],'private_file':str(private),'packet_sha256':digest_file(private),
               'corpus_sha256':packet['corpus_sha256'],'review_document':str(doc)}
        summary['packets'].append(entry); summary['question_family_cells']+=70
    (output/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    Path('docs/family-reference-matrix-progress.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--plan',default='configs/family-reference-plan.v2.draft.json'); parser.add_argument('--output',default='results/benchmark-consolidated/family-matrices-v2'); args=parser.parse_args()
    print(json.dumps(prepare(args.plan,args.output),indent=2))
