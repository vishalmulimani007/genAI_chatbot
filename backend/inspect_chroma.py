import os
from dotenv import load_dotenv
from config_loader import ConfigLoader
import chromadb

load_dotenv()


def inspect_chroma():
    """
    Inspect first 10 records from Chroma Cloud collection
    """

    # Load config
    config_loader = ConfigLoader()
    vector_config = config_loader.get_section("vector_db")

    collection_name = vector_config["collection_name"]

    # Load env variables
    api_key = os.getenv("CHROMA_API_KEY")
    tenant = os.getenv("CHROMA_TENANT")
    database = os.getenv("CHROMA_DATABASE")

    if not api_key or not tenant or not database:
        raise ValueError("Missing Chroma Cloud environment variables")

    # Connect to Chroma Cloud
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database=database
    )

    print("✅ Connected to Chroma Cloud")

    collection = client.get_or_create_collection(name=collection_name)

    print(f"📦 Using collection: {collection_name}")

    # Fetch first 10 records
    results = collection.get(
        limit=10,
        include=["documents", "metadatas", "embeddings"]
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    embeddings = results.get("embeddings", [])
    ids = results.get("ids", [])

    print("\n========== FIRST 10 RECORDS ==========\n")

    for i in range(len(documents)):
        print(f"🔹 RECORD {i+1}")
        print("-" * 50)

        # ID
        print("ID:", ids[i])

        # TEXT
        print("\nTEXT:")
        print(documents[i][:500])  # truncate

        # METADATA
        print("\nMETADATA:")
        print(metadatas[i])

        # EMBEDDING DIM
        if embeddings is not None and len(embeddings) > i:
            print("\nEMBEDDING DIM:", len(embeddings[i]))

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    inspect_chroma()