from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt
from flask_app.models.student import Student
from flask_app.models.book import Book
from flask_app.models.research import Research
from flask_app.models.notification import Notification
bcrypt = Bcrypt(app)
import paypalrestsdk
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

@app.route('/student')
def indexStudent():
    if 'student_id' in session:
        return redirect('/student/profile')
    return redirect('/logout')

@app.route('/login/student')
def loginPageStudent():
    if 'student_id' in session:
        return redirect('/student')
    return render_template('studentLogin.html')

@app.route('/login/student', methods = ['POST'])
def loginStudent():
    if 'student_id' in session:
        return redirect('/student')
    if not Student.validate_student(request.form):
        return redirect(request.referrer)
    student = Student.get_student_by_email(request.form)
    if not student:
        flash('This email doesnt exist', 'emailLoginStudent')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(student['password'], request.form['password']):
        flash('Incorrect password', 'passwordLoginStudent')
        return redirect(request.referrer)
    session['student_id']= student['id']
    return redirect('/student/profile')

@app.route('/student/profile')
def profileStudent():
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id']
    }
    total_notifications = Notification.get_notifications_number()
    student=Student.get_student_by_id(data)
    return render_template('studentProfile.html', student=student, total_notifications=total_notifications)

@app.route('/student/update/profile/pic', methods = ['POST'])
def updateStudentProfilePic():
    if 'student_id' not in session:
        return redirect('/student')
    if 'profilePicStudent' not in request.files:
        flash('Please upload an image', 'profilePicStudent')
        return redirect(request.referrer)
    profile = request.files['profilePicStudent']
    if not allowed_file(profile.filename):
        flash('The file should be in png, jpg or jpeg format!', 'profilePicStudent')
        return redirect(request.referrer)
    if profile and allowed_file(profile.filename):
        filename1 = secure_filename(profile.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename1
        filename1 = time
        profile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        data = {
            'profilePic': filename1,
            'id': session['student_id']
        }
        Student.update_profile_pic(data)
        return redirect(request.referrer)
    return redirect('/student')

@app.route('/student/books', methods=['GET', 'POST'])
def allBooksStudent():
    if request.method == 'GET':
        if 'student_id' not in session:
            return redirect('/student')
        data = {
            'id': session['student_id']
        }
        student=Student.get_student_by_id(data)
        books = Book.get_all_books()
        total_books = Book.get_books_number()
        total_notifications = Notification.get_notifications_number()
        total_pages = (total_books + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('studentViewBooks.html', student=student, books = books, page=page, total_pages=total_pages, total_books=total_books, total_notifications=total_notifications)
    else:
        if 'student_id' not in session:
            return redirect('/student')
        data = {
            'id': session['student_id']
        }
        student=Student.get_student_by_id(data)
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
        total_notifications = Notification.get_notifications_number()
        total_pages = (total_books + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('studentViewBooks.html', student=student, books = books, page=page, total_pages=total_pages, total_books=total_books, total_notifications=total_notifications)

@app.route('/student/book/<int:id>')
def showOneBookStudent(id):
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id'],
        'book_id': id
    }
    student=Student.get_student_by_id(data)
    book = Book.get_book_by_id(data)
    total_notifications = Notification.get_notifications_number()
    return render_template('studentViewOneBook.html', book = book, student = student, total_notifications=total_notifications)

@app.route('/student/download/book/<int:id>')
def downloadBookStudent(id):
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id'],
        'book_id': id
    }
    student=Student.get_student_by_id(data)
    book = Book.get_book_by_id(data)
    total_notifications = Notification.get_notifications_number()
    return render_template('studentDownloadBook.html', book = book, student = student, total_notifications=total_notifications)

@app.route('/student/researches', methods=['GET', 'POST'])
def allResearchesStudent():
    if request.method == 'GET':
        if 'student_id' not in session:
            return redirect('/student')
        data = {
            'id': session['student_id']
        }
        student=Student.get_student_by_id(data)
        researches = Research.get_all_researches()
        total_researches = Research.get_researches_number()
        total_notifications = Notification.get_notifications_number()
        total_pages = (total_researches + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('studentViewResearches.html', student=student, researches = researches, page=page, total_pages=total_pages, total_researches=total_researches, total_notifications=total_notifications)
    else:
        if 'student_id' not in session:
            return redirect('/student')
        data = {
            'id': session['student_id']
        }
        student=Student.get_student_by_id(data)
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
        total_notifications = Notification.get_notifications_number()
        total_pages = (total_researches + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('studentViewResearches.html', student=student, researches = researches, page=page, total_pages=total_pages, total_researches=total_researches, total_notifications=total_notifications)

@app.route('/student/research/<int:id>')
def showOneResearchStudent(id):
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id'],
        'research_id': id
    }
    student=Student.get_student_by_id(data)
    research = Research.get_research_by_id(data)
    
    total_notifications = Notification.get_notifications_number()
    
    return render_template('studentViewOneResearch.html', research = research, student = student, total_notifications=total_notifications)

@app.route('/student/notifications')
def allStudentNotifications():
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id']
    }
    student=Student.get_student_by_id(data)
    notifications=Notification.get_all_notifications()
   
    total_notifications = Notification.get_notifications_number()
    
    total_pages = (total_notifications + 5) // 6
    page = request.args.get('page', 1, type=int)
    return render_template('studentViewNotifications.html', student=student,notifications=notifications,page=page, total_pages=total_pages, total_notifications=total_notifications)

@app.route('/student/notification/<int:id>')
def showOneProperty(id):
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id':session['student_id'],
        'notification_id': id
    }
    student=Student.get_student_by_id(data)
    notification=Student.get_notification_by_id(data)
    total_notifications = Notification.get_notifications_number()
    return render_template('studentViewOneNotification.html', student=student, notification = notification, total_notifications=total_notifications)

