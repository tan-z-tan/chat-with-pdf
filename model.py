from llama_index.indices.base import BaseGPTIndex
from llama_index import GPTSimpleVectorIndex, LLMPredictor, ServiceContext
from llama_index import download_loader
from langchain.chat_models import ChatOpenAI


def create_index(pdf_path: str) -> BaseGPTIndex:
    """Process the uploaded PDF file and return the text."""

    documents = _fetch_documents(pdf_path)
    print(documents)
    index = _create_index(documents)
    return index


def load_index(index_path: str) -> BaseGPTIndex:
    """Load the index from the JSON file."""
    index = GPTSimpleVectorIndex.load_from_disk(index_path)
    return index


def run_query(index: BaseGPTIndex, query, top_k):
    return index.query(query, service_context=_get_service_context(), similarity_top_k=top_k)


def _get_service_context():
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor)
    return service_context


def _fetch_documents(pdf_path: str):
    """Fetch the documents from the PDF file."""
    CJKPDFReader = download_loader("CJKPDFReader")
    loader = CJKPDFReader()
    return loader.load_data(file=pdf_path)


def _create_index(documents):
    index = GPTSimpleVectorIndex.from_documents(documents, service_context=_get_service_context())
    return index
