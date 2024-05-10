from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

class Student:
    db_name = "libraryUetDB"
    def __init__(self, data):
        self.id = data['id']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.phone = data['phone']
        self.studyProgram = data['studyProgram']
        self.faculty = data['faculty']
        self.dega = data['dega']
        self.startAccess = data['startAccess']
        self.endAccess = data['endAccess']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.admin_id = data['admin_id']
        
    @classmethod
    def create_student(cls, data):
        query = "INSERT INTO students (firstName, lastName, phone, studyProgram, faculty, dega, startAccess, endAccess, email, password, admin_id) VALUES (%(firstName)s, %(lastName)s,  %(phone)s, %(studyProgram)s, %(faculty)s, %(dega)s, %(startAccess)s, %(endAccess)s, %(email)s, %(password)s, %(admin_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_students(cls):
        query = "SELECT * FROM students;"
        results = connectToMySQL(cls.db_name).query_db(query)
        students = []
        if results:
            for row in results:
                students.append(row)
        return students
    
    @classmethod
    def get_students_number(cls):
        query = "SELECT COUNT(*) AS student_count FROM students;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['student_count']
        return False
    
    @classmethod
    def get_comments_number(cls):
        query = "SELECT COUNT(*) AS comment_count FROM comments;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['comment_count']
        return False

    @classmethod
    def get_student_by_email(cls, data):
        query = 'SELECT * FROM students where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    @classmethod
    def get_student_by_id(cls, data):
        query = 'SELECT * FROM students where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def update_profile_pic(cls, data):
        query = "UPDATE students set profilePic = %(profilePic)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_notification_by_id(cls, data):
        query = 'SELECT * FROM notifications LEFT JOIN pedagogues ON notifications.pedagogue_id = pedagogues.id LEFT JOIN comments_pedagogue ON comments_pedagogue.pedagogue_id = pedagogues.id WHERE notifications.id = %(notification_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        
        if result:
            query2 = 'SELECT * FROM comments LEFT JOIN students ON comments.student_id = students.id WHERE comments.notification_id = %(notification_id)s;'
            
            results2 = connectToMySQL(cls.db_name).query_db(query2, data)
            
            comments = []

            for row in result:
                if 'comment' in row and row['comment']:
                    comments.append(row)  # Assuming 'comment' is the column name for lecturer comments
            for row in results2:
                comments.append(row)  # Assuming 'comment' is the column name for student comments
        
            result[0]['comments'] = comments
            return result[0]
        
        return False

    
    @classmethod
    def addComment(cls, data):
        query = "INSERT INTO comments (comment, student_id, notification_id) VALUES (%(comment)s, %(student_id)s, %(notification_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_comment_by_id(cls, data):
        query = 'SELECT * FROM comments where id = %(comment_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def deleteAllNotificationComments(cls, data):
        query = "DELETE FROM comments where comments.notification_id = %(notification_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
   
    
    @classmethod
    def deleteComment(cls, data):
        query = "DELETE FROM comments where id = %(comment_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteStudent(cls, data):
        query = "DELETE FROM students where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
        
    @classmethod
    def deleteStudentComment(cls, data):
        query = "DELETE FROM comments where comments.student_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def addTestimonialStudent(cls, data):
        query = "INSERT INTO student_testimonials (comment, student_id) VALUES (%(comment)s, %(student_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteStudentTestimonial(cls, data):
        query = "DELETE FROM student_testimonials where student_testimonials.student_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_testimonials_student(cls):
        query = "SELECT * FROM student_testimonials LEFT JOIN students ON student_testimonials.student_id = students.id;"
        results = connectToMySQL(cls.db_name).query_db(query)
        testimonials = []
        if results:
            for testimonial in results:
                testimonials.append(testimonial)
            return testimonials
        return testimonials
    
    @classmethod
    def studentBookPayment(cls,data):
        query = "INSERT INTO student_book_payments (ammount, status, student_id, book_id) VALUES (%(ammount)s, %(status)s, %(student_id)s, %(book_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteStudentBookPayment(cls, data):
        query = "DELETE FROM student_book_payments where student_book_payments.student_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteDownloadPaymentBook(cls, data):
        query = "DELETE FROM student_book_payments where student_book_payments.book_id = %(book_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deleteDownloadGuestsPaymentBook(cls, data):
        query = "DELETE FROM book_payments where book_payments.book_id = %(book_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    
    @staticmethod
    def validate_student(student):
        is_valid = True
        if not EMAIL_REGEX.match(student['email']): 
            flash("Invalid email address!", 'emailLoginStudent')
            is_valid = False
        if len(student['password'])<8:
            flash("Password is required!", 'passwordLoginStudent')
            is_valid = False
        return is_valid
    
    
    @staticmethod
    def validate_studentRegister(student):
        is_valid = True
        if not EMAIL_REGEX.match(student['email']): 
            flash("Invalid email address!", 'studentEmailRegister')
            is_valid = False
        if len(student['password'])<8:
            flash("Password should be minimum 8 characters!", 'studentPasswordRegister')
            is_valid = False 
        if len(student['confirm_password'])<8:
            flash("Confirm Password should be minimum 8 characters!", 'studentConfirmPasswordRegister')
            is_valid = False  
        if student['password'] != student['confirm_password']:
            flash("Your password is different from the confirmed password ", 'errorStudentPasswordRegister')   
            is_valid = False 
        if len(student['firstName'])<1:
            flash("First name is required!", 'studentNameRegister')
            is_valid = False
        if len(student['lastName'])<1:
            flash("Last name is required!", 'studentlastNameRegister')
            is_valid = False
        if len(student['phone'])<1:
            flash("Phone is required!", 'studentPhoneRegister')
            is_valid = False
        if len(student.get('studyProgram', '')) < 1:
            flash("Study Program is required!", 'studentStudyProgramRegister')
            is_valid = False
        if len(student.get('faculty', '')) < 1:
            flash("Faculty is required!", 'studentFacultyRegister')
            is_valid = False
        if len(student['dega'])<1:
            flash("Profile of study is required!", 'studentDegaRegister')
            is_valid = False
        if len(student['startAccess'])<1:
            flash("Start Access is required!", 'studentStartAccessRegister')
            is_valid = False
        if len(student['endAccess'])<1:
            flash("End Access is required!", 'studentEndAccessRegister')
            is_valid = False
            
        return is_valid
    
    @staticmethod
    def validate_notificationComment(comment):
        is_valid = True
        if len(comment['comment'])< 2:
            flash('comment should be more  or equal to 2 characters', 'notificationComment')
            is_valid = False
        return is_valid
    
    
    @staticmethod
    def validate_testimonial_student(testimonial):
        is_valid = True
        if len(testimonial['comment'])<8:
            flash("Testimonial is required!", 'studentTestimonialAdd')
            is_valid = False
        return is_valid