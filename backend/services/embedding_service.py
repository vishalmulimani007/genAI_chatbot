from typing import List

from sentence_transformers import SentenceTransformer

from config_loader import ConfigLoader


class EmbeddingService:
    """
    Handles text embedding generation using Sentence Transformers.

    Used for:
    - Document embeddings during ingestion
    - Query embeddings during retrieval
    """

    def __init__(self):
        config_loader = ConfigLoader()
        embedding_config = config_loader.get_section("embeddings")
        vector_config = config_loader.get_section("vector_db")

        self.model_name = embedding_config["model"]
        self.device = embedding_config.get("device", "cpu")
        self.expected_dimension = vector_config["embedding_dimension"]

        self.model = SentenceTransformer(self.model_name, device=self.device)

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.
        """

        embedding = self.model.encode(query)

        self._validate_dimension(embedding)

        return embedding.tolist()

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        Used during ingestion.
        """

        embeddings = self.model.encode(documents)

        for emb in embeddings:
            self._validate_dimension(emb)

        return [emb.tolist() for emb in embeddings]

    def _validate_dimension(self, embedding):
        """
        Ensure embedding dimension matches config.
        Prevents vector DB mismatch errors.
        """

        if len(embedding) != self.expected_dimension:
            raise ValueError(
                f"Embedding dimension mismatch. "
                f"Expected {self.expected_dimension}, "
                f"got {len(embedding)}"
            )