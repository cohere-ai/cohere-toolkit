from itertools import zip_longest
from typing import Any, Dict, List

from backend.chat.custom.model_deployments.base import BaseDeployment


def combine_documents(
    documents: Dict[str, List[Dict[str, Any]]],
    model: BaseDeployment,
) -> List[Dict[str, Any]]:
    """
    Combines documents from different retrievers and reranks them.

    Args:
        documents (Dict[str, List[Dict[str, Any]]]): Dictionary from queries of lists of documents.
        model (BaseDeployment): Model deployment.

    Returns:
        List[Dict[str, Any]]: List of combined documents.
    """
    reranked_documents = rerank(documents, model)
    return interleave(reranked_documents)


def rerank(
    documents_by_query: Dict[str, List[Dict[str, Any]]], model: BaseDeployment
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Takes a dictionary from queries of lists of documents and
    internally rerank the documents for each query e.g:
    [{"q1":[1, 2, 3],"q2": [4, 5, 6]] -> [{"q1":[2 , 3, 1],"q2": [4, 6, 5]]

    Args:
        documents_by_query (Dict[str, List[Dict[str, Any]]]): Dictionary from queries of lists of documents.
        model (BaseDeployment): Model deployment.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary from queries of lists of reranked documents.
    """
    # If rerank is not enabled return documents as is:
    if not model.rerank_enabled:
        return documents_by_query

    # rerank the documents by each query
    all_rerank_docs = {}
    for query, documents in documents_by_query.items():
        # Only rerank on text of document
        # TODO handle no text in document
        docs_to_rerank = [doc["text"] for doc in documents]

        # If no documents to rerank, continue to the next query
        if not docs_to_rerank:
            continue

        res = model.invoke_rerank(query=query, documents=docs_to_rerank)
        # Sort the results by relevance score
        res.results.sort(key=lambda x: x.relevance_score, reverse=True)
        # Map the results back to the original documents
        all_rerank_docs[query] = [documents[r.index] for r in res.results]

    return all_rerank_docs


def interleave(documents: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Takes a dictionary from queries of lists of documents and interleaves them
    for example [{"q1":[1, 2, 3],"q2": [4, 5, 6]] -> [1, 4, 2, 5, 3, 6]

    Args:
        documents (Dict[str, List[Dict[str, Any]]]): Dictionary from queries of lists of documents.

    Returns:
        List[Dict[str, Any]]: List of interleaved documents.
    """
    return [
        y
        for x in zip_longest(*documents.values(), fillvalue=None)
        for y in x
        if y is not None
    ]
