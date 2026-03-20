from typing import List, Dict, Any, Optional

from config_loader import ConfigLoader
from services.embedding_service import EmbeddingService
from database.chroma_client import ChromaClient


class RetrievalService:
    """
    Handles retrieval of relevant documents from the vector database.

    Steps:
    1. Generate query embedding
    2. Perform vector similarity search
    3. Apply topic filtering (if provided)
    4. Format results for the RAG pipeline
    """

    def __init__(self):
        config_loader = ConfigLoader()
        retrieval_config = config_loader.get_section("retrieval")

        self.top_k = retrieval_config["top_k"]

        self.embedding_service = EmbeddingService()
        self.vector_db = ChromaClient()

    def retrieve(
        self,
        query: str,
        topic_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.
        """

        # Step 1: Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)

        # Step 2: Perform vector search
        results = self.vector_db.similarity_search(
            query_embedding=query_embedding,
            top_k=self.top_k,
            topic_filter=topic_filter
        )

        # Step 3: Format results
        documents = self._format_results(results)
        documents = sorted(documents, key=lambda x: x["score"])

        return documents[:5]

        # return documents

    # def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
    #     """
    #     Convert raw Chroma results into structured documents.
    #     """

    #     formatted_docs = []

    #     docs = results.get("documents", [[]])[0]
    #     metas = results.get("metadatas", [[]])[0]
    #     ids = results.get("ids", [[]])[0]

    #     for i in range(len(docs)):
    #         formatted_docs.append(
    #             {
    #                 "id": ids[i],
    #                 "text": docs[i],
    #                 "metadata": metas[i]
    #             }
    #         )

    #     return formatted_docs
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:

        formatted_docs = []

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i in range(len(docs)):
            text = docs[i]
            metadata = metas[i]
            doc_id = ids[i]
            score = distances[i] if distances else 1.0

            # VERY LENIENT filter (important)
            if score > 0.8:
                continue

            formatted_docs.append({
                "id": doc_id,
                "text": text,
                "metadata": metadata,
                "score": score
            })

        return formatted_docs
        