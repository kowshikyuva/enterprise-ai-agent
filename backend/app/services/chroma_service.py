import chromadb
import uuid

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="research_documents"
)


def add_document(title, url, content):

    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[content],
        metadatas=[{
            "title": title,
            "url": url
        }]
    )