from docchat import MyGPT4ALL
from knowledgebase import PDFKnowledgeBase
from knowledgebase import(DOCUMENT_SOURCE_DIRECTORY)
from langchain.chains import RetrievalQA
from langchain.embeddings import GPT4AllEmbeddings

GPT4ALL_MODEL_NAME='wizardlm-13b-v1.1-superhot-8k.ggmlv3.q4_0.bin'
GPT4ALL_MODEL_FOLDER_PATH='./llm_model/'
GPT4ALL_BACKEND='llama'
GPT4ALL_ALLOW_STREAMING=True
GPT4ALL_ALLOW_DOWNLOAD=False

llm = MyGPT4ALL(
    model_folder_path=GPT4ALL_MODEL_FOLDER_PATH,
    model_name=GPT4ALL_MODEL_NAME,
    allow_streaming=True,
    allow_download=False
)

embeddings = GPT4AllEmbeddings()

kb = PDFKnowledgeBase(
    pdf_source_folder_path=DOCUMENT_SOURCE_DIRECTORY
)

retriever = kb.return_retriever_from_persistant_vector_db(embedder=embeddings)

qa_chain = RetrievalQA.from_chain_type(
    llm = llm,
    chain_type='stuff',
    retriever=retriever,
    return_source_documents=True, verbose=True
)


while True:
    query = input("What's on your mind: ")
    if query == 'exit':
        break
    result = qa_chain(query)
    answer, docs = result['result'], result['source_documents']

    print(answer)

    print("#"* 30, "Sources", "#"* 30)
    for document in docs:
        print("\n> SOURCE: " + document.metadata["source"] + ":")
        print(document.page_content)
    print("#"* 30, "Sources", "#"* 30)



