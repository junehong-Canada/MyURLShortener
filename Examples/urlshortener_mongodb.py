from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List, Optional

# MongoDB Connection
def connect_to_mongodb():
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
    db = client["urlShortenerDB"]  # Database name
    return db

# Create - Insert a new URL document
def create_url(db, short_url_id: str, long_url: str, user_id: str,
               title: str = None, tags: List[str] = None, 
               expire_date: datetime = None) -> str:
    collection = db["urls"]
    
    document = {
        "shortUrlId": short_url_id,
        "longUrl": long_url,
        "creationDate": datetime.now(),
        "userId": user_id,
        "clicks": 0,
        "metadata": {
            "title": title,
            "tags": tags or [],
            "expireDate": expire_date
        },
        "isActive": True
    }
    
    result = collection.insert_one(document)
    return str(result.inserted_id)

# Read - Get URL document by short ID
def get_url_by_id(db, short_url_id: str) -> Optional[Dict]:
    collection = db["urls"]
    return collection.find_one({"shortUrlId": short_url_id})

# Read - Get all URLs for a user
def get_urls_by_user(db, user_id: str) -> List[Dict]:
    collection = db["urls"]
    return list(collection.find({"userId": user_id}))

# Update - Update URL document
def update_url(db, short_url_id: str, updates: Dict) -> bool:
    collection = db["urls"]
    result = collection.update_one(
        {"shortUrlId": short_url_id},
        {"$set": updates}
    )
    return result.modified_count > 0

# Update - Increment click count
def increment_clicks(db, short_url_id: str) -> bool:
    collection = db["urls"]
    result = collection.update_one(
        {"shortUrlId": short_url_id},
        {"$inc": {"clicks": 1}}
    )
    return result.modified_count > 0

# Delete - Delete URL document
def delete_url(db, short_url_id: str) -> bool:
    collection = db["urls"]
    result = collection.delete_one({"shortUrlId": short_url_id})
    return result.deleted_count > 0

# Main Function
if __name__ == "__main__":
    # Connect to MongoDB and test CRUD operations
    db = connect_to_mongodb()
    
    # Example usage
    url_id = create_url(
        db,
        "abc123",
        "https://example.com",
        "user1",
        "Example Site",
        ["test", "example"],
        datetime(2025, 12, 31)
    )
    print(f"Created URL with ID: {url_id}")