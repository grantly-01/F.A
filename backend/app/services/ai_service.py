"""
Funding Aggregator - AI Service (Groq Integration)
"""
import json
import time
from typing import Optional

from groq import Groq, AsyncGroq
from app.config import get_settings
from app.core.logging import get_logger
from app.core.metrics import AI_REQUESTS, AI_LATENCY

logger = get_logger(__name__)
settings = get_settings()


class AIService:
    """
    AI-powered text processing service using Groq API.
    Uses LLaMA 3.3 70B for:
    - Keyword extraction
    - Text summarization  
    - Smart categorization
    - Natural language search query parsing
    """

    def __init__(self):
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        else:
            self.client = None
            logger.warning("groq_api_key_missing", message="AI features will be disabled")

    def _call_groq(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> Optional[str]:
        """Make a call to Groq API with error handling and metrics."""
        if not self.client:
            return None

        start_time = time.time()
        try:
            kwargs = {
                "model": settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 1024,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            
            duration = time.time() - start_time
            AI_LATENCY.labels(operation="groq_call").observe(duration)
            AI_REQUESTS.labels(operation="groq_call", status="success").inc()

            return response.choices[0].message.content

        except Exception as e:
            duration = time.time() - start_time
            AI_LATENCY.labels(operation="groq_call").observe(duration)
            AI_REQUESTS.labels(operation="groq_call", status="error").inc()
            logger.error("groq_api_error", error=str(e))
            return None

    def extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from grant description using AI."""
        system_prompt = """You are a keyword extraction specialist for funding and grant opportunities.
Extract 5-10 most relevant keywords/phrases from the given text.
Return a JSON object with a single key "keywords" containing an array of strings.
Focus on: research fields, technologies, eligibility criteria, funding types.
Example: {"keywords": ["machine learning", "healthcare", "early-career researchers", "federal funding"]}"""

        result = self._call_groq(system_prompt, text[:3000])
        if result:
            try:
                parsed = json.loads(result)
                keywords = parsed.get("keywords", [])
                AI_REQUESTS.labels(operation="extract_keywords", status="success").inc()
                return keywords
            except json.JSONDecodeError:
                logger.warning("keyword_extraction_parse_error", raw=result[:200])
        
        AI_REQUESTS.labels(operation="extract_keywords", status="fallback").inc()
        return []

    def summarize_grant(self, title: str, description: str) -> Optional[str]:
        """Generate a concise AI summary of a grant."""
        system_prompt = """You are a grant summarization specialist.
Create a concise 2-3 sentence summary of the grant opportunity.
Focus on: who can apply, what's funded, how much, and the deadline.
Return a JSON object with key "summary" containing the summary string.
Example: {"summary": "This grant provides up to $50,000 for early-career researchers in biomedical sciences. Applicants must hold a PhD and be affiliated with a US institution. The deadline is March 2025."}"""

        user_prompt = f"Title: {title}\n\nDescription: {description[:4000]}"
        result = self._call_groq(system_prompt, user_prompt)
        
        if result:
            try:
                parsed = json.loads(result)
                summary = parsed.get("summary", "")
                AI_REQUESTS.labels(operation="summarize", status="success").inc()
                return summary
            except json.JSONDecodeError:
                logger.warning("summary_parse_error", raw=result[:200])

        AI_REQUESTS.labels(operation="summarize", status="fallback").inc()
        return None

    def categorize_grant(self, title: str, description: str, categories: list[str]) -> list[str]:
        """Categorize a grant into predefined categories using AI."""
        system_prompt = f"""You are a grant categorization specialist.
Given a grant description and a list of available categories, select 1-3 most relevant categories.
Available categories: {json.dumps(categories)}
Return a JSON object with key "categories" containing an array of selected category names.
Only select from the provided categories list."""

        user_prompt = f"Title: {title}\n\nDescription: {description[:3000]}"
        result = self._call_groq(system_prompt, user_prompt)

        if result:
            try:
                parsed = json.loads(result)
                selected = parsed.get("categories", [])
                # Validate against available categories
                valid = [c for c in selected if c in categories]
                AI_REQUESTS.labels(operation="categorize", status="success").inc()
                return valid
            except json.JSONDecodeError:
                logger.warning("categorize_parse_error", raw=result[:200])

        AI_REQUESTS.labels(operation="categorize", status="fallback").inc()
        return []

    def parse_natural_language_query(self, query: str) -> dict:
        """
        Parse a natural language search query into structured filters.
        Example: "grants for CS students under $10k with deadline in 2025"
        -> {"keywords": ["CS", "computer science"], "amount_max": 10000, "deadline_year": 2025}
        """
        system_prompt = """You are a search query parser for a grant aggregator.
Parse the user's natural language query into structured search parameters.
Return a JSON object with these optional keys:
- "keywords": array of search keywords
- "category": most relevant category (string)
- "amount_min": minimum amount (number)
- "amount_max": maximum amount (number)
- "country": country filter (string)
- "field": research/academic field (string)
- "eligibility": who can apply (string)
Only include keys that are clearly mentioned in the query."""

        result = self._call_groq(system_prompt, query)
        if result:
            try:
                parsed = json.loads(result)
                AI_REQUESTS.labels(operation="parse_query", status="success").inc()
                return parsed
            except json.JSONDecodeError:
                logger.warning("query_parse_error", raw=result[:200])

        AI_REQUESTS.labels(operation="parse_query", status="fallback").inc()
        return {"keywords": query.split()}

    def generate_recommendations_prompt(self, user_keywords: list[str], recent_favorites: list[str]) -> str:
        """Generate search keywords based on user preferences."""
        system_prompt = """You are a grant recommendation engine.
Based on the user's interests and recently favorited grants, suggest search keywords
that would help find relevant new grants.
Return a JSON object with key "search_terms" containing an array of 5-10 search terms."""

        user_prompt = f"""User interests/keywords: {json.dumps(user_keywords)}
Recently favorited grants: {json.dumps(recent_favorites[:10])}"""

        result = self._call_groq(system_prompt, user_prompt)
        if result:
            try:
                parsed = json.loads(result)
                return parsed.get("search_terms", user_keywords)
            except json.JSONDecodeError:
                pass
        return user_keywords


# Singleton instance
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """Get or create AI service singleton."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service
