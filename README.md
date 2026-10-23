# fuck-your-markdown

**Fuck your markdown. `fym` for short.**

Ship checks that actually fucking run.

Your coding agent fixed a typo and left you `IMPLEMENTATION_PLAN.md`,
`PHASE_2_SUMMARY.md` and `REFACTOR_COMPLETE.md`. Congratulations. The repo has
more paperwork than working software.

`fym` is a small CLI that calls this shit out. It flags stray Markdown and agent
instruction files, reads what they say, and suggests where enforceable rules
belong: tests, linters, type checks, scripts and CI.

“Please respect the architecture” is a wish. An architecture test is a boundary.
“Keep it fast” measures fuck all. Write a benchmark.

No API keys. No model calls. No files changed. Just a failing exit code and some
strongly worded advice.

![fym terminal output suggesting architecture tests, acceptance tests, and scripts or CI for rules found in claude.md](https://raw.githubusercontent.com/benomahony/fuck-your-markdown/main/docs/fym-terminal-output.png)

## What gets bollocked

Two filename rules identify offences; their contents determine suggested replacements.

1. Markdown outside `docs/` fails.
2. Markdown named like agent slop fails wherever it lives, including inside `docs/`. `SPEC.md`, `IMPLEMENTATION_PLAN.md`, `phase-2-summary.md`, `REFACTOR_COMPLETE.md`, `CLAUDE.md`, `AGENTS.md`, `SKILL.md` and friends, at any depth.

`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` and `LICENSE.md` are spared.

Recursive scans skip hidden files, hidden directories and `node_modules/` at any
depth. Those dependencies have enough fucking problems. Explicit file or directory
arguments can still be checked directly.

Skill bundles are an exception to hidden-directory exclusion: `skills/` under
`.agents`, `.claude`, `.codex`, `.cursor`, `.github`, `.gemini`, `.opencode`,
`.windsurf`, `.roo` and `.kilocode` is scanned, including reference Markdown.
Other directories under those namespaces remain excluded. YAML frontmatter is
ignored when suggesting replacements; body line numbers are preserved.

## Install

Requires **Python 3.13+**.

Run it without adding a project dependency:

```bash
uvx --from fuck-your-markdown fym
```

Or install it as a tool:

```bash
uv tool install fuck-your-markdown
# pip works too
pip install fuck-your-markdown
```

For a project development dependency:

```bash
uv add --dev fuck-your-markdown
uv run fym
```

## Usage

```bash
fym
fym src tests
fym --docs documentation
fym --allow README.md --allow CONTRIBUTING.md
fym --agent
```

Exit code is 1 on any offence, 0 otherwise. Passing `--allow` replaces the spared list rather than adding to it. Slop names are checked before the allow list, so you cannot whitelist a plan.

Diagnostics go to stderr. A clean run says nothing. A dirty one has words.

```text
Architecture tests
  Put the boundaries in architecture tests. The diagram isn't going to enforce itself, is it?
  CLAUDE.md:3,12
Linters / ast-grep
  Put it in a linter or ast-grep rule. Stop asking nicely and make the bloody thing fail.
  CLAUDE.md:5
```

Both modes group by replacement type. Terminals get bold headings, bright feedback,
cyan paths and yellow line references. Redirected output is plain; `NO_COLOR` is respected.

## Agent mode

`fym` reads flagged files in both modes. `--agent` swaps the swearing for neutral,
actionable guidance, with the same replacement groups and file and line references.
Apparently the robots need a fucking HR department. Repeated matches in a file share one entry.
It recognises architecture, style, typing, contracts, security, performance,
accessibility, environment setup, documentation requirements and commit conventions.
Commands can be fenced, inline or plain text. Topic-only headings are referenced
when no specific requirement is found underneath; filenames alone do not trigger
recommendations. `--agent` keeps the same groups with neutral guidance.

```text
Architecture tests
  Enforce the cited import boundaries and file placement with architecture tests.
  CLAUDE.md:3,12
  design.md:7
Linters / ast-grep
  Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.
  CLAUDE.md:5
Reuse existing checks. Verify they catch violations before removing the cited prose.
```

Matching is local and heuristic, with no model calls. Unrecognised content gets an
explicit review message instead of invented requirements. Unreadable files are
reported without stopping the remaining analysis. The command does not edit files.
Implement and verify the suggested checks before removing the corresponding prose;
preserve useful human context in the configured docs directory.

The matchers draw on an empirical instruction-file taxonomy and public examples;
see [research notes](docs/matcher-research.md) for sources and limitations.

Paths, `--docs`, `--allow` and exit codes work as usual. Clean runs remain silent.

## Make it fail in CI

```bash
uvx --from fuck-your-markdown==0.1.0 fym
```

For [pre-commit](https://pre-commit.com/), use a local hook. Scan the whole repo so
files hidden in a quiet corner still get their bollocking:

```yaml
repos:
  - repo: local
    hooks:
      - id: fym
        name: Fuck your markdown
        entry: fym
        language: python
        additional_dependencies: [fuck-your-markdown==0.1.0]
        pass_filenames: false
        always_run: true
```

## Keep the useful shit

This is deliberately opinionated. A filename is a policy trigger, not proof that
the document is worthless. The content matcher is heuristic; read the suggestions
before acting on them.

Keep explanations humans need in `docs/`. Turn enforceable requirements into
checks. Verify those checks catch a real violation. Then delete the redundant
fucking prose.

## Development

```bash
uv sync
uv run --with pytest pytest
uv build --no-sources
```

Source and issues: [github.com/benomahony/fuck-your-markdown](https://github.com/benomahony/fuck-your-markdown).
