
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from constants import CHROMA_SETTINGS


from models import LLAMA3
model = LLAMA3

# https://www.sbert.net/docs/pretrained_models.html

# all-mpnet-base-v2  slower/better quality
embeddings_model_name = "all-mpnet-base-v2"
persist_directory = "db"
target_source_chunks = 24


def search(query: str, hide_source: bool = False, mute_stream: bool = False) -> list[dict]:
    """
    Search for the answer to a question in the database
    :param query: the question to search for
    :param hide_source: whether to hide the source documents
    :param mute_stream: whether to mute the streaming output
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
