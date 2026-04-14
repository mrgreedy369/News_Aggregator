from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

uri = os.getenv('MONGO_URI')
print(f"Testing connection with URI: {uri[:30]}...")

try:
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    print(f"Databases: {client.list_database_names()}")
except Exception as e:
    print(f"❌ Connection failed: {e}")