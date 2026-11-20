"""Offline-only operational selection; refuses evaluation corpora and global pilot."""
import argparse
import itertools
import json
import shutil
import time
from pathlib import Path
from product_review_insights.data import digest_file,read_corpus
from product_review_insights.generation import pack_context
from product_review_insights.study import validate_corpus,validate_scoped_chunks


def validate_development_source(index_path, corpus_path, plan):
    index_path,corpus_path=Path(index_path),Path(corpus_path)
    metadata=json.loads((index_path/'metadata.json').read_text())
    manifest=json.loads(corpus_path.with_name('manifest.json').read_text())
    for study in [metadata.get('study',{}),manifest.get('study',{})]:
        if study.get('split')!=plan['allowed_split'] or study.get('cohort_id')!=plan['allowed_cohort']:
            raise ValueError('Only the separate development split/cohort is eligible')
    if metadata['corpus_sha256']!=digest_file(corpus_path):
        raise ValueError('Cached index does not match current development source')
    rows=read_corpus(corpus_path); validate_corpus(rows,manifest,corpus_path)
    for filename,key in [('index.faiss','index_sha256'),('chunks.jsonl','chunks_sha256')]:
        if digest_file(index_path/filename)!=metadata[key]: raise ValueError('Development cache checksum mismatch')
    for name,expected in metadata['encoder_files_sha256'].items():
        if digest_file(index_path/'encoder'/name)!=expected: raise ValueError('Encoder snapshot changed')
    chunks=read_corpus(index_path/'chunks.jsonl'); validate_scoped_chunks(chunks,manifest)
    return metadata,manifest,chunks


def choose_cluster(rows):
    eligible=[r for r in rows if r['nondegenerate_all_seeds']]
    if not eligible: raise ValueError('No nondegenerate clustering candidate')
    return sorted(eligible,key=lambda r:(-r['mean_cosine_silhouette'],-r['mean_adjusted_rand'],r['clusters']))[0]['clusters']



def choose_top_k(feasibility, cap=None):
    possible=[r['top_k'] for r in feasibility if r['all_complete']]
    if not possible: raise ValueError('No top-k candidate fits both methods')
    if cap is not None:
        if type(cap) is not int or cap not in possible:
            raise ValueError('Development-selected cap must fit both methods')
        return cap
    return max(possible)


