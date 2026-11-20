import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Local traditional vs thematic RAG")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("source")
    prepare.add_argument("--output", default="data/processed/pilot")
    prepare.add_argument("--size", type=int, default=10000)
    prepare.add_argument("--seed", type=int, default=42)
    study = sub.add_parser("prepare-study")
    study.add_argument("--scope", default="configs/study-scope.json")
    study.add_argument("--source", default="data/raw/all_beauty.supplied.parquet")
    study.add_argument("--pools", default="results/diversity-exploration/pools.private.json")
    study.add_argument("--output", default="data/processed/study-v1")
    build = sub.add_parser("build")
    build.add_argument("--corpus", default="data/processed/pilot/corpus.jsonl")
    build.add_argument("--output", default="artifacts/pilot")
    build.add_argument("--config", default="configs/pilot.json")
    query = sub.add_parser("query")
    query.add_argument("question")
    query.add_argument("--index", default="artifacts/pilot")
    query.add_argument("--method", choices=["traditional", "thematic"], default="traditional")
    query.add_argument("--cohort")
    run = sub.add_parser("run")
    run.add_argument("--index", default="artifacts/pilot")
    run.add_argument("--questions", default="configs/questions.dev.json")
    run.add_argument("--output", required=True)
    run.add_argument("--repetitions", type=int, default=3)
    run.add_argument("--cohort")
    blind = sub.add_parser("blind")
    blind.add_argument("runs")
    blind.add_argument("--output", required=True)
    report = sub.add_parser("summarize")
    report.add_argument("runs")
    evaluation = sub.add_parser("evaluate")
    evaluation.add_argument("runs")
    evaluation.add_argument("--annotations", required=True)
    evaluation.add_argument("--key", required=True)
    freeze = sub.add_parser("freeze-evaluation")
    freeze.add_argument("--manifest", default="configs/evaluation-freeze.v1.json")
    freeze.add_argument("--private-root", default="results/evaluation-freeze/v1")
    freeze.add_argument("--index-root", default="artifacts/evaluation-v1")
    frozen_build = sub.add_parser("build-frozen-index")
    frozen_build.add_argument("--freeze", default="configs/evaluation-freeze.v1.json")
    frozen_build.add_argument("--case", required=True)
    frozen_build.add_argument("--output", required=True)
    frozen_run = sub.add_parser("run-frozen")
    frozen_run.add_argument("--freeze", default="configs/evaluation-freeze.v1.json")
    frozen_run.add_argument("--case", required=True)
    frozen_run.add_argument("--index")
    frozen_run.add_argument("--output", required=True)
    study_blind = sub.add_parser("blind-study")
    study_blind.add_argument("runs")
    study_blind.add_argument("--freeze", default="configs/evaluation-freeze.v1.json")
    study_blind.add_argument("--output", required=True)
    study_score = sub.add_parser("score-study")
    study_score.add_argument("runs")
    study_score.add_argument("--freeze", default="configs/evaluation-freeze.v1.json")
    study_score.add_argument("--review", required=True)
    study_score.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command in {"freeze-evaluation","build-frozen-index","run-frozen","blind-study","score-study"}:
        from .frozen_evaluation import freeze_evaluation,build_frozen_index,run_frozen,blind_study,score_study
        if args.command=="freeze-evaluation": result=freeze_evaluation(args.manifest,args.private_root,args.index_root)
        elif args.command=="build-frozen-index": result=build_frozen_index(args.freeze,args.case,args.output)
        elif args.command=="run-frozen": result=run_frozen(args.freeze,args.case,args.output,args.index)
        elif args.command=="blind-study": result=blind_study(args.freeze,args.runs,args.output)
        else:
            if Path(args.output).exists(): raise FileExistsError("Use a new score output file")
            report=score_study(args.freeze,args.runs,args.review)
            Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            result={k:report[k] for k in ['case_id','attempts','reviewed_attempts','quality_results_complete','generation_failures']}
        print(json.dumps(result,indent=2,ensure_ascii=False))
        return
    if args.command == "prepare":
        from .data import prepare
        result = prepare(args.source, args.output, args.size, args.seed)
    elif args.command == "prepare-study":
        from .study import prepare_study
        summary = prepare_study(args.scope, args.source, args.pools, args.output)
        result = {"status": summary["status"], "primary_reviews": summary["primary_reviews"],
                  "primary_cohorts": len(summary["primary"]), "balanced_evaluation_corpora": len(summary["sensitivity"]), "output": args.output}
    elif args.command == "build":
        from .retrieval import build
        result = build(args.corpus, args.output, json.loads(Path(args.config).read_text()))
    elif args.command == "query":
        from .retrieval import Retriever
        from .generation import generate
        retriever = Retriever(args.index)
        from .study import validate_index_scope
        validate_index_scope(retriever.metadata, args.cohort)
        result = generate(args.question, retriever.search(args.question, args.method == "thematic"), retriever.config)
    elif args.command == "run":
        from .experiments import run
        result = run(args.index, args.questions, args.output, args.repetitions, args.cohort)
    elif args.command == "blind":
        from .experiments import blind
        blind(args.runs, args.output)
        result = {"output": args.output}
    elif args.command == "evaluate":
        from .experiments import evaluate
        result = evaluate(args.runs, args.annotations, args.key)
    else:
        from .experiments import summarize
        result = summarize(args.runs)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
