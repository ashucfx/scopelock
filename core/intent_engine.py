"""
Intent Decomposer Engine for ScopeLock.

Translates informal natural-language requirements into formal
ScopePolicy contracts. Supports deterministic offline heuristic decomposition
with seamless fallback from LLM inference.
"""

import os
import re

from scopelock.core.schema import ExpectedCapability, ScopePolicy
from scopelock.core.taxonomy import CapabilityCategory


class HeuristicIntentEngine:
    """
    Deterministic rule-based intent analyzer that requires zero external APIs,
    executes with sub-millisecond latency, and works 100% offline.
    """

    # Ambiguity patterns
    AMBIGUOUS_PATTERNS = (
        r"\bmanage my stuff\b",
        r"\bdo whatever\b",
        r"\bgeneral utility\b",
        r"\bsystem tool\b$",
    )

    # Keyword patterns for capabilities
    NETWORK_KEYWORDS = (
        "fetch",
        "http",
        "api",
        "weather",
        "download",
        "request",
        "url",
        "rest",
        "endpoint",
        "scrape",
        "server",
        "webhook",
    )

    FILESYSTEM_KEYWORDS = (
        "file",
        "csv",
        "json",
        "read",
        "write",
        "save",
        "log",
        "directory",
        "folder",
        "disk",
        "backup",
        "txt",
        "export",
    )

    PROCESS_KEYWORDS = (
        "shell",
        "command",
        "bash",
        "execute",
        "run process",
        "terminal",
        "spawn",
        "exec",
        "cli command",
    )

    NEGATION_RE = re.compile(
        r"\b(?:no|without|never|avoid|avoids|avoiding|forbid|forbids|forbidden|"
        r"prohibit|prohibits|prohibited|disallow|disallows|disallowed|not|"
        r"do\s+not|does\s+not|did\s+not|don't|doesn't|didn't|"
        r"must\s+not|mustn't|should\s+not|shouldn't|cannot|can't)\b",
        re.IGNORECASE,
    )

    DATABASE_KEYWORDS = (
        "database",
        "db",
        "sql",
        "postgres",
        "mysql",
        "mongodb",
        "sqlite",
        "query",
        "record",
        "table",
    )

    OFFLINE_STRICT_KEYWORDS = (
        "calculator",
        "math",
        "arithmetic",
        "matrix",
        "sort",
        "unit converter",
        "fibonacci",
        "factorial",
        "string format",
        "offline",
        "pure function",
    )

    @classmethod
    def _mentions_authorized_capability(cls, prompt: str, keywords: tuple[str, ...]) -> bool:
        """Return whether a capability keyword appears without nearby negation.

        This conservative check does not attempt full natural-language parsing. A
        negator within the same punctuation-delimited clause and up to four words
        before a capability term prevents that term from granting permission.
        """
        text = prompt.lower()
        for keyword in keywords:
            escaped = re.escape(keyword).replace(r"\ ", r"\s+")
            for match in re.finditer(rf"(?<!\w){escaped}(?!\w)", text):
                clause_start = max(
                    (text.rfind(mark, 0, match.start()) for mark in ".,;:!?\n"),
                    default=-1,
                ) + 1
                clause_end = min(
                    (position for mark in ".,;:!?\n" if (position := text.find(mark, match.end())) >= 0),
                    default=len(text),
                )
                prefix = text[clause_start : match.start()]
                suffix = text[match.end() : clause_end]
                negated_before = any(
                    len(re.findall(r"\b\w+\b", prefix[negator.end() :])) <= 4
                    for negator in cls.NEGATION_RE.finditer(prefix)
                )
                negated_after = any(
                    len(re.findall(r"\b\w+\b", suffix[: negator.start()])) <= 4
                    for negator in cls.NEGATION_RE.finditer(suffix)
                )
                if negated_before or negated_after:
                    continue
                return True
        return False

    @classmethod
    def decompose(cls, prompt: str) -> ScopePolicy:
        """Decompose a natural language prompt into a ScopePolicy."""
        prompt_lower = prompt.lower().strip()

        # Check for ambiguity
        for pattern in cls.AMBIGUOUS_PATTERNS:
            if re.search(pattern, prompt_lower):
                return ScopePolicy(
                    stated_intent=prompt,
                    allowed_categories=set(),
                    expected_capabilities=[],
                    disallowed_categories={
                        CapabilityCategory.NETWORK,
                        CapabilityCategory.PROCESS,
                        CapabilityCategory.SECRET,
                    },
                    is_ambiguous=True,
                    clarification_prompt=(
                        "Your requirement is ambiguous. Please clarify if network egress "
                        "or filesystem access is required for this utility."
                    ),
                )

        allowed_categories: set[CapabilityCategory] = set()
        expected_caps = []
        disallowed_categories: set[CapabilityCategory] = set()

        # Check if strictly offline / pure computation
        is_strictly_offline = any(k in prompt_lower for k in cls.OFFLINE_STRICT_KEYWORDS)

        # Network check
        has_network = cls._mentions_authorized_capability(prompt_lower, cls.NETWORK_KEYWORDS)
        if has_network and not is_strictly_offline:
            allowed_categories.add(CapabilityCategory.NETWORK)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.NETWORK,
                    action="*",
                    target_scope="*",
                    justification=f"Prompt explicitly mentions network-related requirements: '{prompt}'",
                )
            )
        else:
            disallowed_categories.add(CapabilityCategory.NETWORK)

        # FileSystem check
        has_fs = cls._mentions_authorized_capability(prompt_lower, cls.FILESYSTEM_KEYWORDS)
        if has_fs and not is_strictly_offline:
            allowed_categories.add(CapabilityCategory.FILESYSTEM)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.FILESYSTEM,
                    action="*",
                    target_scope="*",
                    justification=f"Prompt mentions filesystem operations: '{prompt}'",
                )
            )
        elif not has_fs:
            disallowed_categories.add(CapabilityCategory.FILESYSTEM)

        # Database check
        has_database = cls._mentions_authorized_capability(prompt_lower, cls.DATABASE_KEYWORDS)
        if has_database:
            allowed_categories.add(CapabilityCategory.DATABASE)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.DATABASE,
                    action="*",
                    target_scope="*",
                    justification=f"Prompt mentions database operations: '{prompt}'",
                )
            )
        else:
            disallowed_categories.add(CapabilityCategory.DATABASE)

        # Process check
        has_proc = cls._mentions_authorized_capability(prompt_lower, cls.PROCESS_KEYWORDS)
        if has_proc:
            allowed_categories.add(CapabilityCategory.PROCESS)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.PROCESS,
                    action="*",
                    target_scope="*",
                    justification="Process execution explicitly requested by prompt.",
                )
            )
        else:
            disallowed_categories.add(CapabilityCategory.PROCESS)

        # Secrets & Runtime default to disallowed unless explicitly stated
        disallowed_categories.add(CapabilityCategory.SECRET)
        disallowed_categories.add(CapabilityCategory.RUNTIME)

        # Extract an intuitive application name
        app_name = "AI-Generated Utility"
        if "calculator" in prompt_lower:
            app_name = "Arithmetic Calculator CLI"
        elif "weather" in prompt_lower:
            app_name = "Weather Client"
        elif "csv" in prompt_lower or "file" in prompt_lower:
            app_name = "File Reader Utility"

        return ScopePolicy(
            application_name=app_name,
            stated_intent=prompt,
            allowed_categories=allowed_categories,
            expected_capabilities=expected_caps,
            disallowed_categories=disallowed_categories,
            is_ambiguous=False,
        )


class IntentDecomposer:
    """
    Unified intent decomposer. Uses LLM when OPENAI_API_KEY is available,
    otherwise transparently falls back to the deterministic HeuristicIntentEngine.
    """

    @classmethod
    def decompose(cls, prompt: str, force_offline: bool = False) -> ScopePolicy:
        """Parse natural language prompt into a ScopePolicy."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and not force_offline:
            try:
                # LLM decomposition (if openai installed and key provided)
                import openai

                client = openai.OpenAI(api_key=api_key)
                system_prompt = (
                    "You are a formal security analyst. Convert the natural language requirement "
                    "into a strict capability policy. Do not hallucinate permissions. "
                    "If an offline utility is requested, allow zero permissions."
                )
                response = client.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Requirement: {prompt}"},
                    ],
                    response_format=ScopePolicy,
                )
                return response.choices[0].message.parsed
            except Exception:  # noqa: BLE001, S110
                # Graceful fallback to deterministic heuristic
                pass

        return HeuristicIntentEngine.decompose(prompt)
