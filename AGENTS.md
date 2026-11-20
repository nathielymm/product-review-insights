# Project workflow

## Git history and academic progress

- Organize commits around coherent, reviewable deliverables: data audit, corpus preparation, retrieval, evaluation infrastructure, benchmark, reference validation, experiments and analysis.
- Do not create a commit for every user acknowledgement, reviewed example, intermediate wording change or chat turn. Persist such decisions locally and consolidate related changes when the deliverable is complete.
- Commit code, meaningful tests, configuration and explanatory documentation together when they form one change. Keep substantive bug fixes separate when that helps review.
- Describe the problem solved and final behavior. Do not use commit count as evidence of project quality or invent milestones, dates, measurements or results.
- Keep a concise milestone narrative in docs/development-history.md; retain material methodological decisions and limitations without transcribing the conversation.
- Preserve existing history. Any future consolidation must retain a local backup and a mapping to original commits; do not silently rewrite history or change dates to suggest a different development timeline.
- Keep the GitHub repository private. Remote changes must stay within the scope authorized by the user.

## Data and evaluation

- Do not version raw reviews, processed corpora, individual evidence/annotations, personal information, credentials or model files. Keep them under ignored local paths and version aggregate manifests/protocols only.
- User approval of reference interpretations does not imply exhaustive corpus annotation, independent assessment, frozen scoring denominators or final RAG results.
- Run checks appropriate to substantive code changes. Documentation-only or approval recording does not require rerunning model experiments.

- Resource evaluation is limited to wall-clock times and Ollama token counts. Do not enumerate system processes, sample RSS or request monitoring permissions unless the user explicitly changes this scope.
