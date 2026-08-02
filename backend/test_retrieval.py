from app.services.chroma_service import collection

query = "How is AI used in banking?"

results = collection.query(
    query_texts=[query],
    n_results=3
)

print("Query:", query)
print()

for i, doc in enumerate(results["documents"][0]):
    print("=" * 60)
    print(f"Result {i+1}")
    print(doc[:700])