# CapTraceBench Runtime

CapTraceBench is the benchmark used by RedAct to evaluate procedural skill
leakage from public agent traces. It is built on top of the task format and
BenchFlow-style evaluation runtime from
[benchflow-ai/skillsbench](https://github.com/benchflow-ai/skillsbench), with a
curated CapTraceBench task set and metadata for RedAct's trace protection
experiments.

We preserve compatibility with the SkillsBench execution protocol so tasks can
be checked and evaluated through the same `bench` commands, while the benchmark
focuses specifically on capability-trace leakage and protected trace release.

## Quick Start

From this directory:

```bash
uv sync
uv run bench tasks check tasks/<task-id>
uv run bench eval create -t tasks/<task-id> -a oracle
```

Running non-oracle agents requires the corresponding API keys, such as
`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or provider-specific equivalents.

## Layout

```text
tasks/<task-id>/instruction.md
tasks/<task-id>/environment/
tasks/<task-id>/tests/
```

The RedAct repository also provides a released task copy under `data/tasks/`
for RedAct scripts and experiment entry points.

## Notes

- Keep this runtime in a separate environment from the RedAct core package.
- Use `uv.lock` for reproducible benchmark runtime setup.
- Do not commit local `.envrc` or `.env` files containing credentials.

## License

This runtime is adapted from the SkillsBench/BenchFlow task execution stack.
See [LICENSE](LICENSE) for the bundled runtime license.
