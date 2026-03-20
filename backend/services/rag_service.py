# from typing import Dict, Any, Optional, List

# from services.retrieval_service import RetrievalService
# from services.llm_service import LLMService
# from prompt.prompt_builder import PromptBuilder
# from models.response_builder import ResponseBuilder


# class RAGService:
#     """
#     Orchestrates the full Retrieval-Augmented Generation pipeline.

#     Pipeline:
#     1. Retrieve relevant documents
#     2. Build prompt with retrieved context
#     3. Generate answer using LLM
#     4. Build structured response
#     """

#     def __init__(
#         self,
#         retrieval_service: RetrievalService,
#         llm_service: LLMService,
#         prompt_builder: PromptBuilder,
#         response_builder: ResponseBuilder,
#     ):
#         """
#         Initialize RAG pipeline dependencies.
#         Dependencies are injected so they are created only once
#         during application startup.
#         """

#         self.retrieval_service = retrieval_service
#         self.prompt_builder = prompt_builder
#         self.llm_service = llm_service
#         self.response_builder = response_builder

#     def handle_query(
#         self,
#         question: str,
#         topic: Optional[str] = None
#     ) -> Dict[str, Any]:
#         """
#         Process a user query through the full RAG pipeline.
#         """

#         if not question or not question.strip():
#             raise ValueError("Question cannot be empty")

#         # Step 1 — Retrieve relevant documents
#         retrieved_docs: List[Dict[str, Any]] = self.retrieval_service.retrieve(
#             query=question,
#             topic_filter=topic
#         )

#         # Handle case where retrieval returns nothing
#         if not retrieved_docs:
#             return {
#                 "answer": "I couldn't find relevant information in the GitLab documentation.",
#                 "sources": [],
#                 "preview": [],
#                 "suggested_questions": []
#             }

#         # Step 2 — Build prompt
#         prompt = self.prompt_builder.build_prompt(
#             question=question,
#             documents=retrieved_docs
#         )

#         # Step 3 — Generate answer
#         llm_answer = self.llm_service.generate(prompt)

#         # Step 4 — Build structured response
#         response = self.response_builder.build(
#             answer=llm_answer,
#             retrieved_docs=retrieved_docs
#         )

#         return response


from typing import Dict, Any, Optional, List

from services.retrieval_service import RetrievalService
from services.llm_service import LLMService
from services.chat_memory import ChatMemory  # ✅ NEW
from prompt.prompt_builder import PromptBuilder
from models.response_builder import ResponseBuilder


class RAGService:
    """
    Orchestrates the full Retrieval-Augmented Generation pipeline.

    Pipeline:
    1. Get chat history
    2. Retrieve relevant documents
    3. Build prompt with context + history
    4. Generate answer using LLM
    5. Store conversation
    6. Build structured response
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_service: LLMService,
        prompt_builder: PromptBuilder,
        response_builder: ResponseBuilder,
    ):
        self.retrieval_service = retrieval_service
        self.prompt_builder = prompt_builder
        self.llm_service = llm_service
        self.response_builder = response_builder

        # ✅ Chat memory (in-memory storage)
        self.memory = ChatMemory()

    def handle_query(
        self,
        question: str,
        session_id: str,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        # ✅ STEP 1 — Get chat history
        history = self.memory.get_history(session_id)

        # ✅ STEP 2 — Retrieve relevant documents
        retrieved_docs: List[Dict[str, Any]] = self.retrieval_service.retrieve(
            query=question,
            topic_filter=topic
        )

        # Handle case where retrieval returns nothing
        if not retrieved_docs:
            return {
                "answer": "I couldn't find relevant information in the GitLab documentation.",
                "sources": [],
                "preview": [],
                "suggested_questions": []
            }

        # ✅ STEP 3 — Build prompt (include history)
        prompt = self.prompt_builder.build_prompt(
            question=question,
            documents=retrieved_docs,
            chat_history=history
        )

        # ✅ STEP 4 — Generate answer
        try:
            llm_answer = self.llm_service.generate(prompt)
        except Exception:
            return {
                "answer": "There was an error generating the response. Please try again.",
                "sources": [],
                "preview": [],
                "suggested_questions": []
            }

        # ✅ STEP 5 — Store conversation
        self.memory.add_message(session_id, "user", question)
        self.memory.add_message(session_id, "assistant", llm_answer)

        # ✅ STEP 6 — Build structured response
        response = self.response_builder.build(
            answer=llm_answer,
            retrieved_docs=retrieved_docs
        )

        return response