from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash

class Research:
    db_name = "libraryUetDB"
    def __init__(self, data):
        self.id = data['id']
        self.title = data['title']
        self.author = data['author']
        self.publicationDate = data['publicationDate']
        self.journalOrConference = data['journalOrConference']
        self.doi = data['doi']
        self.researchField = data['researchField']
        self.researchPdf = data['researchPdf']
        self.language = data['language']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.admin_id = data['admin_id']
        
    @classmethod
    def create_research(cls, data):
        query = "INSERT INTO researches (title, author, publicationDate, journalOrConference, doi, researchField, researchPdf, language, admin_id) VALUES (%(title)s, %(author)s,  %(publicationDate)s, %(journalOrConference)s, %(doi)s, %(researchField)s, %(researchPdf)s, %(language)s, %(admin_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_all_researches(cls):
        query = "SELECT * FROM researches;"
        results = connectToMySQL(cls.db_name).query_db(query)
        researches = []
        if results:
            for row in results:
                researches.append(row)
        return researches
    
    @classmethod
    def get_researches_number(cls):
        query = "SELECT COUNT(*) AS research_count FROM researches;"
        result = connectToMySQL(cls.db_name).query_db(query)
        if result:
            return result[0]['research_count']
        return False

   
    @classmethod
    def get_research_by_id(cls, data):
        query = 'SELECT * FROM researches where id = %(research_id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def deleteResearch(cls, data):
        query = "DELETE FROM researches where id = %(research_id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_research_by_title(cls, data):
        query = 'SELECT * FROM researches where title LIKE %(title)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        researches=[]
        if result:
            for research in result:
                researches.append(research)
            return researches
            
        return researches
         
    @staticmethod
    def validate_research(research):
        is_valid = True
        if len(research['title'])<2:
            flash("Title is required", 'titleResearchRegister')
            is_valid = False 
        if len(research['author'])<2:
            flash("Author is required", 'authorResearchRegister')
            is_valid = False 
        if len(research['publicationDate'])<1:
            flash("Publication Date is required!", 'publicationDateResearchRegister')
            is_valid = False 
        if len(research['journalOrConference'])<3:
            flash("Journal or Conference is required", 'journalOrConferenceResearchRegister')
            is_valid = False
        if len(research['doi'])<5:
            flash("DOI is required!", 'doiResearchRegister')
            is_valid = False
        if len(research['researchField'])<2:
            flash("Research Field is required!", 'researchFieldRegister')
            is_valid = False
        if len(research['language'])<2:
            flash("Language is required!", 'languageResearchRegister')
            is_valid = False  
        return is_valid