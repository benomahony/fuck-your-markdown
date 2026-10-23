"""Acceptance tests invoking the installed CLI in temporary repositories."""

from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import unittest


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name)

    def check(self, files, arguments=(), expected=(), environment=None):
        for name in files:
            path = self.repo / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(files[name] if isinstance(files, dict) else "Example content\n")
        result = subprocess.run(
            [str(Path(sys.executable).parent / "fym"), *arguments],
            cwd=self.repo, capture_output=True, text=True, timeout=10, env=environment,
        )
        self.assertEqual(result.returncode, int(bool(expected)), result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(re.sub(r"\x1b\[[0-9;]*m", "", result.stderr).splitlines(), list(expected))
        for name in files:
            self.assertEqual((self.repo / name).read_text(),
                             files[name] if isinstance(files, dict) else "Example content\n")
        return result.stderr

    def test_empty_repository(self):
        self.check([])

    def test_agent_mode_reports_only_discovered_requirements(self):
        self.check({"CLAUDE.md": "# Rules\nDomain must not import API.\nUse structured logging, never print.\n"},
            arguments=["--agent"], expected=[
                "Architecture tests",
                "  Enforce the cited import boundaries and file placement with architecture tests.",
                "  CLAUDE.md:2",
                "Linters / ast-grep",
                "  Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.",
                "  CLAUDE.md:3",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_groups_replacement_types_across_files(self):
        """Each replacement has one heading, with repeated file matches combined."""
        self.check({
            "CLAUDE.md": "Domain must not import API.\nUse structured logging.\nDomain must only depend on core.\n",
            "design.md": "Services must not import routes.\nUse snake_case naming.\n",
        }, arguments=["--agent"], expected=[
            "Architecture tests",
            "  Enforce the cited import boundaries and file placement with architecture tests.",
            "  CLAUDE.md:1,3",
            "  design.md:1",
            "Linters / ast-grep",
            "  Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.",
            "  CLAUDE.md:2",
            "  design.md:2",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
        ])

    def test_agent_mode_does_not_infer_requirements_from_filename(self):
        self.check({"ARCHITECTURE.md": "# Project history\nA history of the project.\n"},
            arguments=["--agent"], expected=[
                "Review / move to docs/",
                "  No enforceable rules recognised; review before moving or deleting.",
                "  ARCHITECTURE.md",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_omits_long_source_excerpts(self):
        requirement = "Domain must not import API. " + "Extra context. " * 40
        self.check({"rules.md": requirement}, arguments=["--agent"], expected=[
            f"Architecture tests",
            "  Enforce the cited import boundaries and file placement with architecture tests.",
                "  rules.md:1",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
        ])

    def test_agent_mode_recognises_folder_layout_and_style_blocks(self):
        self.check({"guide.md": "# Layout\n```text\nsrc/\n└── domain/\n```\n# Style examples\n```python\nlogger.info(message)\n```\n"},
            arguments=["--agent"], expected=[
                "Architecture tests",
                "  Enforce the cited import boundaries and file placement with architecture tests.",
                "  guide.md:2",
                "Linters / ast-grep",
                "  Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.",
                "  guide.md:7",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_ignores_incidental_mentions_and_regular_code(self):
        self.check({"guide.md": "# History\nWe discussed architecture and logging.\n```python\nprint('must import API')\n```\n"},
            arguments=["--agent"], expected=[
                "Review / move to docs/",
                "  No enforceable rules recognised; review before moving or deleting.",
                "  guide.md",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_discovers_contracts_and_behaviour(self):
        self.check({"rules.md": "IDs must be valid UUIDs.\nInvalid requests must return 400.\n"},
            arguments=["--agent"], expected=[
                "Contract tests",
                "  Test the cited schemas with valid and invalid inputs.",
                "  rules.md:1",
                "Acceptance tests",
                "  Test the cited behaviour through public interfaces; assert observable outcomes.",
                "  rules.md:2",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_discovers_diagrams_and_commands(self):
        self.check({"rules.md": "```mermaid\ngraph TD\nAPI --> Domain\n```\n```bash\npytest\n```\n"},
            arguments=["--agent"], expected=[
                "Architecture tests",
                "  Enforce the cited import boundaries and file placement with architecture tests.",
                "  rules.md:1",
                "Scripts + CI",
                "  Move the cited commands into scripts run by CI; propagate failures.",
                "  rules.md:5",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_finds_unfenced_command_in_claude_file(self):
        self.check({"claude.md": "# Architecture\n\n1kljmasldk\n\n# Run the tests\n\nuv run pytest\n"},
            arguments=["--agent", "claude.md"], expected=[
                "Architecture tests",
                "  Enforce the cited import boundaries and file placement with architecture tests.",
                "  claude.md:1",
                "Scripts + CI",
                "  Move the cited commands into scripts run by CI; propagate failures.",
                "  claude.md:7",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_is_silent_when_clean(self):
        self.check(["docs/guide.md", "README.md"], arguments=["--agent"])

    def test_hidden_skill_bundles_are_scanned_without_agent_caches(self):
        self.check({
            ".agents/skills/check/SKILL.md": "No wildcard imports.\n",
            ".claude/skills/check/references/rules.md": "Use snake_case naming.\n",
            "package/.cursor/skills/check/SKILL.md": "Use structured logging.\n",
            ".claude/cache/guide.md": "Never log secrets.\n",
            "node_modules/lib/.agents/skills/check/SKILL.md": "Never log secrets.\n",
        }, arguments=["--agent"], expected=[
            "Linters / ast-grep",
            "  Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.",
            "  .agents/skills/check/SKILL.md:1",
            "  .claude/skills/check/references/rules.md:1",
            "  package/.cursor/skills/check/SKILL.md:1",
            "Reuse existing checks. Verify they catch violations before removing the cited prose.",
        ])

    def test_skill_files_fail_even_in_docs_and_when_allowed(self):
        self.check({"docs/skills/build/SKILL.md": "# Workflow\nGenerate the report.\n"},
            arguments=["--agent", "--allow", "SKILL.md"], expected=[
                "Scripts + CI",
                "  Move the cited commands into scripts run by CI; propagate failures.",
                "  docs/skills/build/SKILL.md:1",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_skill_frontmatter_is_ignored_and_body_lines_are_preserved(self):
        self.check({"skills/check/SKILL.md": "---\nname: check\ndescription: Use strict mode when editing code.\n---\n\nNo wildcard imports.\n"},
            arguments=["--agent"], expected=[
                "Linters / ast-grep",
                "  Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.",
                "  skills/check/SKILL.md:6",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
            ])

    def test_agent_mode_respects_paths_allow_list_and_custom_docs(self):
        self.check([
            "outside.md", "src/keep.md", "src/guide.md", "manual/guide.md",
        ], arguments=["src", "manual", "--agent", "--docs", "manual",
                      "--allow", "keep.md"], expected=[
            "Review / move to manual/",
            "  No enforceable rules recognised; review before moving or deleting.",
                "  src/guide.md",
                "Reuse existing checks. Verify they catch violations before removing the cited prose.",
        ])

    def check_review(self, files, offending, arguments=(), docs="docs"):
        self.check(files, arguments=arguments, expected=[
            f"Review / move to {docs}/",
            "  No rules found. Review it, then move useful docs or bin the fucking thing.",
            *(f"  {name}" for name in offending),
            "Make the checks catch violations. Then delete the fucking prose.",
        ])

    def test_documentation_and_non_markdown_pass(self):
        self.check(["docs/guide.md", "docs/api/reference.mdx", "docs/tutorial.markdown",
                    "src/main.py", "notes.txt"])

    def test_supported_extensions_outside_docs_fail(self):
        files = sorted(f"src/guide-{index}.{ext}"
                       for index, ext in enumerate(("MD", "markdown", "md", "mdx")))
        self.check_review(files, files)

    def test_default_exemptions(self):
        self.check(["README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE.md"])

    def test_slop_fails_inside_docs_even_when_allowed(self):
        files = sorted(f"docs/nested/{name}" for name in (
            "SPEC.md", "IMPLEMENTATION_PLAN.md", "phase-2-summary.md",
            "REFACTOR_COMPLETE.md", "CLAUDE.md", "AGENTS.md",
        ))
        self.check_review(files, files, arguments=["--allow", "*.md"])

    def test_custom_docs_directory(self):
        self.check_review(["documentation/guide.md", "docs/guide.md"], ["docs/guide.md"],
                          arguments=["--docs", "documentation"], docs="documentation")

    def test_repeated_allow_patterns_replace_defaults(self):
        self.check_review(["README.md", "src/guide.md", "examples/tutorial.mdx"], ["README.md"],
                          arguments=["--allow", "src/*.md", "--allow", "examples/*.mdx"])

    def test_explicit_files_and_directories_limit_scope(self):
        self.check_review(["outside.md", "src/guide.md", "tests/example.md"],
                          ["src/guide.md", "tests/example.md"], arguments=["src", "tests/example.md"])

    def test_hidden_paths_are_ignored_during_scan(self):
        self.check([".hidden.md", ".git/guide.md", "src/.cache/guide.md"])

    def test_nested_node_modules_are_ignored_but_project_files_are_checked(self):
        self.check_review([
            "CLAUDE.md", "frontend/guide.md", "node_modules/package/SPEC.md",
            "frontend/node_modules/@scope/package/readme.md",
            "frontend/node_modules/package/node_modules/other/AGENTS.md",
        ], ["CLAUDE.md", "frontend/guide.md"])

    def test_external_directory_scan_skips_dependencies(self):
        target = self.repo / "project"
        self.check_review(["project/frontend/node_modules/package/CLAUDE.md", "project/MEMORY.md"],
                          [f"{target}/MEMORY.md"], arguments=[str(target)])

    def test_explicit_dependency_file_can_still_be_checked(self):
        name = "node_modules/package/guide.md"
        self.check_review([name], [name], arguments=[name])

    def test_overlapping_inputs_are_deduplicated_and_sorted(self):
        self.check_review(["z.md", "a.md", "src/guide.md"], ["a.md", "src/guide.md", "z.md"],
                          arguments=[".", "src", "z.md"])

    def test_normal_mode_uses_same_replacement_groups_with_sweary_guidance(self):
        self.check({"CLAUDE.md": "Domain must not import API.\nUse structured logging.\n"}, expected=[
            "Architecture tests",
            "  Put the boundaries in architecture tests. The diagram isn't going to enforce itself, is it?",
            "  CLAUDE.md:1",
            "Linters / ast-grep",
            "  Put it in a linter or ast-grep rule. Stop asking nicely and make the bloody thing fail.",
            "  CLAUDE.md:2",
            "Make the checks catch violations. Then delete the fucking prose.",
        ])

    def test_terminal_feedback_is_bright_and_redirected_output_is_plain(self):
        """Keep profanity legible in colour while preserving plain pipe output."""
        environment = {**os.environ, "FORCE_COLOR": "1", "COLUMNS": "200"}
        environment.pop("NO_COLOR", None)
        output = self.check({"claude.md": "Use structured logging.\n"}, environment=environment, expected=[
            "Linters / ast-grep",
            "  Put it in a linter or ast-grep rule. Stop asking nicely and make the bloody thing fail.",
            "  claude.md:1",
            "Make the checks catch violations. Then delete the fucking prose.",
        ])
        self.assertIn("\x1b[1;91m", output)
        self.assertNotIn("\x1b[2m", output)



if __name__ == "__main__":
    unittest.main()
