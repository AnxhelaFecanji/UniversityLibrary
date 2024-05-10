from flask_app import app

from flask_app.controllers import admin, students, pedagogues, guests

if __name__=="__main__":     
    app.run(debug=True) 