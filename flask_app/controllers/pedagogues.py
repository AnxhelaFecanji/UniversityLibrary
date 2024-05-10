from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt
from flask_app.models.student import Student
from flask_app.models.pedagogue import Pedagogue
from flask_app.models.book import Book
from flask_app.models.research import Research
from flask_app.models.notification import Notification
bcrypt = Bcrypt(app)

from datetime import datetime
from urllib.parse import unquote
UPLOAD_FOLDER = 'flask_app/static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import os
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import HTTPException, NotFound
import urllib.parse

import smtplib


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/pedagogue')
def indexPedagogue():
    if 'pedagogue_id' in session:
        return redirect('/pedagogue/profile')
    return redirect('/logout')

@app.route('/login/pedagogue')
def loginPagePedagogue():
    if 'pedagogue_id' in session:
        return redirect('/pedagogue')
    return render_template('pedagogueLogin.html')

@app.route('/login/pedagogue', methods = ['POST'])
def loginPedagogue():
    if 'pedagogue_id' in session:
        return redirect('/pedagogue')
    if not Pedagogue.validate_pedagogue(request.form):
        return redirect(request.referrer)
    pedagogue = Pedagogue.get_pedagogue_by_email(request.form)
    if not pedagogue:
        flash('This email doesnt exist', 'emailLoginPedagogue')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(pedagogue['password'], request.form['password']):
        flash('Incorrect password', 'passwordLoginPedagogue')
        return redirect(request.referrer)
    session['pedagogue_id']= pedagogue['id']
    return redirect('/pedagogue/profile')

@app.route('/pedagogue/profile')
def profilePedagogue():
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id': session['pedagogue_id']
    }
    pedagogue=Pedagogue.get_pedagogue_by_id(data)
    return render_template('pedagoguedashboard.html', pedagogue=pedagogue)

@app.route('/pedagogue/update/profile/pic', methods = ['POST'])
def updateProfilePic():
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    if 'profilePic' not in request.files:
        flash('Please upload an image', 'profilePic')
        return redirect(request.referrer)
    profile = request.files['profilePic']
    if not allowed_file(profile.filename):
        flash('The file should be in png, jpg or jpeg format!', 'profilePic')
        return redirect(request.referrer)
    if profile and allowed_file(profile.filename):
        filename1 = secure_filename(profile.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename1
        filename1 = time
        profile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        data = {
            'profilePic': filename1,
            'id': session['pedagogue_id']
        }
        Pedagogue.update_profile_pic(data)
        return redirect(request.referrer)
    return redirect('/pedagogue')

@app.route('/pedagogue/books', methods=['GET', 'POST'])
def allBooks():
    if request.method == 'GET':
        if 'pedagogue_id' not in session:
            return redirect('/pedagogue')
        data = {
            'id': session['pedagogue_id']
        }
        pedagogue=Pedagogue.get_pedagogue_by_id(data)
        books = Book.get_all_books()
        total_books = Book.get_books_number()
        
        total_pages = (total_books + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('pedagogueViewBooks.html', pedagogue=pedagogue, books = books, page=page, total_pages=total_pages, total_books=total_books)
    else:
        if 'pedagogue_id' not in session:
            return redirect('/pedagogue')
        data = {
            'id': session['pedagogue_id']
        }
        pedagogue=Pedagogue.get_pedagogue_by_id(data)
        if not request.form['title']:
            title = 'all'
        else:
            title = request.form['title'] + '%'
        if title == 'all':
            books = Book.get_all_books()
        elif title != 'all':
            data = {
                'title': title
            }
            books = Book.get_book_by_title(data)
        total_books = Book.get_books_number()
        
        total_pages = (total_books + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('pedagogueViewBooks.html', pedagogue=pedagogue, books = books, page=page, total_pages=total_pages, total_books=total_books)
        

@app.route('/pedagogue/book/<int:id>')
def showOnePedagogue(id):
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id': session['pedagogue_id'],
        'book_id': id
    }
    pedagogue=Pedagogue.get_pedagogue_by_id(data)
    book = Book.get_book_by_id(data)
    return render_template('pedagogueViewOneBook.html', book = book, pedagogue = pedagogue)

@app.route('/pedagogue/researches', methods=['GET', 'POST'])
def allResearches():
    if request.method == 'GET':
        if 'pedagogue_id' not in session:
            return redirect('/pedagogue')
        data = {
            'id': session['pedagogue_id']
        }
        pedagogue=Pedagogue.get_pedagogue_by_id(data)
        researches = Research.get_all_researches()
        total_researches = Research.get_researches_number()
        
        total_pages = (total_researches + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('pedagogueViewResearches.html', pedagogue=pedagogue, researches = researches, page=page, total_pages=total_pages, total_researches=total_researches)
    else:
        if 'pedagogue_id' not in session:
            return redirect('/pedagogue')
        data = {
            'id': session['pedagogue_id']
        }
        pedagogue=Pedagogue.get_pedagogue_by_id(data)
        if not request.form['title']:
            title = 'all'
        else:
            title = request.form['title'] + '%'
        if title == 'all':
            researches = Research.get_all_researches()
        elif title != 'all':
            data = {
                'title': title
            }
            researches = Research.get_research_by_title(data)
        total_researches = Research.get_researches_number()
        
        total_pages = (total_researches + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('pedagogueViewResearches.html', pedagogue=pedagogue, researches = researches, page=page, total_pages=total_pages, total_researches=total_researches)

@app.route('/pedagogue/research/<int:id>')
def showOneResearch(id):
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id': session['pedagogue_id'],
        'research_id': id
    }
    pedagogue=Pedagogue.get_pedagogue_by_id(data)
    research = Research.get_research_by_id(data)
    return render_template('pedagogueViewOneResearch.html', research = research, pedagogue = pedagogue)

@app.route('/pedagogue/add/notification')
def newNotification():
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id': session['pedagogue_id']
    }
    pedagogue = Pedagogue.get_pedagogue_by_id(data)
    return render_template('newNotification.html', pedagogue = pedagogue)

@app.route('/pedagogue/add/notification', methods = ['POST'])
def createNotification():
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id': session['pedagogue_id']
    }
    pedagogue = Pedagogue.get_pedagogue_by_id(data)
    if pedagogue:
        if not Notification.validate_notification(request.form):
            return redirect(request.referrer)
    data = {
        'title': request.form['title'],
        'description': request.form['description'],
        'field': request.form['field'],
        'pedagogue_id': session['pedagogue_id']
    }
    Notification.create_notification(data)
    flash('Notification created successfully', 'notificationSuccessCreated')
    return redirect(request.referrer)

@app.route('/pedagogue/my/notifications')
def allMyNotifications():
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id': session['pedagogue_id']
    }
    pedagogue=Pedagogue.get_pedagogue_by_id(data)
    notifications=Notification.get_my_all_notifications(data)
   
    total_notifications = Notification.get_notifications_number()
    
    total_pages = (total_notifications + 5) // 6
    page = request.args.get('page', 1, type=int)
    return render_template('pedagogueViewNotifications.html', pedagogue=pedagogue,notifications=notifications,page=page, total_pages=total_pages, total_notifications=total_notifications)

