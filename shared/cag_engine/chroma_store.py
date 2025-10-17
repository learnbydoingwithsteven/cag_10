"""
ChromaDB vector store implementation.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional, Tuple
import logging
import uuid
from .base import VectorStore

logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of vector store."""

    def __init__(
        self,
        collection_name: str,
        persist_directory: str = "./chroma_db",
        embedding_function=None
    ):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Initialized ChromaDB collection: {collection_name}")

    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ):
        """
        Add documents to the vector store.

        Args:
            documents: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
            embeddings: Optional pre-computed embeddings
        """
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in documents]

            # Prepare metadatas
            if metadatas is None:
                metadatas = [{} for _ in documents]

            # Add to collection
            if embeddings:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings
                )
            else:
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

            logger.info(f"Added {len(documents)} documents to collection")

        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    async def search(
        self,
        query: str,
        limit: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        query_embedding: Optional[List[float]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            limit: Maximum number of results
            filter_dict: Optional metadata filter
            query_embedding: Optional pre-computed query embedding

        Returns:
            List of tuples (document, score, metadata)
        """
        try:
            # Perform search
            if query_embedding:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=limit,
                    where=filter_dict
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit,
                    where=filter_dict
                )

            # Format results
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                documents = results['documents'][0]
                distances = results['distances'][0]
                metadatas = results['metadatas'][0]

                for doc, dist, meta in zip(documents, distances, metadatas):
                    # Convert distance to similarity score (1 - distance for cosine)
                    similarity = 1 - dist
                    formatted_results.append((doc, similarity, meta))

            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            raise

    async def delete(self, ids: List[str]):
        """
        Delete documents by IDs.

        Args:
            ids: List of document IDs to delete
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "name": self.collection_name,
                "count": count,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {}

    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            # Get all IDs
            results = self.collection.get()
            if results['ids']:
                self.collection.delete(ids=results['ids'])
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            raise

    async def update_document(
        self,
        doc_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ):
        """
        Update a document in the collection.

        Args:
            doc_id: Document ID
            document: Optional new document text
            metadata: Optional new metadata
            embedding: Optional new embedding
        """
        try:
            update_params = {"ids": [doc_id]}
            
            if document:
                update_params["documents"] = [document]
            if metadata:
                update_params["metadatas"] = [metadata]
            if embedding:
                update_params["embeddings"] = [embedding]

            self.collection.update(**update_params)
            logger.info(f"Updated document: {doc_id}")

        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            raise

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            Dictionary with document data or None if not found
        """
        try:
            results = self.collection.get(ids=[doc_id])
            
            if results['ids']:
                return {
                    "id": results['ids'][0],
                    "document": results['documents'][0] if results['documents'] else None,
                    "metadata": results['metadatas'][0] if results['metadatas'] else None,
                    "embedding": results['embeddings'][0] if results.get('embeddings') else None
                }
            return None

        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None

    async def batch_search(
        self,
        queries: List[str],
        limit: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[List[Tuple[str, float, Dict[str, Any]]]]:
        """
        Perform batch search for multiple queries.

        Args:
            queries: List of query texts
            limit: Maximum number of results per query
            filter_dict: Optional metadata filter

        Returns:
            List of result lists, one per query
        """
        try:
            results = self.collection.query(
                query_texts=queries,
                n_results=limit,
                where=filter_dict
            )

            # Format results for each query
            all_results = []
            for i in range(len(queries)):
                query_results = []
                if results['documents'] and len(results['documents']) > i:
                    documents = results['documents'][i]
                    distances = results['distances'][i]
                    metadatas = results['metadatas'][i]

                    for doc, dist, meta in zip(documents, distances, metadatas):
                        similarity = 1 - dist
                        query_results.append((doc, similarity, meta))

                all_results.append(query_results)

            return all_results

        except Exception as e:
            logger.error(f"Error in batch search: {str(e)}")
            raise
