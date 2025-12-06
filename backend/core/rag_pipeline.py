from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_chroma import Chroma
from ..models.prompts import chat_prompt
from ..models.llm import get_llm
from dotenv import load_dotenv
from pathlib import Path
import os


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PERSIST_DIR = str(BASE_DIR / "vectorstore")

# Load vector store
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

vector_store = Chroma(
    collection_name="support_docs",
    embedding_function=embeddings,
    persist_directory=PERSIST_DIR
)

retriever = vector_store.as_retriever(search_kwargs={"k":6})

prompt = chat_prompt

model = get_llm()

parser = StrOutputParser()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "context": RunnableLambda(lambda x: retriever.invoke(x["question"])) | RunnableLambda(format_docs),
        "question": RunnableLambda(lambda x: x["question"])
    }
    | prompt
    | model
    | parser
)

async def run_rag(query: str):
    return await rag_chain.ainvoke({"question": query})

# def run_rag(query: str):
#     return rag_chain.invoke({"question": query})


if __name__=="__main__":
    query = "How to upgrade ram in my asus strix laptop?"
    result = run_rag(query=query)
    print(result)