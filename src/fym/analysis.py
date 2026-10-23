"""Local, evidence-based suggestions for requirements found in Markdown."""

import re

GUIDANCE = {
    "Architecture tests": "Enforce the cited import boundaries and file placement with architecture tests.",
    "Linters / ast-grep": "Encode the cited conventions as linter or ast-grep rules with passing/failing fixtures.",
    "Contract tests": "Test the cited schemas with valid and invalid inputs.",
    "Acceptance tests": "Test the cited behaviour through public interfaces; assert observable outcomes.",
    "Type checks": "Encode the cited type requirements in compiler/type-checker configuration and CI.",
    "Security checks": "Enforce the cited security rules with scanners and negative security tests.",
    "Performance tests": "Turn the cited budgets into repeatable benchmarks or query-count checks.",
    "UI / accessibility tests": "Test the cited UI behaviour and accessibility with browser checks.",
    "Repository checks": "Enforce the cited commit and PR conventions with hooks or CI checks.",
    "Environment checks": "Validate the cited environment requirements in setup scripts or configuration schemas.",
    "Documentation checks": "Check the cited API documentation and examples with doc linters or executable examples.",
    "Scripts + CI": "Move the cited commands into scripts run by CI; propagate failures.",
}


# Topic taxonomy: Agent READMEs (arXiv:2511.12884), Table 3.
# The mappings to executable replacements are fym's design, not the paper's result.
RULES = (
    (r"\b(secrets?|credentials?|api keys?|passwords?|authentication|authorization|sql injection|xss|csrf|sanitize|sanitise|hardcod(?:e|ed|ing))\b", "Security checks"),
    (r"\b(type[- ]?(?:safe|safety|check(?:ing)?|hints?|annotations?)|strict mode|noImplicitAny|mypy|pyright|tsc|(?-i:Any)|casts?)\b", "Type checks"),
    (r"\b(latency|throughput|benchmarks?|performance|query count|n\+1|memory (?:usage|limit|budget)|p95|p99)\b", "Performance tests"),
    (r"\b(accessibility|a11y|aria|keyboard navigation|screen readers?|wcag|visual regression)\b", "UI / accessibility tests"),
    (r"\b(commit messages?|conventional commits?|pr titles?|pull request titles?|branch nam(?:e|es|ing)|co-authored-by)\b", "Repository checks"),
    (r"\b(environment variables?|env vars?|configuration|config validation|node version|python version|java version)\b|\.env\b", "Environment checks"),
    (r"\b(jsdoc|docstrings?|doctests?|public api documentation)\b", "Documentation checks"),
    (r"\b(wildcard imports?|import order|es modules?|commonjs|require\(|style|format(?:ting)?|naming|camelcase|snake_case|logging|logger|print|console\.log|semicolons?|single quotes?|double quotes?|indentation|ascii|line length|deprecated)\b", "Linters / ast-grep"),
    (r"\b(imports?|depend(?:s|encies|ency)?|layers?|boundar(?:y|ies)|folders?|director(?:y|ies)|files? live|reside|business logic)\b", "Architecture tests"),
    (r"\b(schemas?|contracts?|uuids?|data shapes?|required fields?|backward compatible|backwards compatibility|api signatures?|output format|json output|valid json|return artifact)\b", "Contract tests"),
    (r"\b(tests?|coverage|fixtures?|snapshots?|mock(?:s|ing)?|given|when|then|returns?|rejects?|accepts?|raises?|throws?|status codes?|responses?)\b", "Acceptance tests"),
)

HEADINGS = (
    (r"architectur|(?:project|repository|repo|codebase|folder|directory) (?:structure|layout)|dependency boundar", "Architecture tests"),
    (r"code style|coding (?:style|standards|guidelines)|naming conventions?|implementation (?:details|patterns)", "Linters / ast-grep"),
    (r"type (?:safety|checking)|typing", "Type checks"),
    (r"security|authentication|authorization", "Security checks"),
    (r"performance|optimisation|optimization|benchmark", "Performance tests"),
    (r"accessibility|ui/ux|user interface|user experience", "UI / accessibility tests"),
    (r"commit (?:messages?|conventions?)|pr (?:instructions|conventions|titles?)|pull requests?|version control", "Repository checks"),
    (r"configuration|environment|prerequisites", "Environment checks"),
    (r"documentation (?:requirements|standards)|docstrings", "Documentation checks"),
    (r"output format|return artifact|output schema", "Contract tests"),
    (r"build|deployment|devops|release|setup|running tests|run the tests|test commands|workflow|procedure|execution steps|step-by-step", "Scripts + CI"),
    (r"testing|writing tests|write tests|acceptance criteria|error handling|debugging|review checklist|validation|verification", "Acceptance tests"),
)

DIRECTIVE = re.compile(
    r"\b(must|should|shall|never|always|required|only|use|avoid|do not|don't|prefer|no|"
    r"ensure|validate|keep|include|add|write|run|follow|given|when|then|returns?|rejects?|accepts?)\b", re.I,
)