def prepare(index_path,corpus_path,output,artifact,plan_path):
    output,artifact=Path(output),Path(artifact)
    if output.exists() or artifact.exists(): raise FileExistsError('Use fresh development output and artifact directories')
    plan=json.loads(Path(plan_path).read_text())
    metadata,manifest,chunks=validate_development_source(index_path,corpus_path,plan)
    import faiss
    import numpy as np
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.metrics import silhouette_score,adjusted_rand_score
    from sentence_transformers import SentenceTransformer
    from product_review_insights.retrieval import select_hits
    started=time.perf_counter(); index=faiss.read_index(str(Path(index_path)/'index.faiss'))
    # Reconstruct vectors from the checksum-verified index; do not trust an unchecked .npy cache.
    vectors=index.reconstruct_n(0,index.ntotal)
    if vectors.shape!=(len(chunks),metadata['dimension']): raise ValueError('Development cache shape differs')
    scores=[]; labels={}
    for count in plan['cluster_candidates']:
        runs=[]; silhouettes=[]; sizes=[]
        for seed in plan['clustering_seeds']:
            y=MiniBatchKMeans(n_clusters=count,random_state=seed,n_init=10,batch_size=1024).fit_predict(vectors)
            runs.append(y); sizes.append(np.bincount(y,minlength=count).tolist())
            silhouettes.append(float(silhouette_score(vectors,y,metric='cosine')))
            if seed==plan['selection_seed']: labels[count]=y
        scores.append({'clusters':count,'silhouette_by_seed':dict(zip(map(str,plan['clustering_seeds']),silhouettes)),
                       'mean_cosine_silhouette':float(np.mean(silhouettes)),
                       'mean_adjusted_rand':float(np.mean([adjusted_rand_score(a,b) for a,b in itertools.combinations(runs,2)])),
                       'min_cluster_size':min(min(s) for s in sizes),'max_cluster_size':max(max(s) for s in sizes),
                       'nondegenerate_all_seeds':all(min(s)>=2 for s in sizes)})
    selected=choose_cluster(scores); selected_labels=labels[selected]
    model=SentenceTransformer(str(Path(index_path)/'encoder'),device='cpu',local_files_only=True)
    query_vectors=model.encode([q['question'] for q in plan['queries']],normalize_embeddings=True).astype('float32')
    distances,ranked=index.search(query_vectors,min(plan['candidate_pool'],index.ntotal))
    feasibility=[]; examples=[]
    for k in plan['top_k_candidates']:
        complete=True; lengths=[]; counts=[]
        for qi,q in enumerate(plan['queries']):
            for thematic in [False,True]:
                chosen=select_hits(ranked[qi],selected_labels,k,thematic)
                hits=[{**chunks[i],'cluster':int(selected_labels[i]),'score':float(distances[qi,list(ranked[qi]).index(i)])} for i in chosen]
                context,included=pack_context(hits,plan['context_chars']); complete &= len(included)==k
                lengths.append(len(context)); counts.append(len(included))
                examples.append({'query_id':q['id'],'top_k':k,'method':'thematic' if thematic else 'traditional','evidence':included})
        feasibility.append({'top_k':k,'all_complete':bool(complete),'min_included':min(counts),'max_context_chars':max(lengths)})
    selected_k=choose_top_k(feasibility,plan.get('top_k_cap_after_generation'))
    config={'seed':plan['selection_seed'],'embedding_model':str(Path(index_path)/'encoder'),
            'clusters':selected,'top_k':selected_k,**{k:plan[k] for k in ['candidate_pool','context_chars','num_ctx','num_predict','temperature','ollama_model']},
            'structured_output':plan.get('structured_output',False),
            'configuration_role':'development-selected candidate; generation verification and final evaluation freeze pending'}
    artifact.mkdir(parents=True); output.mkdir(parents=True)
    shutil.copy2(Path(index_path)/'index.faiss',artifact/'index.faiss')
    shutil.copy2(Path(index_path)/'chunks.jsonl',artifact/'chunks.jsonl')
    shutil.copytree(Path(index_path)/'encoder',artifact/'encoder')
    np.save(artifact/'clusters.npy',selected_labels)
    new_metadata={**metadata,'config':config,'study':manifest['study'],'corpus_manifest':manifest,
                  'clusters_sha256':digest_file(artifact/'clusters.npy'),'cluster_counts':np.bincount(selected_labels).tolist(),
                  'development_selection_plan_sha256':digest_file(plan_path),
                  'cache_reuse_note':'Vectors reconstructed from verified development FAISS index; same current development corpus and encoder snapshot.'}
    (artifact/'metadata.json').write_text(json.dumps(new_metadata,indent=2)+'\n')
    (output/'retrieval-probes.private.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2)+'\n')
    report={'status':'offline_development_selection_complete_generation_pending','development_reviews':manifest['reviews'],
            'development_chunks':len(chunks),'corpus_sha256':metadata['corpus_sha256'],'plan_sha256':digest_file(plan_path),
            'script_sha256':digest_file(__file__),'packing_code_sha256':digest_file('src/product_review_insights/generation.py'),'cluster_diagnostics':scores,'packing_feasibility':feasibility,
            'candidate_config':config,'development_artifact':str(artifact),'elapsed_seconds':time.perf_counter()-started,
            'used_evaluation_reference':False,'rag_quality_metrics_computed':False,'generation_calls':0,
            'limitations':['Silhouette and stability are unsupervised diagnostics, not thematic validity or answer quality.','Largest fitting top-k is an operational choice, not a statistically optimal setting.','Candidate pool and generation settings prespecified, not exhaustively tuned.']}
    (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'candidate-config.json').write_text(json.dumps(config,indent=2)+'\n')
    Path('docs/development-selection-summary.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--index',default='artifacts/study-v1/development-check'); p.add_argument('--corpus',default='data/processed/study-v2-qa-final/development/development_disjoint/corpus.jsonl'); p.add_argument('--output',default='results/development-selection/v1'); p.add_argument('--artifact',default='artifacts/development-selection/v1'); p.add_argument('--plan',default='configs/development-selection-plan.json'); a=p.parse_args()
    print(json.dumps(prepare(a.index,a.corpus,a.output,a.artifact,a.plan),indent=2))
