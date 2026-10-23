"""Matcher cases adapted from empirical categories and public repository patterns."""

import unittest

from fym.analysis import suggestions


class MatcherTests(unittest.TestCase):
    def test_instruction_patterns(self):
        """Recognise common instructions without requiring the word 'must'."""
        cases = {
            "Prefer ES modules over CommonJS.": "Linters / ast-grep",
            "No wildcard imports.": "Linters / ast-grep",
            "Keep source files ASCII only.": "Linters / ast-grep",
            "Use snake_case for functions.": "Linters / ast-grep",
            "Avoid deprecated check() calls.": "Linters / ast-grep",
            "Use strict mode and noImplicitAny.": "Type checks",
            "Public functions must have type annotations.": "Type checks",
            "Avoid Any in public APIs.": "Type checks",
            "Never hardcode credentials.": "Security checks",
            "Do not log secrets.": "Security checks",
            "Always validate authorization.": "Security checks",
            "Ensure p99 latency stays under 100ms.": "Performance tests",
            "Avoid N+1 queries.": "Performance tests",
            "Keep memory usage below the stated limit.": "Performance tests",
            "Ensure keyboard navigation works.": "UI / accessibility tests",
            "Use ARIA labels for controls.": "UI / accessibility tests",
            "Always run visual regression tests.": "UI / accessibility tests",
            "Use Conventional Commits for commit messages.": "Repository checks",
            "PR titles must start with the package name.": "Repository checks",
            "Never include a Co-Authored-By trailer.": "Repository checks",
            "Validate environment variables on startup.": "Environment checks",
            "Use the Python version specified by the project.": "Environment checks",
            "Include JSDoc for exported functions.": "Documentation checks",
            "Docstrings should contain executable examples.": "Documentation checks",
            "Domain must not import persistence.": "Architecture tests",
            "Business logic should reside in src/core.": "Architecture tests",
            "IDs must be valid UUIDs.": "Contract tests",
            "Changes must be backward compatible.": "Contract tests",
            "Invalid requests must return 400.": "Acceptance tests",
            "Never edit snapshots manually.": "Acceptance tests",
            "Use real fixtures instead of mocks.": "Acceptance tests",
            "Requests must accept any valid payload.": "Acceptance tests",
        }
        for text, group in cases.items():
            with self.subTest(text=text):
                self.assertEqual(suggestions(text), {group: [1]})

    def test_command_forms(self):
        """Recognise commands in lists, inline spans and environment-prefixed lines."""
        for command in (
            "uv run pytest", "- Install deps: `pnpm install`",
            "- Run tests: `pnpm test`", "1. `npm run typecheck`",
            "`pnpm --filter=next build`", "`yarn test:core`",
            "Run `cargo nextest run --workspace` before submitting.",
            "INSTA_UPDATE=always cargo test --workspace",
            "./gradlew test", "go test ./...", "dotnet test",
            "poetry run pytest", "pre-commit run --all-files",
        ):
            with self.subTest(command=command):
                self.assertEqual(suggestions(command), {"Scripts + CI": [1]})

    def test_heading_only_sections(self):
        for heading, group in (
            ("Architecture", "Architecture tests"),
            ("Repository Layout", "Architecture tests"),
            ("Codebase structure", "Architecture tests"),
            ("Code style", "Linters / ast-grep"),
            ("Coding Guidelines", "Linters / ast-grep"),
            ("How to write tests", "Acceptance tests"),
            ("Security Considerations", "Security checks"),
            ("Performance", "Performance tests"),
            ("UI/UX", "UI / accessibility tests"),
            ("Environment Setup", "Environment checks"),
            ("Commit Messages and Pull Requests", "Repository checks"),
        ):
            with self.subTest(heading=heading):
                self.assertEqual(suggestions(f"# {heading}\nPlaceholder text."), {group: [1]})

    def test_concrete_evidence_supersedes_topic_heading(self):
        self.assertEqual(suggestions("# Code style\nNo wildcard imports.\nSingle quotes, no semicolons.\n"),
                         {"Linters / ast-grep": [2, 3]})

    def test_nested_sections_do_not_repeat_parent_heading(self):
        self.assertEqual(suggestions("# Architecture\n## Dependencies\nDomain must not import API.\n"),
                         {"Architecture tests": [3]})

    def test_unrelated_prose_is_not_a_requirement(self):
        for text in (
            "We discussed security, architecture and performance yesterday.",
            "Always ask the user what they want.",
            "You are an expert React developer.",
            "See the issue tracker for the current roadmap.",
            "Use this skill when writing tests.",
            "---\nname: tests\ndescription: Always run pytest.\n---\n",
            "# History\nThe project used npm in 2022.",
            "<!--\n# Security\nNever log secrets.\n-->",
            "```python\n# Security\nprint('never log secrets')\n```",
        ):
            with self.subTest(text=text):
                self.assertEqual(suggestions(text), {})


if __name__ == "__main__":
    unittest.main()
