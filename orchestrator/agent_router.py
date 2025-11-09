import os
import yaml
import json
from typing import Dict, Any, Optional
from providers.llm_service_provider import get_llm_service
from core.logger import get_logger, log_info, log_warning, log_error, log_debug
from core.exceptions import ConfigError

logger = get_logger("AgentRouter")


class AgentRouter:
    """
    Multi-domain intent router.
    Domain is explicitly provided by the caller (frontend or orchestrator).
    Each domain corresponds to a directory under /data/<domain>/intents.yaml
    """

    def __init__(self, base_dir: str = "data", default_domain: str = "hello"):
        self.base_dir = base_dir
        self.default_domain = default_domain
        self.llm = get_llm_service()
        self.intent_configs = self._load_all_domains()

        log_info(
            "AgentRouter initialized.",
            domains=list(self.intent_configs.keys()),
            default_domain=self.default_domain,
        )

    # Load all domain intent configurations
    def _load_all_domains(self) -> Dict[str, Dict[str, Any]]:
        """Scan data directory and load intents.yaml for each domain"""
        domains: Dict[str, Dict[str, Any]] = {}

        if not os.path.exists(self.base_dir):
            raise ConfigError(f"Base directory not found: {self.base_dir}")

        for d in os.listdir(self.base_dir):
            domain_path = os.path.join(self.base_dir, d)
            if not os.path.isdir(domain_path):
                continue  # skip non-directory files

            intent_path = os.path.join(domain_path, "intents.yaml")
            if not os.path.exists(intent_path):
                log_warning("No intents.yaml found for domain.", domain=d)
                continue

            try:
                with open(intent_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                    intents = data.get("intents", {})
                    if intents:
                        domains[d] = intents
                        log_info("Loaded domain intents.", domain=d, count=len(intents))
                    else:
                        log_warning("Empty or invalid intents.yaml.", domain=d, path=intent_path)
            except Exception as e:
                log_error("Failed to load domain intents.", domain=d, error=str(e), path=intent_path)

        if not domains:
            raise ConfigError(f"No valid domain configurations found in '{self.base_dir}'")

        return domains

    # Classify intent for a given query and domain
    async def classify_intent(self, query: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Classify user intent for a given query within the specified domain.
        If domain is not provided or invalid, fall back to the default domain.
        """
        domain = domain or self.default_domain
        if domain not in self.intent_configs:
            log_warning("Unknown domain; falling back to default.", domain=domain, default=self.default_domain)
            domain = self.default_domain

        intents = self.intent_configs[domain]
        query_lower = query.lower().strip()

        log_debug("Starting intent classification.", domain=domain, query=query)

        # 1️⃣ Rule-based keyword matching
        for intent, meta in intents.items():
            for kw in meta.get("keywords", []):
                if kw.lower() in query_lower:
                    log_info("Rule-based intent matched.", domain=domain, intent=intent, keyword=kw)
                    return {
                        "domain": domain,
                        "intent": intent,
                        "confidence": 1.0,
                        "method": "rule",
                        "matched_keyword": kw,
                    }

        # 2️⃣ LLM-based classification (fallback)
        try:
            prompt = self._build_llm_prompt(query, domain, intents)
            raw = await self.llm.apredict(prompt)
            parsed = self._safe_parse(raw)

            if parsed.get("intent"):
                log_info(
                    "LLM classified intent.",
                    domain=domain,
                    query=query,
                    intent=parsed["intent"],
                    confidence=parsed.get("confidence", 0.8),
                )
                return {
                    "domain": domain,
                    "intent": parsed["intent"],
                    "confidence": parsed.get("confidence", 0.8),
                    "method": "llm",
                }

        except Exception as e:
            log_error("LLM-based intent classification failed.", domain=domain, error=str(e))

        # 3️⃣ Default fallback
        log_warning("No intent matched; using default fallback.", domain=domain, query=query)
        return {
            "domain": domain,
            "intent": "qa",
            "confidence": 0.5,
            "method": "default",
        }

    def _build_llm_prompt(self, query: str, domain: str, intents: Dict[str, Any]) -> str:
        """Build structured LLM classification prompt."""
        options = list(intents.keys())
        descs = [f"{k}: {v.get('description', '')}" for k, v in intents.items()]

        log_debug("Building LLM prompt for classification.", domain=domain, intent_options=options)

        return f"""
        You are an intent classifier for the domain '{domain}'.

        Possible intents: {options}

        Descriptions:
        {chr(10).join(descs)}

        Task:
        Identify which intent best fits this user query.
        Return ONLY JSON in this structure:
        {{
          "intent": "<one of {options}>",
          "confidence": float (0.0 - 1.0)
        }}

        Query: {query}
        """

    def _safe_parse(self, raw: Any) -> Dict[str, Any]:
        """Safely parse JSON output from the LLM."""
        if isinstance(raw, dict):
            return raw

        try:
            parsed = json.loads(str(raw))
            log_debug("LLM output parsed successfully.", output=parsed)
            return parsed
        except json.JSONDecodeError:
            log_warning("LLM returned non-JSON output; fallback used.", raw_output=str(raw))
            return {"intent": "qa", "confidence": 0.5}
