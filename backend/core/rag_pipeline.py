from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_chroma import Chroma
from ..models.prompts import chat_prompt
from ..models.llm import get_llm
from dotenv import load_dotenv
from pathlib import Path
import os


load_dotenv()


# Load vector store
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)


async def run_rag_stream(question: str, vectorstore_path: str):
    vector_store = Chroma(
        embedding_function=embeddings,
        persist_directory=vectorstore_path
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

    async for chunk in rag_chain.astream({"question": question}):
        yield chunk