@app.route('/pedagogue/notification/<int:id>')
def showOneNotification(id):
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id':session['pedagogue_id'],
        'notification_id': id
    }
    pedagogue=Pedagogue.get_pedagogue_by_id(data)
    notification=Student.get_notification_by_id(data)
    print(notification)

    total_notifications = Notification.get_notifications_number()
    commentsStudentNr = Student.get_comments_number()
    commentsPedagogueNr = Pedagogue.get_comments_pedagogue_number()
    commentsNr = commentsStudentNr + commentsPedagogueNr
    
    return render_template('pedagogueViewOneNotification.html', pedagogue=pedagogue, notification = notification, total_notifications=total_notifications, commentsNr=commentsNr)

@app.route('/pedagogue/delete/comment/<int:comment_id>')
def deleteCommentPedagogue(comment_id):
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    
    data = {
        'id': session['pedagogue_id'],
        'comment_id': comment_id
    }
    comment = Pedagogue.get_comment_pedagogue_by_id(data)
    print(comment)
    print("Received comment ID:", id)
    print("Session pedagogue ID:", session.get('pedagogue_id'))
    if comment and comment['pedagogue_id'] == session['pedagogue_id']:
        Pedagogue.deleteCommentPedagogue(data)
    return redirect(request.referrer)

@app.route('/pedagogue/comments/add/<int:id>', methods = ['POST'])
def createCommentPedagogue(id):
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    if not Pedagogue.validate_notificationCommentPedagogue(request.form):
        return redirect(request.referrer)
    data = {
        'pedagogue_id': session['pedagogue_id'],
        'notification_id': id,
        'comment': request.form['comment']
    }
    Pedagogue.addCommentPedagogue(data)
    return redirect(request.referrer)

@app.route('/pedagogue/notification/delete/<int:id>')
def deleteNotificationPedagogue(id):
    if 'pedagogue_id' not in session:
        return redirect('/pedagogue')
    data = {
        'id':session['pedagogue_id'],
        'notification_id': id
    }
    notification = Notification.get_notification_by_id(data)
    
    if notification['pedagogue_id'] == session['pedagogue_id']:
        Student.deleteAllNotificationComments(data)
        Pedagogue.deleteAllNotificationCommentsPedagogue(data)
        Notification.deleteNotification(data)
    return redirect(request.referrer)