@app.route('/student/delete/comment/<int:id>')
def deleteComment(id):
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id':session['student_id'],
        'comment_id': id
    }
    comment = Student.get_comment_by_id(data)
    
    if comment['student_id'] == session['student_id']:
        Student.deleteComment(data)
    return redirect(request.referrer)

@app.route('/student/comments/add/<int:id>', methods = ['POST'])
def createComment(id):
    if 'student_id' not in session:
        return redirect('/student')
    if not Student.validate_notificationComment(request.form):
        return redirect(request.referrer)
    data = {
        'student_id': session['student_id'],
        'notification_id': id,
        'comment': request.form['comment']
    }
    Student.addComment(data)
    return redirect(request.referrer)

@app.route('/student/testimonials/new')
def newTestimonialStudent():
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id']
    }
    student = Student.get_student_by_id(data)
    return render_template('newTestimonialStudent.html', student=student)

@app.route('/student/testimonials/new', methods = ['POST'])
def createTestimonialStudent():
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'id': session['student_id']
    }
    student = Student.get_student_by_id(data)
    if student:
        if not Student.validate_testimonial_student(request.form):
            return redirect(request.referrer)
    data = {
        'comment': request.form['comment'],
        'student_id': session['student_id']
    }
    Student.addTestimonialStudent(data)
    flash('Testimonial created successfully', 'testimonialSuccessCreatedStudent')
    return redirect(request.referrer)

@app.route('/checkout/paypal/student/download/book/<int:id>')
def checkoutPaypalStudentDownloadBook(id):
    if 'student_id' not in session:
        return redirect('/student')
    data = {
        'book_id': id
    }
    
    book = Book.get_book_by_id(data)
    cmimi = book['price']
    
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AdRJOyyK_pDYlXB6f_q70Gx-MvxqJuVQEBN8b0BEdqcHg3hhvBD7Nk0PV6GQ15tCgRk1zrl_gm8baBB2",
            "client_secret": "EKozGHz0v7yAVgFO3iy55DkmJkWxQs6_o2_sO32-_Q3EZDno2DwHM9NzIKBXlQGMsO8MKUfLziZZl3TQ"
        })
        
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "transactions": [{
                "amount": {
                    "total": cmimi,
                    "currency": "USD"  # Adjust based on your currency
                },
                "description": f"Payment for book with ID {id} "
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccessStudentBook', _external=True, book_id=id, cmimi=cmimi),
                "cancel_url": "http://example.com/cancel"
            }
        })
        print(cmimi)

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            
            return redirect(approval_url)
            
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        
        return redirect(request.referrer)

@app.route("/success/student/download/book")
def paymentSuccessStudentBook():
    payment_id = request.args.get('paymentId', '')
    payer_id = request.args.get('PayerID', '')
    try:
        paypalrestsdk.configure({
            "mode": "sandbox", # Change this to "live" when you're ready to go live
            "client_id": "AdRJOyyK_pDYlXB6f_q70Gx-MvxqJuVQEBN8b0BEdqcHg3hhvBD7Nk0PV6GQ15tCgRk1zrl_gm8baBB2",
            "client_secret": "EKozGHz0v7yAVgFO3iy55DkmJkWxQs6_o2_sO32-_Q3EZDno2DwHM9NzIKBXlQGMsO8MKUfLziZZl3TQ"
        })
        payment = paypalrestsdk.Payment.find(payment_id)
        if payment.execute({"payer_id": payer_id}):
            
            
            ammount = request.args.get('cmimi')
            status = 'Paid'
            student_id = session['student_id']
            book_id = request.args.get('book_id')
            data = {
                'ammount': ammount,
                'status': status,
                'student_id': student_id,
                'book_id': book_id
            }
            Student.studentBookPayment(data)
            
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect(f'/student/download/book/{book_id}')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect(f'/student/book/{book_id}')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect(f'/student/book/{book_id}')


@app.route("/cancel/student/payment/book")
def paymentCancelStudentDownloadBook():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/student/books')