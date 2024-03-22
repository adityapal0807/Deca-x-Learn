# create_vector_db.py
import pandas as pd
from typing import Optional, List, Tuple
import chromadb
from chromadb.config import Settings

class CreateCollection:
    """Class to create and manage a collection in a chromadb database."""

    def __init__(self, collection_name: str, db_path: Optional[str] = None) -> None:
        """
        Initialize the CreateCollection class.

        Args:
            collection_name (str): The name of the collection to be created or managed.
            db_path (Optional[str]): The path to the database. Defaults to './db' if None.
        """
        self.collection_name = collection_name
        self.db_path = db_path if db_path else './db'
        self.EXISTING_DB = False
        self.client = self._create_client()

    def _create_client(self):
        """Create a chromadb client."""
        return chromadb.PersistentClient(path=self.db_path, settings=Settings(allow_reset=True))

    def create_collection(self):
        """Create a new collection in the database."""
        # client = self._create_client()
        try:
            collection = self.client.get_collection(name=self.collection_name)
            print("Database exists.")
            self.EXISTING_DB = True
        except:
            print('Creating database...')
            # client.reset()
            collection = self.client.create_collection(self.collection_name, metadata={"hnsw:space": "cosine"})
            self.EXISTING_DB = False

        return collection

    def remove_collection(self):
        print(f'deleting collection {self.collection_name}')
        self.client.delete_collection(name=self.collection_name)

    def fill_collection_csv(self, csv_path: str):
        """Fill the collection with data from a CSV file."""
        df = pd.read_csv(csv_path)
        sentences = df['Content'].str.split('.').tolist()
        documents = [str(sentence[0]) if isinstance(sentence, list) and sentence else "" for sentence in sentences]
        ids = [str(index) for index, _ in enumerate(sentences)]

        db_collection = self.create_collection()

        if not self.EXISTING_DB:
            db_collection.add(documents=documents, metadatas=None, ids=ids)
        return db_collection

    def db_collection(self, fill_collection: bool, csv_path: Optional[str] = None):
        collection_manager = CreateCollection(self.collection_name)
        self.fill_collection = fill_collection
        if fill_collection:
            db_collection = collection_manager.fill_collection_csv(csv_path)
        else:
            db_collection = collection_manager.create_collection()

        return db_collection


# if __name__ == "__main__":
#     # Example usage in create_vector_db.py
#     csv_path = 'output.csv'
#     collection_manager = CreateCollection('physics1')
#     db_collection = collection_manager.db_collection(True, csv_path)
