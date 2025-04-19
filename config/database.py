import firebase_admin
from firebase_admin import credentials, firestore
import os
from pathlib import Path

class FirebaseDB:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseDB, cls).__new__(cls)
            cls._instance._initialize_firebase()
        return cls._instance
    
    def _initialize_firebase(self):
        """Initialize Firebase connection using credentials"""
        try:
            # Get the path to firebase_key.json
            base_dir = Path(__file__).parent.parent
            cred_path = os.path.join(base_dir, 'config', 'firebase_key.json')
            
            # Initialize Firebase
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            
            # Initialize Firestore
            self.db = firestore.client()
            print("Firebase connection established successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            self.db = None
    
    def get_collection(self, collection_name):
        """Get a reference to a collection"""
        return self.db.collection(collection_name) if self.db else None
    
    def add_document(self, collection_name, data, document_id=None):
        """Add a document to a collection"""
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        if document_id:
            return collection.document(document_id).set(data)
        else:
            return collection.add(data)
    
    def get_document(self, collection_name, document_id):
        """Get a document by ID"""
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        return collection.document(document_id).get()
    
    def update_document(self, collection_name, document_id, data):
        """Update fields in a document"""
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        return collection.document(document_id).update(data)
    
    def delete_document(self, collection_name, document_id):
        """Delete a document"""
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        return collection.document(document_id).delete()
    
    def query_documents(self, collection_name, field, operator, value):
        """Query documents based on field conditions"""
        collection = self.get_collection(collection_name)
        if not collection:
            return []

        return collection.where(field, operator, value).stream()
