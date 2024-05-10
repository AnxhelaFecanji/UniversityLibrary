from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

class Notification:
    db_name = "libraryUetDB"
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.description = data['description']
        self.field = data['field']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.pedagogue_id = data['pedagogue_id']
        
    @classmethod
    def create_notification(cls, data):
        query = "INSERT INTO notifications (title, description, field, pedagogue_id) VALUES (%(title)s, %(description)s, %(field)s, %(pedagogue_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_notifications(cls):
        query = "SELECT * FROM notifications;"
        results = connectToMySQL(cls.db_name).query_db(query)
        notifications = []
        if results:
            for row in results:
                notifications.append(row)
        return notifications
    
    @classmethod
    def get_my_all_notifications(cls, data):
        query = "SELECT * FROM notifications WHERE pedagogue_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        notifications = []
        if results:
            for row in results:
                notifications.append(row)
        return notifications
    
    @classmethod
    def deletePedagogueNotification(cls, data):
        query = "DELETE FROM notifications where notifications.pedagogue_id = %(pedagogue_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
     
    @classmethod
    def deleteNotification(cls, data):
        query = "DELETE FROM notifications where id = %(notification_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def get_notifications_number(cls):
        query = "SELECT COUNT(*) AS notifications_count FROM notifications;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['notifications_count']
        return False
   
    @classmethod
    def get_notification_by_id(cls, data):
        query = 'SELECT * FROM notifications where id = %(notification_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
         
    @staticmethod
    def validate_notification(notification):
        is_valid = True
        if len(notification['title'])<2:
            flash("Title is required", 'titleNotificationRegister')
            is_valid = False   
        if len(notification['description'])<8:
            flash("Description is required and should be more than 8 characters!", 'descriptionNotificationRegister')
            is_valid = False
        if len(notification['field'])<2:
            flash("Field is required!", 'fieldNotificationRegister')
            is_valid = False   
        return is_valid