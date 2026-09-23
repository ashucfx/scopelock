"""
Intent Decomposer Engine for ScopeLock.

Translates informal natural-language requirements into formal
ScopePolicy contracts. Supports deterministic offline heuristic decomposition
with seamless fallback from LLM inference.
"""

import os
import re
from typing import Optional, Set
from scopelock.core.taxonomy import CapabilityCategory, CapabilityAction
from scopelock.core.schema import ScopePolicy, ExpectedCapability


class HeuristicIntentEngine:
    """
    Deterministic rule-based intent analyzer that requires zero external APIs,
    executes with sub-millisecond latency, and works 100% offline.
    """

    # Ambiguity patterns
    AMBIGUOUS_PATTERNS = [
        r"\bmanage my stuff\b",
        r"\bdo whatever\b",
        r"\bgeneral utility\b",
        r"\bsystem tool\b$",
    ]

    # Keyword patterns for capabilities
    NETWORK_KEYWORDS = [
        "fetch", "http", "api", "weather", "download", "request",
        "url", "rest", "endpoint", "scrape", "server", "webhook"
    ]

    FILESYSTEM_KEYWORDS = [
        "file", "csv", "json", "read", "write", "save", "log",
        "directory", "folder", "disk", "backup", "txt", "export"
    ]

    PROCESS_KEYWORDS = [
        "shell", "command", "bash", "execute", "run process", "terminal",
        "spawn", "exec", "cli command"
    ]

    DATABASE_KEYWORDS = [
        "database", "db", "sql", "postgres", "mysql", "mongodb",
        "sqlite", "query", "record", "table"
    ]

    OFFLINE_STRICT_KEYWORDS = [
        "calculator", "math", "arithmetic", "matrix", "sort",
        "unit converter", "fibonacci", "factorial", "string format",
        "offline", "pure function"
    ]

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
                        CapabilityCategory.SECRET
                    },
                    is_ambiguous=True,
                    clarification_prompt=(
                        "Your requirement is ambiguous. Please clarify if network egress "
                        "or filesystem access is required for this utility."
                    )
                )

        allowed_categories: Set[CapabilityCategory] = set()
        expected_caps = []
        disallowed_categories: Set[CapabilityCategory] = set()

        # Check if strictly offline / pure computation
        is_strictly_offline = any(k in prompt_lower for k in cls.OFFLINE_STRICT_KEYWORDS)

        # Network check
        has_network = any(k in prompt_lower for k in cls.NETWORK_KEYWORDS)
        if has_network and not is_strictly_offline:
            allowed_categories.add(CapabilityCategory.NETWORK)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.NETWORK,
                    action="*",
                    target_scope="*",
                    justification=f"Prompt explicitly mentions network-related requirements: '{prompt}'"
                )
            )
        else:
            disallowed_categories.add(CapabilityCategory.NETWORK)

        # FileSystem check
        has_fs = any(k in prompt_lower for k in cls.FILESYSTEM_KEYWORDS)
        if has_fs and not is_strictly_offline:
            allowed_categories.add(CapabilityCategory.FILESYSTEM)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.FILESYSTEM,
                    action="*",
                    target_scope="*",
                    justification=f"Prompt mentions filesystem operations: '{prompt}'"
                )
            )
        elif not has_fs:
            disallowed_categories.add(CapabilityCategory.FILESYSTEM)

        # Process check
        has_proc = any(k in prompt_lower for k in cls.PROCESS_KEYWORDS)
        if has_proc:
            allowed_categories.add(CapabilityCategory.PROCESS)
            expected_caps.append(
                ExpectedCapability(
                    category=CapabilityCategory.PROCESS,
                    action="*",
                    target_scope="*",
                    justification="Process execution explicitly requested by prompt."
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
            is_ambiguous=False
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
                        {"role": "user", "content": f"Requirement: {prompt}"}
                    ],
                    response_format=ScopePolicy
                )
                return response.choices[0].message.parsed
            except Exception:
                # Graceful fallback to deterministic heuristic
                pass

        return HeuristicIntentEngine.decompose(prompt)
