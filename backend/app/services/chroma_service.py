from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import chromadb
import uuid

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="research_documents"
)

# On its very first .add() call, Chroma's default embedding function
# downloads a small model from Hugging Face. If that network path is slow
# or blocked, it hangs with no error and no log output. This timeout turns
# that into a visible, recoverable failure instead.
CHROMA_TIMEOUT_SECONDS = 30

_executor = ThreadPoolExecutor(max_workers=4)


def document_exists(url: str) -> bool:
    existing = collection.get(where={"url": url}, limit=1)
    return bool(existing.get("ids"))


def _raw_add(title, url, content):
    collection.add(
        ids=[str(uuid.uuid4())],
        documents=[content],
        metadatas=[{
            "title": title,
            "url": url
        }]
    )


def add_document(title, url, content):
    # Avoid re-embedding the same source when it's reused across questions/projects.
    if document_exists(url):
        return

    print(f"Embedding + storing in ChromaDB: {title[:60]!r}...")
    try:
        future = _executor.submit(_raw_add, title, url, content)
        future.result(timeout=CHROMA_TIMEOUT_SECONDS)
        print("Chroma store finished.")
    except FutureTimeoutError:
        print(f"Chroma embedding timed out after {CHROMA_TIMEOUT_SECONDS}s "
              f"(likely the embedding model download stalled) - skipping vector store for this source.")
    except Exception as e:
        print(f"Chroma store failed: {e} - skipping vector store for this source.")