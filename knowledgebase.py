import os
from typing import Optional
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import GPT4AllEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHROMA_DB_DIRECTORY = 'db'
TARGET_SOURCE_CHUNKS=4
DOCUMENT_SOURCE_DIRECTORY='data'
CHUNK_SIZE=500
CHUNK_OVERLAP=50
HIDE_SOURCE_DOCUMENTS=False

settings = Settings(
    chroma_db_impl='duckdb+parquet',
    persist_directory=CHROMA_DB_DIRECTORY,
    anonymized_telemetry=False
)

class PDFKnowledgeBase:
    def __init__(self, pdf_source_folder_path: str) -> None:
        """
        Loads pdf and creates a Knowledge base using the Chroma
        vector DB.
        Args:
            pdf_source_folder_path (str): The source folder containing 
            all the pdf documents
        """
        self.pdf_source_folder_path = pdf_source_folder_path

    def load_pdfs(self):
        loader = DirectoryLoader(
        self.pdf_source_folder_path
        )
        loaded_pdfs = loader.load()
        return loaded_pdfs

    def split_documents(self, loaded_docs, chunk_size: Optional[int] = 500,chunk_overlap: Optional[int] = 20 ):
        splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        )
        chunked_docs = splitter.split_documents(loaded_docs)
        return chunked_docs
    
    def convert_document_to_embeddings(
        self, chunked_docs, embedder):
    
        persistent_client = chromadb.PersistentClient(path=CHROMA_DB_DIRECTORY)
        vector_db = Chroma(persist_directory=CHROMA_DB_DIRECTORY,
                        embedding_function=embedder,
                        client=persistent_client
                        )
        
        vector_db.add_documents(chunked_docs)
        vector_db.persist()
        return vector_db   
        

    def return_retriever_from_persistant_vector_db(
        self, embedder
    ):  
        if not os.path.isdir(CHROMA_DB_DIRECTORY):
            raise NotADirectoryError(
            "Please load your vector database first."
        )
        # return a retriever object which will retrieve the 
        # relevant chunks 
        persistent_client = chromadb.PersistentClient(path=CHROMA_DB_DIRECTORY)
        vector_db = Chroma(persist_directory=CHROMA_DB_DIRECTORY,
                        embedding_function=embedder,
                        client=persistent_client
                        )
        
        
    
        return vector_db.as_retriever(
        search_kwargs={"k": TARGET_SOURCE_CHUNKS}
    )

    def initiate_document_injetion_pipeline(self):
        loaded_pdfs = self.load_pdfs()
        chunked_documents = self.split_documents(loaded_docs=loaded_pdfs)
        
        print("=> PDF loading and chunking done.")
        print(len(chunked_documents))

        embeddings = GPT4AllEmbeddings()
        vector_db = self.convert_document_to_embeddings(
            chunked_docs=chunked_documents, embedder=embeddings
        )
        print(vector_db._collection.count())

        print("=> vector db initialised and created.")
        print("All done")