from fastapi import FastAPI, HTTPException, Request
from pymongo import MongoClient
from pydantic import BaseModel, Field
import logging
from fastapi import middleware

logging.basicConfig(level=logging.INFO)

app = FastAPI()
# username = "prashanth_ikarus"
# password = ""

# escaped_username = urllib.parse.quote_plus(username)
# escaped_password = urllib.parse.quote_plus(password)
# MongoDB connection details
mongo_uri = "mongodb+srv://ikarus-sagar:SagarIkarus@cluster-1.yntllpq.mongodb.net/"
#mongo_uri =  "mongodb+srv://{escaped_username}:{escaped_password}@cluster.pnekiv8.mongodb.net/"
database_name = "Library"
collection_name = "NITW_Books"


# Connect to MongoDB
client = MongoClient(mongo_uri)
database = client[database_name]
collection = database[collection_name]


class BookCreate(BaseModel):
    title: str  
    author: str 
    rating: float

class BookUpdate(BaseModel):
    author: str
    rating: float

@app.get("/books")
def get_books(author: str = None, rating: float = None):
    query = {}
    if author:
        query["author"] = author
    if rating is not None:
        query["rating"] = rating
    books = list(collection.find(query, {"_id": 0}))
    return {"books": books}

@app.post("/books/create")
def create_book(book: BookCreate):
    #insert a new book document
    book_data = book.dict()
    result = collection.insert_one(book_data)
    return {"message": "Book created", "book_title": book_data["title"]}

@app.get("/books/get/{book_title}")
def read_book(book_title: str):
    book = collection.find_one({"title": book_title}, {"_id": 0})
    if book:
        return book
    else:
        raise HTTPException(status_code=404, detail="Book not found")

@app.put("/books/update/{book_title}")
def update_book(book_title: str, book: BookUpdate):
    #update a book document
    updated_book_data = book.dict()
    result = collection.update_one({"title": book_title}, {"$set": updated_book_data})
    if result.modified_count > 0:
        return {"message": "Book updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/delete/{book_title}")
def delete_book(book_title: str):
    #delete a book document
    result = collection.delete_one({"title": book_title})
    
    if result.deleted_count > 0:
        return {"message": "Book deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Book not found")


@app.middleware("http")
async def middleware(request: Request, call_next):
    logging.info("Middleware: Before request processing")
    response = await call_next(request)
    logging.info("Middleware: After request processing")
    return response
