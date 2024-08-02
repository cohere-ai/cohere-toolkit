# ../src/main.py

import os
import uuid
import json
import cohere
import pickle

from typing import Any
from joblib import Parallel, delayed
from langchain_cohere import CohereEmbeddings
from langchain_core.documents import Document
from langchain_core.stores import InMemoryStore
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain.retrievers import MultiVectorRetriever
from unstructured.partition.pdf import partition_pdf

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from typing import Any


class Element(BaseModel):
    type: str
    text: Any

# Constants
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
CHAT_MODEL = "command-r-plus"
EMBED_MODEL = "embed-english-v3.0"
RERANK_MODEL = "rerank-english-v3.0"

PDF_PATH = "src/backend/data/bdc/apple-10k.pdf"


co = cohere.Client(
    api_key=COHERE_API_KEY
)


# Parsing
raw_pdf_elements = partition_pdf(
    filename=PDF_PATH,
    extract_images_in_pdf=False,
    infer_table_structure=True,
    chunking_strategy="by_title",
    max_characters=4000,
    new_after_n_chars=3800,
    combine_text_under_n_chars=2000,
    image_output_dir_path="."
)

def categorize_by_type(raw_pdf_elements: list, persist: bool=True) -> tuple[list, list]:
    all_elements = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            all_elements.append(
                Element(type="table", text=str(element))
            )
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            all_elements.append(
                Element(type="text", text=str(element))
            )
    # Separate into lists
    table_elements = [e for e in all_elements if e.type == "table"]
    text_elements = [e for e in all_elements if e.type == "text"]
    print(f"tables: {len(table_elements)}\ntexts: {len(text_elements)}")

    if persist:
        with open("src/backend/data/bdc/tables.pkl", "wb") as f:
            pickle.dump(table_elements, f)
        with open("src/backend/data/bdc/texts.pkl", "wb") as f:
            pickle.dump(text_elements, f)

    return table_elements, text_elements


def get_chat_outputs(
    prompts: list[str],
    preamble: str,
    chat_history: list=None,
    model: str=CHAT_MODEL,
    temperature: float=0.1,
    documents: any=None
) -> list[str]:
    responses = []
    for i, prompt in enumerate(prompts):
        print(f"counter: {i}")
        responses.append(
            co.chat(
                message=prompt,
                preamble=preamble,
                chat_history=chat_history,
                documents=documents,
                model=model,
                temperature=temperature
            ).text
        )
    print("complete")
    return responses

# def parallel_proc_chat(
#     prompts: list,
#     preamble: str,
#     chat_history: list=None,
#     model: str=CHAT_MODEL,
#     temperature: float=0.1,
#     n_jobs: int=10): 
#     responses = Parallel(n_jobs=n_jobs, prefer="threads")(delayed(get_chat_output)(prompt,preamble,chat_history,model,temperature) for prompt in prompts)
#     # responses = Parallel(n_jobs=n_jobs, prefer="threads")(
#     #     delayed(get_chat_output)(
#     #         prompt, preamble, chat_history, model, temperature
#     #     )
#     #     for prompt in prompts
#     # )
#     return responses


def rerank(query: str, documents: list, model: str=RERANK_MODEL, top_n: int=3) -> list[str]:
    response = co.rerank(
        query=query,
        documents=documents,
        top_n=top_n,
        model=model,
        return_documents=True
    )
    top_chunks_after_reranking = [result.document.text for result in response.results]
    return top_chunks_after_reranking


