from knowledgebase import PDFKnowledgeBase
from knowledgebase import (DOCUMENT_SOURCE_DIRECTORY)

kb = PDFKnowledgeBase(pdf_source_folder_path=DOCUMENT_SOURCE_DIRECTORY)

kb.initiate_document_injetion_pipeline()


