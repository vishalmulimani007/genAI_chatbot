# from typing import List, Dict, Any

# from config_loader import ConfigLoader


# class PromptBuilder:
#     """
#     Builds the RAG prompt sent to the LLM.

#     Responsibilities:
#     - Format retrieved documents into context
#     - Add hallucination guardrails
#     - Insert user question
#     """

#     def __init__(self):
#         config_loader = ConfigLoader()
#         rag_config = config_loader.get_section("rag")

#         self.max_context_chunks = rag_config["max_context_chunks"]
#         self.enable_guardrails = rag_config["enable_guardrails"]

#     def build_prompt(self, question: str, documents: List[Dict[str, Any]]) -> str:
#         """
#         Construct the final prompt for the LLM.
#         """

#         context = self._build_context(documents)

#         prompt = f"""
# You are an assistant that answers questions using GitLab documentation.

# Use ONLY the provided context to answer the question.

# If the answer is not present in the context, say:
# "I couldn't find that information in the GitLab documentation."

# Always include:
# 1. A clear answer
# 2. Source citations
# 3. Suggested follow-up questions

# CONTEXT:
# {context}

# QUESTION:
# {question}

# ANSWER:
# """

#         return prompt.strip()

#     def _build_context(self, documents: List[Dict[str, Any]]) -> str:
#         """
#         Format retrieved documents into structured context.
#         """

#         context_sections = []

#         for doc in documents[: self.max_context_chunks]:

#             metadata = doc.get("metadata", {})
#             title = metadata.get("title", "Unknown")
#             url = metadata.get("url", "Unknown")
#             topic = metadata.get("topic", "Unknown")

#             text = doc.get("text", "")

#             section = f"""
# Title: {title}
# Topic: {topic}
# URL: {url}

# Content:
# {text}
# """

#             context_sections.append(section.strip())

#         return "\n\n".join(context_sections)

from typing import List, Dict, Any, Optional

from config_loader import ConfigLoader


class PromptBuilder:
    """
    Builds the RAG prompt sent to the LLM.

    Responsibilities:
    - Format retrieved documents into context
    - Include conversation history
    - Add hallucination guardrails
    - Insert user question
    """

    def __init__(self):
        config_loader = ConfigLoader()
        rag_config = config_loader.get_section("rag")

        self.max_context_chunks = rag_config["max_context_chunks"]
        self.enable_guardrails = rag_config["enable_guardrails"]

    def build_prompt(
        self,
        question: str,
        documents: List[Dict[str, Any]],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Construct the final prompt for the LLM with chat history.
        """

        context = self._build_context(documents)
        history_text = self._build_history(chat_history)

        prompt = f"""
You are a GitLab assistant.

You must answer using:
1. Conversation history (if relevant)
2. Provided context (PRIMARY source)

STRICT RULES:
- Use context as the main source of truth
- Do NOT make assumptions
- If answer is not in context, say:
  "I couldn't find that information in the GitLab documentation."

CONVERSATION HISTORY:
{history_text}

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        return prompt.strip()

    def _build_history(
        self,
        chat_history: Optional[List[Dict[str, str]]]
    ) -> str:
        """
        Convert chat history into formatted text.
        Only last few messages are included to avoid token overflow.
        """

        if not chat_history:
            return "No previous conversation."

        history_lines = []

        # Take last 5 messages only
        for msg in chat_history[-5:]:
            role = msg.get("role", "user").upper()
            content = msg.get("content", "")

            history_lines.append(f"{role}: {content}")

        return "\n".join(history_lines)

    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into structured context.
        """

        context_sections = []

        for i, doc in enumerate(documents[: self.max_context_chunks]):

            metadata = doc.get("metadata", {})
            title = metadata.get("title", "Unknown")
            url = metadata.get("url", "Unknown")
            topic = metadata.get("topic", "Unknown")

            text = doc.get("text", "")

            # Limit text size (important)
            text = text[:800]

            section = f"""
[DOCUMENT {i+1}]
Title: {title}
Topic: {topic}
URL: {url}

Content:
{text}
"""

            context_sections.append(section.strip())

        return "\n\n".join(context_sections)