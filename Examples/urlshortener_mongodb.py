from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
    db = client["urlShortenerDB"]  # Database name
    return db

# Insert a Document into MongoDB
def insert_document(db):
    collection = db["urls"]  # Collection name

    # Document to insert
    document = {
        "shortUrlId": "3ad32p9",
        "longUrl": "https://example.com/very-long-url",
        "creationDate": datetime(2024, 3, 8, 12, 0, 0),  # ISODate format
        "userId": "user123",
        "clicks": 1023,
        "metadata": {
            "title": "Example Web Page",
            "tags": ["example", "web", "url shortener"],
            "expireDate": datetime(2025, 3, 8, 12, 0, 0)  # ISODate format
        },
        "isActive": True
    }

    # Insert document
    result = collection.insert_one(document)
    print(f"Document inserted with ID: {result.inserted_id}")

# Main Function
if __name__ == "__main__":
    # Connect to MongoDB and insert the document
    db = connect_to_mongodb()
    insert_document(db)