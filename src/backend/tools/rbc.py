import os
import requests
from typing import Any, Dict, List

import pandas as pd
from langchain_cohere import CohereEmbeddings, CohereRerank
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader

from dotenv import load_dotenv
load_dotenv()

from backend.chat.collate import RELEVANCE_THRESHOLD
from backend.tools.base import BaseTool


class RBCDataAnalyzer(BaseTool):
    """
    This class retrieves data about vacations and other relevant information
    """

    NAME = "rbc_hr_data"
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    FILEPATH = "src/backend/data/rbc/rbc-hr-data.csv"
    DATAPATH = "src/backend/data/rbc/hr_data_index"
    URL = "https://docs.google.com/spreadsheets/d/1g11gAq9ZA_kiHz-VICbn3d9_HkuzCry9apoIomFMYaU/edit?usp=sharing"
    TOP_K = 10

    REQUEST_PROMPT = \
"""Type of request based on the user query to determine the scope to retrieve HR data by, either through a name of the employee or a role of that employee. This can be one of the following: search-by-role or search-by-name or misc.
A 'search-by-role' request is called when the user wants generic information about a role, including total vacation and sick leave days for that role, the accural rates of vacation for that role, etc.
A 'search-by-name' request is called when the user wants specific information about a specific employee, including their used vacation and sick leaves, total accrued vacation, approvers, and any upcomming vacation.
A 'misc' request is called when the user query does not relate to either a 'search-by-role' or a 'search-by-name' request. This is for all other general or specific analysis requests about the HR data."""
    ROLE_PROMPT = "Title of employee if identified in the query. This can ONLY be one of the following: senior manager, manager, staff"

    def __init__(self) -> None:
        self.df = pd.read_csv(self.FILEPATH)
        self.df["name"] = self.df["name"].str.lower()
        self.df["role"] = self.df["role"].str.lower()
        self.embed = CohereEmbeddings(
            cohere_api_key=self.COHERE_API_KEY,
            model="embed-english-v3.0",
        )
        self.retriever = self._load_db().as_retriever(search_kwargs={"k": self.TOP_K})

    @classmethod
    def is_available(cls) -> bool:
        return cls.COHERE_API_KEY is not None and os.path.isfile(cls.FILEPATH)
    
    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        request = parameters.get("request", "")
        request = request.lower()
        print(request)
        name = parameters.get("name", "neel")
        try:
            name = name.lower()
        except:
            name = "neel"
        role = parameters.get("role", "")
        try:
            role = role.lower()
        except:
            role = ""
        
        match request:
            case "search-by-role":
                if role != "":
                    response = self._get_info_role(role)
                else:
                    response = [{"text": "Invalid role. Please provide an accurate role."}]
            case "search-by-name":
                response = self._get_info_name(name)
            case "misc":
                loader = CSVLoader(file_path="src/backend/data/rbc/rbc-hr-data.csv")
                data = loader.load()
                response = []
                for doc in data:
                    response.append(
                        {
                            "text": doc.page_content,
                            "url": self.URL
                        }
                    )
            case _:
                response = [{"text": "Invalid request. Please rephrase and try again."}]
        return response
    
    def _load_db(self) -> list[dict]:
        try:
            db = FAISS.load_local(
                self.DATAPATH,
                self.embed,
                allow_dangerous_deserialization=True,
            )
        except:
            raise FileNotFoundError("No FAISS vectorstore found")
        return db
    
    def _get_info_name(self, name: str) -> list[dict]:
        response = []
        try:
            record = self.df.loc[self.df["name"] == name].iloc[0].to_dict()
        except Exception as e:
            return [
                {"text": "Error, database has no record of this name."}
            ]
        # role
        response.append({
            "text": f"This information is for {record['role'].capitalize()}-level employee {record['full_name']} (Employee ID: {record['employee_id']})",
            "url": self.URL,
        })
        # total used vacation days
        response.append({
            "text": f"Employee {record['full_name']} has used {record['vacation_days_used']} days of vacation",
            "url": self.URL,
        })
        # total used sick leave days
        response.append({
            "text": f"Employee {record['full_name']} has used {record['sick_days_used']} days of sick leave",
            "url": self.URL,
        })
        # total accrued vacation days
        response.append({
            "text": f"Employee {record['full_name']} has accured a total of {record['vacation_days_accrued_year']} days to date in the current fiscal year",
            "url": self.URL,
        })
        # upcoming time_off_date
        if record['upcoming_time_off_days'] == 0:
            response.append({"text": f"Employee {record['full_name']} has no upcomming leave planned in this fiscal year"})
        else:
            response.append({
                "text": f"Employee {record['full_name']} is planning to take off {record['upcoming_time_off_days']} days of vacation starting on {record['upcoming_time_off_date']}",
                "url": self.URL,
            })
        # vacation approval
        response.append({
            "text": f"Employee {record['full_name']}'s vacation is approved by {record['manager']}"
        })
        return response
    
    def _get_info_role(self, role: str) -> list[dict]:
        response = []
        try:
            record = self.df.loc[self.df["role"] == role].iloc[0].to_dict()
        except Exception as e:
            return [
                {"text": "Error, database has no record of this role."}
            ]
        # role
        response.append({
            "text": f"This information is for the role {record['role'].capitalize()}.",
            "url": self.URL,
        })
        # total vacation days
        response.append({
            "text": f"Total vacation days alloted to a {record['role'].capitalize()} is {record['vacation_days_total']} per fiscal year",
            "url": self.URL,
        })
        # total sick days
        response.append({
            "text": f"Total sick days alloted to a {record['role'].capitalize()} is {record['sick_days_total']} per fiscal year",
            "url": self.URL,
        })
        # accural rate
        response.append({
            "text": f"The vacation accural rate for a {record['role'].capitalize()} is {record['accural_rate']} days per month",
            "url": self.URL,
        })
        return response
    

