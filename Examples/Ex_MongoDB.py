from pymongo import MongoClient # pip install pymongo
# Client: MongoDB Compass

# Establish connection to MongoDB
print("Establish connection to MongoDB")
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI
db = client['test_database']  # Replace with your database name
collection = db['test_collection']  # Replace with your collection name

# 1. CREATE: Insert documents into the collection
def create_documents():
    # Single document
    single_doc = {"name": "Alice", "age": 25, "city": "New York"}
    collection.insert_one(single_doc)
    
    # Multiple documents
    multiple_docs = [
        {"name": "Bob", "age": 30, "city": "Los Angeles"},
        {"name": "Charlie", "age": 35, "city": "Chicago"},
    ]
    collection.insert_many(multiple_docs)
    print("Documents inserted.")

# 2. READ: Query documents from the collection
def read_documents():
    # Find all documents
    print("All documents:")
    for doc in collection.find():
        print(doc)
    
    # Find specific documents
    print("\nDocuments where age > 25:")
    for doc in collection.find({"age": {"$gt": 25}}):
        print(doc)
    
    # Find one document
    single_doc = collection.find_one({"name": "Alice"})
    print("\nSingle document (Alice):", single_doc)

# 3. UPDATE: Modify documents in the collection
def update_documents():
    # Update a single document
    collection.update_one({"name": "Alice"}, {"$set": {"age": 26}})
    print("\nAlice's age updated.")
    
    # Update multiple documents
    collection.update_many({"city": "Los Angeles"}, {"$set": {"city": "San Francisco"}})
    print("City updated for all residents of Los Angeles.")

# 4. DELETE: Remove documents from the collection
def delete_documents():
    # Delete a single document
    collection.delete_one({"name": "Alice"})
    print("\nAlice's document deleted.")
    
    # Delete multiple documents
    collection.delete_many({"age": {"$lt": 30}})
    print("Documents with age < 30 deleted.")

# Main function to demonstrate CRUD operations
if __name__ == "__main__":
    print("Main")
    # Create
    create_documents()
    
    # Read
    read_documents()
    
    # Update
    update_documents()
    read_documents()  # Check updates
    
    # Delete
    delete_documents()
    read_documents()  # Check remaining documents