def heading_advice(title: str) -> str | None:
    for pattern, advice in HEADINGS:
        if re.search(pattern, title, re.I):
            return advice
    return None


def classify(text: str) -> str | None:
    for pattern, advice in RULES:
        if re.search(pattern, text, re.IGNORECASE):
            return advice
    return None


def line_advice(text: str, section: str) -> str | None:
    if re.search(r"\b(?:use|invoke|load|trigger) (?:this|the) skill\b", text, re.I):
        return None
    if is_command(text):
        return "Scripts + CI"
    if not DIRECTIVE.search(text) and not heading_advice(section):
        return None
    return classify(text)


def block_advice(language: str, content: str, section: str) -> str | None:
    if not content.strip():
        return None
    if language.strip().lower() == "mermaid" and re.match(r"\s*(graph|flowchart|classDiagram)\b", content):
        return "Architecture tests"
    if re.search(r"[├└]──", content):
        return "Architecture tests"
    if language.strip().lower() in {"sh", "bash", "shell", "console"}:
        return "Scripts + CI"
    if re.search(r"\b(style|conventions?|examples?|patterns?)\b", section, re.I):
        return "Linters / ast-grep"
    return None


COMMAND = re.compile(
    r"^(?:(?:[A-Z_][A-Z_0-9]*=\S+\s+)*)(?:"
    r"uv (?:run|sync|venv|pip|tool)\b|"
    r"(?:npm|pnpm|yarn|bun) (?:--\S+\s+)*(?:run|test[\w:-]*|build[\w:-]*|lint[\w:-]*|install|dev|exec|dlx|types)\b|"
    r"(?:python[\d.]* -m (?:pytest|unittest)|pytest|ruff|make|just|npx|mypy|pyright|tsc)\b|"
    r"cargo (?:test|nextest|build|check|clippy|fmt)\b|go (?:test|build|vet|fmt)\b|"
    r"(?:\./)?(?:gradlew|gradle|mvnw|mvn)\s+\S|dotnet (?:test|build|format)\b|"
    r"(?:poetry|pipenv) (?:run|install|sync)\b|pip[\d.]* install\b|"
    r"docker(?: compose)? (?:build|up|run)\b|pre-commit run\b)"
)


def is_command(text: str) -> bool:
    candidates = re.findall(r"`([^`]+)`", text)
    candidates.append(re.sub(r"^(?:[-*+] |\d+[.)] )", "", text.strip()).removeprefix("$ "))
    return any(COMMAND.match(candidate.strip()) for candidate in candidates)


def add_heading_fallbacks(headings, findings, line_count):
    """Keep topic-only sections visible, without repeating sections with evidence."""
    matched_lines = [line for numbers in findings.values() for line in numbers]
    for index, (number, level, title) in enumerate(headings):
        end = next((other for other, depth, _ in headings[index + 1:] if depth <= level), line_count + 1)
        if any(number < line < end for line in matched_lines):
            continue
        advice = heading_advice(title)
        if advice:
            findings.setdefault(advice, []).append(number)


def body_lines(content: str) -> list[str]:
    """Ignore YAML metadata without changing body line references."""
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        end = next((index for index, line in enumerate(lines[1:], 1)
                    if line.strip() in {"---", "..."}), None)
        if end is not None:
            lines[:end + 1] = [""] * (end + 1)
    return lines


def suggestions(content: str) -> dict[str, list[int]]:
    """Return line-linked advice only for recognised prose or Markdown blocks."""
    lines = body_lines(content)
    findings: dict[str, list[int]] = {}
    section = ""
    headings: list[tuple[int, int, str]] = []
    in_comment = False
    fence = ""
    block: list[str] = []
    block_line = 0
    language = ""
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not fence:
            if in_comment:
                in_comment = "-->" not in stripped
                continue
            if stripped.startswith("<!--"):
                in_comment = "-->" not in stripped
                continue
        marker = re.match(r"^(`{3,}|~{3,})(.*)$", stripped)
        if marker:
            if not fence:
                fence, language = marker.groups()
                block_line = number
                block = []
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                content = "\n".join(block)
                advice = block_advice(language, content, section)
                if advice:
                    findings.setdefault(advice, []).append(block_line)
                fence = ""
            continue
        if fence:
            block.append(line)
            continue
        if stripped.startswith("#"):
            section = stripped.lstrip("# ").rstrip("# ")
            headings.append((number, len(stripped) - len(stripped.lstrip("#")), section))
            continue
        advice = line_advice(stripped, section)
        if advice:
            findings.setdefault(advice, []).append(number)
    add_heading_fallbacks(headings, findings, len(lines))
    return {advice: sorted(set(numbers)) for advice, numbers in sorted(findings.items(), key=lambda item: min(item[1]))}