def generate_vectorstore(
    prompt_text: str,
    table_elements: list,
    text_elements: list
) -> MultiVectorRetriever:
    table_prompts = [prompt_text.format(element=element.text) for element in table_elements]
    table_summaries = get_chat_outputs(table_prompts, None)
    text_prompts = [prompt_text.format(element=element.text) for element in text_elements]
    text_summaries = get_chat_outputs(text_prompts, None)

    # Persist table and text summaries
    with open("src/backend/data/bdc/table_summaries.pkl", "wb") as f:
        pickle.dump(table_summaries, f)
    with open("src/backend/data/bdc/text_summaries.pkl", "wb") as f:
        pickle.dump(text_summaries, f)

    # # load table and text summaries
    # with open("data/table_summaries.pkl", "rb") as f:
    #     table_summaries = pickle.load(f)
    # with open("data/text_summaries.pkl", "rb") as f:
    #     text_summaries = pickle.load(f)

    tables = [element.text for element in table_elements]
    texts = [element.text for element in text_elements]

    # Setup vectorstore
    vectorstore = Chroma(
        collection_name="summaries", 
        embedding_function=CohereEmbeddings(cohere_api_key=COHERE_API_KEY, model=EMBED_MODEL)
    )
    store = InMemoryStore()
    id_key = "doc_id"

    retriever = MultiVectorRetriever(
        vectorstore=vectorstore,
        docstore=store,
        id_key=id_key
    )

    # Store tables
    table_ids = [str(uuid.uuid4()) for _ in tables]
    docs_tables = [
        Document(page_content=s, metadata={id_key: table_ids[i]})
        for i, s in enumerate(table_summaries)
    ]
    retriever.vectorstore.add_documents(docs_tables)
    retriever.docstore.mset(list(zip(table_ids, tables)))

    # Store texts
    doc_ids = [str(uuid.uuid4()) for _ in texts]
    docs_texts = [
        Document(page_content=s, metadata={id_key: doc_ids[i]})
        for i, s in enumerate(text_summaries)
    ]
    retriever.vectorstore.add_documents(docs_texts)
    retriever.docstore.mset(list(zip(doc_ids, texts)))

    return retriever


def generate(query: str, retriever: MultiVectorRetriever) -> tuple:
    search_query = co.chat(message=query, model=CHAT_MODEL, temperature=0.2, search_queries_only=True)

    reranked_docs = []
    for sq in search_query.search_queries:
        docs = retriever.invoke(sq.text)
        _reranked_docs = rerank(sq.text, docs)
        reranked_docs.extend(_reranked_docs)

    documents = [
        {
            "title": f"chunk {i}",
            "text": reranked_docs[i],
            "url": "https://d18rn0p25nwr6d.cloudfront.net/CIK-0000320193/ee662306-a551-4192-91d8-e9931452076e.pdf"
        }
        for i in range(len(reranked_docs))
    ]

    preamble = \
"""
## Task & Context
You help people answer their questions and other requests interactively. You will be asked a very wide array of requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to help you, which you use to research your answer. You should focus on serving the user's needs as best you can, which will be wide-ranging.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and spelling.
"""
    response = co.chat(
      message=query,
      documents=documents,
      preamble=preamble,
      model=CHAT_MODEL,
      temperature=0.3
    )

    return response.text, documents


if __name__ == "__main__":

    # Generate table and text summaries
    prompt_text = \
    """
    ## Purpose
    You are an assistant tasked with summarizing tables and text.

    ## Task
    Give a concise summary of the content in the table or text Only provide the summary and no other text.

    ## Content in Table or Text
    {element}
    """

    table_elements, text_elements = categorize_by_type(raw_pdf_elements=raw_pdf_elements)

    # Load element lists
    try:
        with open("src/backend/data/bdc/tables.pkl", "rb") as f:
            table_elements = pickle.load(f)
    except:
        raise FileNotFoundError("Tables file not found")
    try:
        with open("src/backend/data/bdc/texts.pkl", "rb") as f:
            text_elements = pickle.load(f)
    except:
        raise FileNotFoundError("Texts file not found")

    retriever = generate_vectorstore(prompt_text, table_elements, text_elements)

    query = "Does the document have anything on share repurchases"

    response, docs = generate(query, retriever)
    
    print("RESPONSE:")
    print(response)

    print("DOCS:")
    for doc in docs:
        print(doc)