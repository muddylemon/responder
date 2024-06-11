
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from constants import CHROMA_SETTINGS


from models import LLAMA3
model = LLAMA3

embeddings_model_name = "all-MiniLM-L6-v2"
persist_directory = "db"


def search(query: str) -> list[dict]:
    """
    Search for the answer to a question in the database
    :param query: the question to search for
    :return: a list of documents related to the query
    """
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    db = Chroma(persist_directory=persist_directory,
                embedding_function=embeddings)

    retriever = db.as_retriever(search_type="mmr", search_kwargs={
                                'k': 10, 'fetch_k': 50})

    docs = retriever.invoke(query)
    if not docs:
        return "No documents found", []

    return docs
