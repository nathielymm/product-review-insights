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
    build = sub.add_parser("build")
    build.add_argument("--corpus", default="data/processed/pilot/corpus.jsonl")
    build.add_argument("--output", default="artifacts/pilot")
    build.add_argument("--config", default="configs/pilot.json")
    query = sub.add_parser("query")
    query.add_argument("question")
    query.add_argument("--index", default="artifacts/pilot")
    query.add_argument("--method", choices=["traditional", "thematic"], default="traditional")
    run = sub.add_parser("run")
    run.add_argument("--index", default="artifacts/pilot")
    run.add_argument("--questions", default="configs/questions.dev.json")
    run.add_argument("--output", required=True)
    run.add_argument("--repetitions", type=int, default=3)
    blind = sub.add_parser("blind")
    blind.add_argument("runs")
    blind.add_argument("--output", required=True)
    report = sub.add_parser("summarize")
    report.add_argument("runs")
    evaluation = sub.add_parser("evaluate")
    evaluation.add_argument("runs")
    evaluation.add_argument("--annotations", required=True)
    evaluation.add_argument("--key", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        from .data import prepare
        result = prepare(args.source, args.output, args.size, args.seed)
    elif args.command == "build":
        from .retrieval import build
        result = build(args.corpus, args.output, json.loads(Path(args.config).read_text()))
    elif args.command == "query":
        from .retrieval import Retriever
        from .generation import generate
        retriever = Retriever(args.index)
        result = generate(args.question, retriever.search(args.question, args.method == "thematic"), retriever.config)
    elif args.command == "run":
        from .experiments import run
        result = run(args.index, args.questions, args.output, args.repetitions)
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
