from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from dotenv import load_dotenv
from pathlib import Path
from uuid import uuid4


load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

BASE_DIR = Path(__file__).resolve().parent.parent
PERSIST_DIR = str(BASE_DIR / "vectorstore")
DOCUMENTS_DIR = str(BASE_DIR / "data" / "documents")

# Ensure whether directories exist or not
Path(PERSIST_DIR).mkdir(parents=True, exist_ok=True)
Path(DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)


def ingest_documents(file_path: Path):
    print(f"\nLoading {file_path.name} ...")
    
    # Load pdf
    loader = PyPDFLoader(str(file_path))
    docs = loader.load()
    
    # Split into chunks
    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(docs)
    
    # Store in Chroma
    vector_store = Chroma(
        collection_name="support_docs",
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR
    )
    ids = [f"{file_path.stem}_{uuid4()}" for _ in range(len(chunks))]
    vector_store.add_documents(documents=chunks, ids=ids)
    print(f"Ingested {file_path.name} successfully.")
    
    
    
if __name__=="__main__":
    for file in Path(DOCUMENTS_DIR).glob("*.pdf"):
        ingest_documents(file)