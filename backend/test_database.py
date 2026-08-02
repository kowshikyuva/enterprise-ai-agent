from app.database.database import SessionLocal
from app.services.storage_service import save_source

db = SessionLocal()

source = save_source(
    db,
    "Test Article",
    "https://example.com",
    "This is a sample article."
)

print(source.id)
print(source.title)