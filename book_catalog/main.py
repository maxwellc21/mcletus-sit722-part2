from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import Book
from schemas import BookInDB, BookCreate, BookUpdate
from typing import List

app = FastAPI()

@app.get("/books/", response_model=List[BookInDB])
async def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(Book).offset(skip).limit(limit).all()
    return [BookInDB.from_orm(book) for book in books]

@app.get("/books/{book_id}", response_model=BookInDB)
async def read_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookInDB.from_orm(book)

@app.post("/books/", response_model=BookInDB, status_code=201)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return BookInDB.from_orm(db_book)

@app.put("/books/{book_id}", response_model=BookInDB)
async def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return BookInDB.from_orm(db_book)

@app.delete("/books/{book_id}", response_model=BookInDB)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return BookInDB.from_orm(db_book)

@app.get("/test-db-connection/")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1")
        return {"status": "success", "result": result.fetchall()}
    except Exception as e:
        return {"status": "failure", "error": str(e)}
