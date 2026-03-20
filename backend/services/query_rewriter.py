from services.llm_service import LLMService

class QueryRewriter:

    def __init__(self):
        self.llm = LLMService()

    def rewrite(self, query: str) -> str:

        prompt = f"""
Rewrite the following question to be more specific for searching GitLab documentation.

Question: {query}

Rewritten:
"""

        try:
            return self.llm.generate(prompt)
        except:
            return query