class RBCDocumentRetriever(BaseTool):
    """
    This class retrieves documentation from example documents portals about organizational and operation information
    """

    NAME = "rbc_hr_document"
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    FILEPATH = "src/backend/data/rbc/hr_doc_index"

    # search parameters
    TOP_K = 15

    def __init__(self):
        # load cohere models
        self.embed = CohereEmbeddings(
            cohere_api_key=self.COHERE_API_KEY,
            model="embed-english-v3.0",
        )
        self.retriever = self._load_db().as_retriever(search_kwargs={"k": self.TOP_K})

    @classmethod
    def is_available(cls) -> bool:
        return cls.COHERE_API_KEY is not None and os.path.isdir(cls.FILEPATH)
    
    async def call(self, parameters: dict, **kwargs: Any) -> List[Dict[str, Any]]:
        query = parameters.get("query", "")

        # retrieve documents
        _docs = self.retriever.invoke(query, input_type="search_query")
        # transform Document objs into dict w/ metadata for rerank
        docs = []
        for doc in _docs:
            docs.append(
                {
                    "title": doc.metadata.get("title", ""),
                    "text": doc.page_content,
                    "author": "RBC HR",
                    "url": doc.metadata.get("source", "")
                }
            )
        print(len(docs))

        # # rerank TOP_N documents
        # if self.USE_RERANK:
        #     ranked_results = []
        #     results = self.rerank.rerank(
        #         query=query,
        #         documents=docs,
        #         rank_fields=["text", "title", "author"],
        #         top_n=self.TOP_N
        #     )
        #     for res in results:
        #         print(res)
        #         idx = res['index']
        #         relevance_score = res['relevance_score']

        #         if relevance_score >= RELEVANCE_THRESHOLD:
        #             doc = docs[idx]
        #             ranked_results.append(
        #                 doc
        #             )
        #     print(len(ranked_results))
        #     # return ranked results
        #     if len(ranked_results) < 1:
        #         return [{"text": "No information found, please reach out to RBC HR at hr@rbc.ca"}]
        #     print(ranked_results)
        #     return ranked_results
    
        # return non-ranked results
        if len(docs) < 1:
            return [{"text": "No information found, please reach out to RBC HR at hr@rbc.ca"}]
        return docs

    def _load_db(self) -> FAISS:
        try:
            db = FAISS.load_local(
                self.FILEPATH,
                self.embed,
                allow_dangerous_deserialization=True,
            )
        except:
            raise FileNotFoundError("No FAISS vectorstore found")
        return db
    

if __name__ == "__main__":
    # loader = CSVLoader(file_path="src/backend/data/rbc/rbc-hr-data.csv")
    # data = loader.load()
    # folder = "src/backend/data/rbc"

    # db = FAISS.from_documents(
    #     data,
    #     CohereEmbeddings(cohere_api_key=os.getenv("COHERE_API_KEY"), model="embed-english-v3.0")
    # )

    # db.save_local("src/backend/data/rbc/hr_data_index")

    # URLs of the PDFs to be downloaded

    pdf_urls = [
        "https://docs.google.com/document/d/1EHVDP6Cddrm_S8DU80iVRJX-iuWvQdd3pgSf2YCt_LU/edit",
        "https://docs.google.com/document/d/1Xg1Ve88xBKNZPCK43xHl7NzTfqNrD2mJQ6ahCKLLCQE/edit",
    ]

    # Directory to save the downloaded PDFs
    download_directory = "src/backend/data/rbc"
    docs = []
    folder = "src/backend/data/rbc"
    files = [file for file in os.listdir("src/backend/data/rbc") if file.endswith(".pdf")]
    print(files)
    for file, url in zip(files, pdf_urls):
        file = os.path.join("src/backend/data/rbc", file)
        loader = PyMuPDFLoader(file)
        _docs = loader.load()
        for doc in _docs:
            doc.metadata['source'] = url
        docs.extend(_docs)

    print(docs[0])
    print(len(docs))

    db = FAISS.from_documents(
        docs,
        CohereEmbeddings(cohere_api_key=os.getenv("COHERE_API_KEY"), model="embed-english-v3.0")
    )

    db.save_local("src/backend/data/rbc/hr_doc_index")
