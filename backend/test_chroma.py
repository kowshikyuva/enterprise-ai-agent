from app.services.chroma_service import collection

collection.add(
    ids=["1"],
    documents=["Artificial Intelligence is transforming healthcare."],
    metadatas=[{"title": "Test"}]
)

print(collection.count())