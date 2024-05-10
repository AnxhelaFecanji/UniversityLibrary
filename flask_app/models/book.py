from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

class Book:
    db_name = "libraryUetDB"
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.author = data['author']
        self.description = data['description']
        self.nrOfPages = data['nrOfPages']
        self.isbn = data['isbn']
        self.dateOfPublication = data['dateOfPublication']
        self.subjectArea = data['subjectArea']
        self.language = data['language']
        self.coverImage = data['coverImage']
        self.publishingHouse = data['publishingHouse']
        self.price = data['price']
        self.bookPdf = data['bookPdf']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.admin_id = data['admin_id']
        
    @classmethod
    def create_book(cls, data):
        query = "INSERT INTO books (title, author, description, nrOfPages, isbn, dateOfPublication, subjectArea, language, coverImage, publishingHouse, price, bookPdf, admin_id) VALUES (%(title)s, %(author)s,  %(description)s, %(nrOfPages)s, %(isbn)s, %(dateOfPublication)s, %(subjectArea)s, %(language)s, %(coverImage)s, %(publishingHouse)s, %(price)s, %(bookPdf)s, %(admin_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_books(cls):
        query = "SELECT * FROM books;"
        results = connectToMySQL(cls.db_name).query_db(query)
        books = []
        if results:
            for row in results:
                books.append(row)
        return books

    @classmethod
    def get_books_number(cls):
        query = "SELECT COUNT(*) AS books_count FROM books;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['books_count']
        return False
    
    @classmethod
    def get_books_price(cls, data):
        query = "SELECT price FROM books WHERE id = %(book_id)s;"
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
   
    @classmethod
    def get_book_by_id(cls, data):
        query = 'SELECT * FROM books where id = %(book_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def deleteBook(cls, data):
        query = "DELETE FROM books where id = %(book_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_book_by_title(cls, data):
        query = 'SELECT * FROM books where title LIKE %(title)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        books=[]
        if result:
            for book in result:
                books.append(book)
            return books
            
        return books
         
    @staticmethod
    def validate_book(book):
        is_valid = True
        if len(book['title'])<2:
            flash("Title is required", 'titleBookRegister')
            is_valid = False 
        if len(book['author'])<8:
            flash("Author is required", 'authorBookRegister')
            is_valid = False  
        if len(book['description'])<10:
            flash("Description is required and should be more than 10 characters!", 'descriptionBookRegister')
            is_valid = False
        if len(book['nrOfPages'])<1:
            flash("Number of pages is required!", 'pagesBookRegister')
            is_valid = False
        if len(book['isbn'])<13:
            flash("ISBN is required!", 'isbnBookRegister')
            is_valid = False
        if len(book.get('subjectArea', '')) < 1:
            flash("Subject Area is required!", 'subjectAreaBookRegister')
            is_valid = False
        if len(book['dateOfPublication'])<1:
            flash("Publication Date is required!", 'publicationDateBookRegister')
            is_valid = False
        if len(book['language'])<1:
            flash("Language is required!", 'languageBookRegister')
            is_valid = False
        if len(book['publishingHouse'])<1:
            flash("Publishin House is required!", 'publishingHouseBookRegister')
            is_valid = False
        if len(book['price'])<1:
            flash("Price is required!", 'priceBookRegister')
            is_valid = False
            
        return is_valid