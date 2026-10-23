from pathlib import Path, PurePath
from typing import Annotated

import typer
from rich.console import Console
from rich.text import Text

from fym.analysis import GUIDANCE, suggestions

SUFFIXES = {".md", ".markdown", ".mdx"}

SLOP = (
    "spec*",
    "*_spec",
    "plan*",
    "*_plan",
    "design*",
    "proposal*",
    "implementation*",
    "architecture*",
    "analysis*",
    "summary*",
    "*_summary",
    "notes",
    "todo",
    "phase*",
    "step*",
    "status*",
    "progress*",
    "migration*",
    "refactor*",
    "fixes*",
    "*_report",
    "*complete*",
    "*_review",
    "claude",
    "agent",
    "agents",
    "gemini",
    "codex",
    "copilot-instructions",
    "skill",
)

KEEP = ("README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE.md")
SKILL_NAMESPACES = {".agents", ".claude", ".codex", ".cursor", ".github", ".gemini", ".opencode", ".windsurf", ".roo", ".kilocode"}

app = typer.Typer(
    add_completion=False, help="Errors on any markdown outside the docs folder."
)


def scan_subdirectories(directory: Path, names: list[str], root: Path) -> list[str]:
    if directory != root and directory.name in SKILL_NAMESPACES:
        return [name for name in names if name == "skills"]
    return [name for name in names
            if name != "node_modules" and (not name.startswith(".") or name in SKILL_NAMESPACES)]


def collect(roots: list[Path]) -> list[Path]:
    found: set[Path] = set()
    for root in roots:
        if root.is_dir():
            for directory, directories, filenames in root.walk():
                directories[:] = scan_subdirectories(directory, directories, root)
                if directory != root and directory.name in SKILL_NAMESPACES:
                    continue
                found.update(
                    directory / name
                    for name in filenames
                    if not name.startswith(".")
                    and Path(name).suffix.lower() in SUFFIXES
                )
        elif root.suffix.lower() in SUFFIXES:
            found.add(root)
    return sorted(found)


def slop(path: Path, patterns: tuple[str, ...]) -> bool:
    stem = PurePath(path.stem.lower())
    return any(stem.match(pattern) for pattern in patterns)


def offends(path: Path, docs: str, allow: list[str]) -> bool:
    if any(path.match(pattern) for pattern in allow):
        return False
    return docs not in path.parts


SWEARY_GUIDANCE = {
    "Architecture tests": "Put the boundaries in architecture tests. The diagram isn't going to enforce itself, is it?",
    "Linters / ast-grep": "Put it in a linter or ast-grep rule. Stop asking nicely and make the bloody thing fail.",
    "Contract tests": "Write contract tests. Your schema needs teeth, not another fucking paragraph.",
    "Acceptance tests": "Write acceptance tests. Assert the behaviour instead of writing fan fiction about it.",
    "Type checks": "Configure the type checker. 'Please use types' is not a fucking compiler option.",
    "Security checks": "Add scanners and security tests. A stern paragraph won't stop a fucking exploit.",
    "Performance tests": "Write a benchmark. 'Keep it fast' measures precisely fuck all.",
    "UI / accessibility tests": "Add browser and accessibility checks. The checklist can't press the fucking Tab key.",
    "Repository checks": "Put the convention in hooks or CI. Stop policing commits with a fucking essay.",
    "Environment checks": "Validate the environment in code. Another setup sermon won't configure a bloody thing.",
    "Documentation checks": "Lint the docs and execute the examples. Prove the bloody things work.",
    "Scripts + CI": "Put the commands in scripts and CI. The markdown isn't going to run itself, is it?",
}


def print_groups(groups: dict[str, list[str]], agent: bool) -> None:
    console = Console(stderr=True, highlight=False)
    guidance = GUIDANCE if agent else SWEARY_GUIDANCE
    fallback = ("No enforceable rules recognised; review before moving or deleting." if agent
                else "No rules found. Review it, then move useful docs or bin the fucking thing.")
    for replacement, references in groups.items():
        console.print(Text(replacement, style="bold magenta"), soft_wrap=not console.is_terminal)
        console.print(Text(f"  {guidance.get(replacement, fallback)}", style="dim" if agent else "bold bright_red"), soft_wrap=not console.is_terminal)
        for reference in references:
            location = Text(f"  {reference}", style="cyan")
            location.highlight_regex(r":[\d,]+$", style="bold yellow")
            console.print(location, soft_wrap=not console.is_terminal)
    if groups:
        closing = ("Reuse existing checks. Verify they catch violations before removing the cited prose." if agent
                   else "Make the checks catch violations. Then delete the fucking prose.")
        console.print(Text(closing, style="dim italic" if agent else "bold bright_red"), soft_wrap=not console.is_terminal)


@app.command()
def main(
    paths: Annotated[
        list[Path] | None, typer.Argument(help="Files or directories to check.")
    ] = None,
    docs: Annotated[
        str, typer.Option(help="Directory name markdown is allowed to live in.")
    ] = "docs",
    allow: Annotated[
        list[str] | None, typer.Option(help="Glob patterns to spare.")
    ] = None,
    agent: Annotated[
        bool, typer.Option("--agent", help="Read flagged markdown and suggest checks for discovered requirements.")
    ] = False,
) -> None:
    spared = allow if allow else list(KEEP)
    guilty = [path for path in collect(paths or [Path()])
              if slop(path, SLOP) or offends(path, docs, spared)]
    if not guilty:
        raise typer.Exit()
    groups: dict[str, list[str]] = {}
    for path in guilty:
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            typer.echo(f"{path}: Cannot analyse markdown: {error}", err=True)
            continue
        found = suggestions(content)
        if not found:
            groups.setdefault(f"Review / move to {docs}/", []).append(str(path))
        for replacement, numbers in found.items():
            references = ",".join(map(str, numbers))
            groups.setdefault(replacement, []).append(f"{path}:{references}")
    print_groups(groups, agent)
    raise typer.Exit(1)
