from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from app.config.settings import settings

embed_fn = SentenceTransformerEmbeddings(model_name=settings.kb_model_name)
db = Chroma(persist_directory=str(settings.chroma_dir), embedding_function=embed_fn)

print("📚 Total entries:", db._collection.count())

docs = db.get(limit=5)
for i, d in enumerate(docs["documents"]):
    print(f"\n--- Document {i+1} ---")
    print("Content:", d[:250], "...")
    print("Metadata:", docs["metadatas"][i])
