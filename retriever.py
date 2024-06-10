
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
embeddings_model_name = "all-MiniLM-L6-v2"
persist_directory = "db"
target_source_chunks = 12


def search(query: str, hide_source: bool = False, mute_stream: bool = False) -> tuple[str, list[dict]]:
    """
    Search for the answer to a question in the database
    :param query: the question to search for
    :param hide_source: whether to hide the source documents
    :param mute_stream: whether to mute the streaming output
    """
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    db = Chroma(persist_directory=persist_directory,
                embedding_function=embeddings)

    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    # activate/deactivate the streaming StdOut callback for LLMs
    callbacks = [] if mute_stream else [StreamingStdOutCallbackHandler()]

    llm = Ollama(model=model, callbacks=callbacks)

    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=not hide_source)

    res = qa(query)
    answer, docs = res['result'], [
    ] if hide_source else res['source_documents']

    return answer, docs
