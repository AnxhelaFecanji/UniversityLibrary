from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

class Guest:
    db_name = "libraryUetDB"
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.role_type = data['role_type']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        
    @classmethod
    def create_guest(cls, data):
        query = "INSERT INTO guests (first_name, last_name, role_type, email, password) VALUES (%(first_name)s, %(last_name)s,  %(role_type)s,  %(email)s, %(password)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_guests(cls):
        query = "SELECT * FROM guests;"
        results = connectToMySQL(cls.db_name).query_db(query)
        guests = []
        if results:
            for row in results:
                guests.append(row)
        return guests
    
    @classmethod
    def get_guests_number(cls):
        query = "SELECT COUNT(*) AS guest_count FROM guests;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['guest_count']
        return False

    @classmethod
    def get_guest_by_email(cls, data):
        query = 'SELECT * FROM guests where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    @classmethod
    def get_guest_by_id(cls, data):
        query = 'SELECT * FROM guests where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def update_profile_pic_guest(cls, data):
        query = "UPDATE guests set profilePic = %(profilePic)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def createPaymentBook(cls,data):
        query = "INSERT INTO book_payments (ammount, status, guest_id, book_id) VALUES (%(ammount)s, %(status)s, %(guest_id)s, %(book_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def makeDonation(cls,data):
        query = "INSERT INTO payments (ammount, status, guest_id) VALUES (%(ammount)s, %(status)s, %(guest_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def registrationPayment(cls,data):
        query = "INSERT INTO registration_payments (ammount, status, guest_id) VALUES (%(ammount)s, %(status)s, %(guest_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def bookPayment(cls,data):
        query = "INSERT INTO book_payments (ammount, status, guest_id, book_id) VALUES (%(ammount)s, %(status)s, %(guest_id)s, %(book_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def addTestimonialGuest(cls, data):
        query = "INSERT INTO testimonials (testimonial, guest_id) VALUES (%(testimonial)s, %(guest_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_testimonials_guest(cls):
        query = "SELECT * FROM testimonials LEFT JOIN guests ON testimonials.guest_id = guests.id;"
        results = connectToMySQL(cls.db_name).query_db(query)
        testimonials = []
        if results:
            for testimonial in results:
                testimonials.append(testimonial)
            return testimonials
        return testimonials

        
    @staticmethod
    def validate_guest(guest):
        is_valid = True
        if not EMAIL_REGEX.match(guest['email']): 
            flash("Invalid email address!", 'emailLoginGuest')
            is_valid = False
        if len(guest['password'])<8:
            flash("Password is required!", 'passwordLoginGuest')
            is_valid = False
        return is_valid
    
    
    @staticmethod
    def validate_guestRegister(guest):
        is_valid = True
        if not EMAIL_REGEX.match(guest['email']): 
            flash("Invalid email address!", 'guestEmailRegister')
            is_valid = False
        if len(guest['password'])<8:
            flash("Password should be minimum 8 characters!", 'guestPasswordRegister')
            is_valid = False 
        if len(guest['confirm_password'])<8:
            flash("Confirm Password should be minimum 8 characters!", 'guestConfirmPasswordRegister')
            is_valid = False  
        if guest['password'] != guest['confirm_password']:
            flash("Your password is different from the confirmed password ", 'errorGuestPasswordRegister')   
            is_valid = False 
        if len(guest['first_name'])<1:
            flash("First name is required!", 'guestNameRegister')
            is_valid = False
        if len(guest['last_name'])<1:
            flash("Last name is required!", 'guestlastNameRegister')
            is_valid = False
        if len(guest['role_type'])<1:
            flash("Role is required!", 'guestRoleRegister')
            
        return is_valid
    
    @staticmethod
    def validate_testimonial_guest(testimonial):
        is_valid = True
        if len(testimonial['testimonial'])<8:
            flash("Testimonial is required!", 'testimonialadd')
            is_valid = False
        return is_valid
  