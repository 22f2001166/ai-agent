import os
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.base import Embeddings
from embed import get_embedding
import fitz


class TitanEmbedding(Embeddings):
    def embed_documents(self, texts):
        return [get_embedding(text) for text in texts]

    def embed_query(self, text):
        return get_embedding(text)


def load_documents(folder_path="data/policies"):
    docs = []
    for fname in os.listdir(folder_path):
        if fname.endswith(".pdf"):
            path = os.path.join(folder_path, fname)
            text = ""
            with fitz.open(path) as pdf:
                for page in pdf:
                    text += page.get_text()
            docs.append(Document(page_content=text, metadata={"source": fname}))
    return docs


def build_vector_index():
    docs = load_documents()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    vectorstore = FAISS.from_documents(chunks, embedding=TitanEmbedding())
    vectorstore.save_local("vectorstore")
    print("Vectorstore built and saved.")


def load_vector_index():
    return FAISS.load_local(
        "vectorstore", TitanEmbedding(), allow_dangerous_deserialization=True
    )
