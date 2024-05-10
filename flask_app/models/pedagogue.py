from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

class Pedagogue:
    db_name = "libraryUetDB"
    def __init__(self, data):
        self.id = data['id']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.phone = data['phone']
        self.department = data['department']
        self.position = data['position']
        self.title = data['title']
        self.faculty = data['faculty']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.admin_id = data['admin_id']
        
    @classmethod
    def create_pedagogue(cls, data):
        query = "INSERT INTO pedagogues (firstName, lastName, phone, department, faculty, position, title, email, password, admin_id) VALUES (%(firstName)s, %(lastName)s,  %(phone)s, %(department)s, %(faculty)s, %(position)s, %(title)s, %(email)s, %(password)s, %(admin_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_pedagogues(cls):
        query = "SELECT * FROM pedagogues;"
        results = connectToMySQL(cls.db_name).query_db(query)
        pedagogues = []
        if results:
            for row in results:
                pedagogues.append(row)
        return pedagogues
    
    @classmethod
    def get_pedagogues_number(cls):
        query = "SELECT COUNT(*) AS pedagogue_count FROM pedagogues;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['pedagogue_count']
        return False

    @classmethod
    def get_pedagogue_by_email(cls, data):
        query = 'SELECT * FROM pedagogues where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    @classmethod
    def get_pedagogue_by_id(cls, data):
        query = 'SELECT * FROM pedagogues where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def update_profile_pic(cls, data):
        query = "UPDATE pedagogues set profilePic = %(profilePic)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_comments_pedagogue_number(cls):
        query = "SELECT COUNT(*) AS comment_count FROM comments_pedagogue;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['comment_count']
        return False
    
    @classmethod
    def addCommentPedagogue(cls, data):
        query = "INSERT INTO comments_pedagogue (comment, pedagogue_id, notification_id) VALUES (%(comment)s, %(pedagogue_id)s, %(notification_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
   
    
    @classmethod
    def deleteAllNotificationCommentsPedagogue(cls, data):
        query = "DELETE FROM comments_pedagogue where comments_pedagogue.notification_id = %(notification_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
   
    
    @classmethod
    def deleteCommentPedagogue(cls, data):
        query = "DELETE FROM comments_pedagogue where comment_id = %(comment_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    
    @classmethod
    def deletePedagogue(cls, data):
        query = "DELETE FROM pedagogues where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def deletePedagogueComment(cls, data):
        query = "DELETE FROM comments_pedagogue where comments_pedagogue.pedagogue_id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_comment_pedagogue_by_id(cls, data):
        query = 'SELECT * FROM comments_pedagogue where comment_id = %(comment_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
        
    @staticmethod
    def validate_pedagogue(pedagogue):
        is_valid = True
        if not EMAIL_REGEX.match(pedagogue['email']): 
            flash("Invalid email address!", 'emailLoginPedagogue')
            is_valid = False
        if len(pedagogue['password'])<8:
            flash("Password is required!", 'passwordLoginPedagogue')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_pedagogueRegister(pedagogue):
        is_valid = True
        if not EMAIL_REGEX.match(pedagogue['email']): 
            flash("Invalid email address!", 'pedagogueEmailRegister')
            is_valid = False
        if len(pedagogue['password'])<8:
            flash("Password should be minimum 8 characters!", 'pedagoguePasswordRegister')
            is_valid = False 
        if len(pedagogue['confirm_password'])<8:
            flash("Confirm Password should be minimum 8 characters!", 'pedagogueConfirmPasswordRegister')
            is_valid = False  
        if pedagogue['password'] != pedagogue['confirm_password']:
            flash("Your password is different from the confirmed password ", 'errorPedagoguePasswordRegister')   
            is_valid = False 
        if len(pedagogue['firstName'])<1:
            flash("First name is required!", 'pedagogueNameRegister')
            is_valid = False
        if len(pedagogue['lastName'])<1:
            flash("Last name is required!", 'pedagoguelastNameRegister')
            is_valid = False
        if len(pedagogue['position'])<1:
            flash("Position is required!", 'pedagoguePositionRegister')
            is_valid = False
        if len(pedagogue['title'])<1:
            flash("Title is required!", 'pedagogueTitleRegister')
            is_valid = False
        if len(pedagogue['phone'])<1:
            flash("Phone is required!", 'pedagoguePhoneRegister')
            is_valid = False
        if len(pedagogue.get('department', '')) < 1:
            flash("Department is required!", 'pedagogueDepartmentRegister')
            is_valid = False
        if len(pedagogue.get('faculty', '')) < 1:
            flash("Faculty is required!", 'PedagogueFacultyRegister')
            is_valid = False     
        return is_valid
    
    @staticmethod
    def validate_notificationCommentPedagogue(comment):
        is_valid = True
        if len(comment['comment'])< 2:
            flash('comment should be more  or equal to 2 characters', 'notificationCommentPedagogue')
            is_valid = False
        return is_valid