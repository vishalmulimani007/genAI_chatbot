# from typing import List, Dict, Any

# from config_loader import ConfigLoader


# class ResponseBuilder:
#     """
#     Builds the final structured response returned by the API.

#     Responsibilities:
#     - Attach source citations
#     - Add page preview snippets
#     - Generate suggested questions
#     """

#     def __init__(self):
#         config_loader = ConfigLoader()
#         rag_config = config_loader.get_section("rag")

#         self.enable_citations = rag_config.get("enable_citations", True)
#         self.enable_page_preview = rag_config.get("enable_page_preview", True)
#         self.enable_suggested_questions = rag_config.get("enable_suggested_questions", True)

#     def build(
#         self,
#         answer: str,
#         retrieved_docs: List[Dict[str, Any]]
#     ) -> Dict[str, Any]:
#         """
#         Construct final API response.
#         """

#         response = {
#             "answer": answer
#         }

#         if self.enable_citations:
#             response["sources"] = self._build_sources(retrieved_docs)

#         if self.enable_page_preview:
#             response["preview"] = self._build_previews(retrieved_docs)

#         if self.enable_suggested_questions:
#             response["suggested_questions"] = self._build_suggestions()

#         return response

#     def _build_sources(self, docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
#         """
#         Extract citation sources from retrieved documents.
#         """

#         sources = []
#         seen_urls = set()

#         for doc in docs:
#             metadata = doc.get("metadata", {})
#             title = metadata.get("title")
#             url = metadata.get("url")

#             if url and url not in seen_urls:
#                 sources.append({
#                     "title": title,
#                     "url": url
#                 })
#                 seen_urls.add(url)

#         return sources

#     def _build_previews(self, docs: List[Dict[str, Any]]) -> List[str]:
#         """
#         Provide short preview snippets from retrieved documents.
#         """

#         previews = []

#         for doc in docs:
#             text = doc.get("text", "")
#             snippet = text[:200].strip()

#             if snippet:
#                 previews.append(snippet)

#         return previews

#     def _build_suggestions(self) -> List[str]:
#         """
#         Generate placeholder suggested questions.
#         (Can be replaced later by LLM-generated suggestions)
#         """

#         return [
#             "What are GitLab company values?",
#             "How does GitLab manage remote teams?",
#             "What is GitLab's hiring process?"
#         ]


from typing import List, Dict, Any

from config_loader import ConfigLoader
from services.llm_service import LLMService


class ResponseBuilder:
    """
    Builds the final structured response returned by the API.

    Responsibilities:
    - Attach source citations
    - Add page preview snippets
    - Generate dynamic suggested questions using LLM
    """

    def __init__(self):
        config_loader = ConfigLoader()
        rag_config = config_loader.get_section("rag")

        self.enable_citations = rag_config.get("enable_citations", True)
        self.enable_page_preview = rag_config.get("enable_page_preview", True)
        self.enable_suggested_questions = rag_config.get("enable_suggested_questions", True)

        # ✅ NEW: LLM for dynamic suggestions
        self.llm = LLMService()

    def build(
        self,
        answer: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Construct final API response.
        """

        response = {
            "answer": answer
        }

        if self.enable_citations:
            response["sources"] = self._build_sources(retrieved_docs)

        if self.enable_page_preview:
            response["preview"] = self._build_previews(retrieved_docs)

        if self.enable_suggested_questions:
            response["suggested_questions"] = self._generate_suggestions(answer)

        return response

    def _build_sources(self, docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Extract citation sources from retrieved documents.
        """

        sources = []
        seen_urls = set()

        for doc in docs:
            metadata = doc.get("metadata", {})
            title = metadata.get("title")
            url = metadata.get("url")

            if url and url not in seen_urls:
                sources.append({
                    "title": title,
                    "url": url
                })
                seen_urls.add(url)

        return sources

    def _build_previews(self, docs: List[Dict[str, Any]]) -> List[str]:
        """
        Provide clean preview snippets from retrieved documents.
        """

        previews = []

        for doc in docs:
            text = doc.get("text", "")

            # Clean + shorten preview
            snippet = " ".join(text.split())[:200]

            if snippet:
                previews.append(snippet)

        return previews

    def _generate_suggestions(self, answer: str) -> List[str]:
        """
        Generate follow-up questions dynamically using LLM.
        """

        prompt = f"""
Based on the following answer, generate 3 relevant follow-up questions.

Rules:
- Questions must be concise
- Questions must be related to the topic
- Do NOT repeat the same idea

Answer:
{answer}

Follow-up Questions:
"""

        try:
            response = self.llm.generate(prompt)

            # Convert LLM output into list
            lines = response.split("\n")
            questions = []

            for line in lines:
                line = line.strip("- ").strip()
                if line:
                    questions.append(line)

            return questions[:3]

        except Exception:
            # fallback (still dynamic-ish but safe)
            return []