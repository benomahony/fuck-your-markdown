# Evidence behind the matchers

[Agent READMEs: An Empirical Study of Context Files for Agentic Coding](https://arxiv.org/html/2511.12884v1)
(November 2025) examines 2,303 instruction files from 1,925 repositories.
Its content taxonomy has 16 categories; those labels come from manual analysis
of 332 CLAUDE.md files, not every file in the larger collection. Table 3 and the
examples in section 4.3 inform our topic detection.

Our replacement choices are an engineering interpretation of those topics:

| Detected material | Suggested replacement |
| --- | --- |
| Architecture and repository layout | Import-boundary and file-placement tests |
| Implementation conventions | Linters, formatters and ast-grep rules |
| Testing, behaviour and debugging requirements | Acceptance tests |
| Build/run and deployment | Scripts and CI |
| Configuration and environments | Setup validation and configuration schemas |
| Version-control conventions | Hooks and repository checks |
| Security constraints | Scanners and negative security tests |
| Performance budgets | Benchmarks and query-count checks |
| UI/UX requirements | Browser and accessibility tests |
| Documentation requirements | Doc linters and executable examples |

Type and contract checks refine the implementation category. General project
background, agent personas and project-management prose do not automatically
become executable constraints.

[Evaluating AGENTS.md](https://arxiv.org/html/2602.11988v1) studies task outcomes,
not a replacement taxonomy. It reports additional costs and different results
for generated versus human-written context. It does **not** establish that
replacing all documentation with tests improves performance.

[From Agent Behaviour to Agent-Friendly Documentation](https://arxiv.org/html/2608.20195v1)
studies documentation interactions across agent sessions and pull requests.
Its distinction between standing instructions and working notes supports treating
narration separately from enforceable requirements; it does not validate our regexes.

Public examples reviewed as cross-checks:
[AGENTS.md](https://agents.md/),
[Ruff](https://github.com/astral-sh/ruff/blob/main/AGENTS.md),
[Next.js](https://github.com/vercel/next.js/blob/canary/AGENTS.md),
[Pydantic AI](https://github.com/pydantic/pydantic-ai/blob/main/AGENTS.md), and
[Temporal Java SDK](https://github.com/temporalio/sdk-java/blob/master/AGENTS.md).
Tests use short adapted examples rather than copies of these files.

Heading matches identify a topic to review, not a discovered concrete constraint.
A heading is referenced only when its section has no more specific matched lines.
Matchers are local heuristics: the papers' model-classification scores do not
measure their accuracy. Tests cover positive cases and incidental mentions,
comments, unrelated prose and code blocks as negative cases.

## Skill bundles

[From Anatomy to Smells: An Empirical Study of SKILL.md in Agent Skills](https://arxiv.org/html/2607.01456v1)
examines 238 skills; its body taxonomy covers 224 files with H2 sections. It
distinguishes 13 broad components and 44 detailed ones, including procedural
steps, prerequisites, commands, output formats and validation. This informs
workflow-to-script, output-to-contract and checklist-to-test suggestions.
Frontmatter and routing descriptions identify a skill; they are not code
requirements. We ignore that metadata and do not automatically convert routing
instructions or references into tests. These mappings are our interpretation,
not conclusions that all skills should be removed.
