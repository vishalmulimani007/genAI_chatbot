import os
from typing import List, Dict, Any

import chromadb
from config_loader import ConfigLoader


class ChromaClient:
    """
    Handles connection and operations with Chroma Cloud.

    Initialization flow:
    1. Read Chroma Cloud credentials from environment variables
    2. Connect to Chroma Cloud
    3. Connect or create the configured collection
    """

    def __init__(self):
        config_loader = ConfigLoader()
        vector_config = config_loader.get_section("vector_db")

        self.collection_name = vector_config["collection_name"]

        # Read environment variables
        api_key = os.getenv("CHROMA_API_KEY")
        tenant = os.getenv("CHROMA_TENANT")
        database = os.getenv("CHROMA_DATABASE")

        if not api_key:
            raise ValueError("CHROMA_API_KEY environment variable not set")

        if not tenant:
            raise ValueError("CHROMA_TENANT environment variable not set")

        if not database:
            raise ValueError("CHROMA_DATABASE environment variable not set")

        # Connect to Chroma Cloud
        self.client = chromadb.CloudClient(
            api_key=api_key,
            tenant=tenant,
            database=database
        )

        print("Connected to Chroma Cloud")

        # Connect or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name
        )

        print(f"Using collection: {self.collection_name}")

    def add_documents(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """
        Insert documents into Chroma collection.
        Used during ingestion.
        """

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int,
        topic_filter: str = None
    ) -> Dict[str, Any]:
        """
        Perform vector similarity search with optional topic filter.
        """

        where_clause = None

        if topic_filter:
            where_clause = {"topic": topic_filter}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause
        )

        return results

    def count_documents(self) -> int:
        """
        Return the number of documents stored in the collection.
        """

        return self.collection.count()