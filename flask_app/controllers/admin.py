from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt

from flask_app.models.admin import Admin
from flask_app.models.student import Student
from flask_app.models.pedagogue import Pedagogue
from flask_app.models.book import Book
from flask_app.models.research import Research
from flask_app.models.guest import Guest
from flask_app.models.notification import Notification
bcrypt = Bcrypt(app)

from datetime import datetime
from urllib.parse import unquote
UPLOAD_PDF_FOLDER = 'flask_app/static/pdfs'
UPLOAD_IMG_FOLDER = 'flask_app/static/img'
PDF_EXTENSIONS = {'pdf'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_PDF_FOLDER'] = UPLOAD_PDF_FOLDER
app.config['UPLOAD_IMG_FOLDER'] = UPLOAD_IMG_FOLDER

import os
from werkzeug.exceptions import RequestEntityTooLarge

from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from werkzeug.exceptions import HTTPException, NotFound
import urllib.parse

import smtplib


def allowed_file(filename, file_type):
    if file_type == 'pdf':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in PDF_EXTENSIONS
    elif file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in IMAGE_EXTENSIONS
    else:
        return False

@app.route('/')
def indexmain():
    if 'user_id' in session:
        return redirect('/admin')
    students = Student.get_all_students()
    pedagogues = Pedagogue.get_all_pedagogues()
    guests = Guest.get_all_guests()
    student_testimonials = Student.get_all_testimonials_student()
    guest_testimonials = Guest.get_all_testimonials_guest()
    nrBooks=Book.get_books_number()
    nrResearches=Research.get_researches_number()
    return render_template('mainPage.html', students=students, pedagogues=pedagogues, guests=guests, student_testimonials=student_testimonials, guest_testimonials=guest_testimonials, nrBooks=nrBooks, nrResearches=nrResearches)

@app.route('/admin')
def indexadmin():
    if 'user_id' in session:
        return redirect('/admin/dashboard')
    return redirect('/logout')

@app.route('/login/admin')
def loginPageAdmin():
    if 'user_id' in session:
        return redirect('/admin')
    return render_template('adminLogin.html')

@app.route('/login/admin', methods = ['POST'])
def loginAdmin():
    if 'user_id' in session:
        return redirect('/admin')
    if not Admin.validate_admin(request.form):
        return redirect(request.referrer)
    user = Admin.get_admin_by_email(request.form)
    if not user:
        flash('This email doesnt exist', 'emailLoginAdmin')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(user['password'], request.form['password']):
        flash('Incorrect password', 'passwordLoginAdmin')
        return redirect(request.referrer)
    
    session['user_id']= user['id']
    return redirect('/admin/dashboard')

@app.route('/admin/dashboard')
def adminPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    nrOfStudents = Student.get_students_number()
    nrOfResearches = Research.get_researches_number()
    nrOfPedagogues = Pedagogue.get_pedagogues_number()
    nrOfBooks = Book.get_books_number()
    nrOfGuests = Guest.get_guests_number()
    if admin and admin['role'] == 'admin':
        return render_template('adminDashboard.html', loggedUser = admin, nrOfStudents = nrOfStudents, nrOfResearches = nrOfResearches, nrOfPedagogues = nrOfPedagogues, nrOfBooks = nrOfBooks, nrOfGuests=nrOfGuests)
    return redirect('/logout')

@app.route('/admin/student/new')
def newStudent():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('registerStudent.html')
    return redirect('/logout')

@app.route('/admin/register/student', methods = ['POST'])
def registerStudent():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Student.validate_studentRegister(request.form):
            return redirect(request.referrer)
        student = Student.get_student_by_email(request.form)
        if student:
            flash('This account already exists', 'studentEmailRegister')
            return redirect(request.referrer)
        data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'phone': request.form['phone'],
            'studyProgram': request.form['studyProgram'],
            'faculty': request.form['faculty'],
            'dega': request.form['dega'],
            'startAccess': request.form['startAccess'],
            'endAccess': request.form['endAccess'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password']),
            'admin_id': session['user_id']
            
        }
        Student.create_student(data)
        flash('Student created successfully', 'studentSuccessRegister')
        return redirect(request.referrer)
    return redirect('/')

@app.route('/admin/pedagogue/new')
def newPedagogue():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('registerPedagogue.html')
    return redirect('/logout')

@app.route('/admin/register/pedagogue', methods = ['POST'])
def registerPedagogue():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Pedagogue.validate_pedagogueRegister(request.form):
            return redirect(request.referrer)
        pedagogue = Pedagogue.get_pedagogue_by_email(request.form)
        if pedagogue:
            flash('This account already exists', 'pedagogueEmailRegister')
            return redirect(request.referrer)
        data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'phone': request.form['phone'],
            'department': request.form['department'],
            'faculty': request.form['faculty'],
            'position': request.form['position'],
            'title': request.form['title'],
            'email': request.form['email'],
            'password': bcrypt.generate_password_hash(request.form['password']),
            'admin_id': session['user_id']
            
        }
        Pedagogue.create_pedagogue(data)
        flash('Pedagogue created successfully', 'pedagogueSuccessRegister')
        return redirect(request.referrer)
    return redirect('/')

@app.route('/admin/book/new')
def newBook():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('addBook.html')
    return redirect('/logout')

@app.route('/admin/add/book', methods = ['POST'])
def addBook():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Book.validate_book(request.form):
            return redirect(request.referrer)
    if 'coverImage' not in request.files:
        flash('Please upload an image', 'imageCoverBook')
        return redirect(request.referrer)
    coverimage = request.files['coverImage']
    if not allowed_file(coverimage.filename, 'image'):
        flash('The file should be in png, jpg or jpeg format!', 'imageCoverBook')
        return redirect(request.referrer)
    
    if coverimage and allowed_file(coverimage.filename, 'image'):
        filename1 = secure_filename(coverimage.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename1
        filename1 = time
        coverimage.save(os.path.join(app.config['UPLOAD_IMG_FOLDER'], filename1))
    
    if 'bookPdf' not in request.files:
        flash('No file part', 'bookPdfRegister')
        return redirect(request.referrer)
    pdfBook = request.files['bookPdf']
    if not allowed_file(pdfBook.filename, 'pdf'):
        flash('The file should be in pdf format!', 'bookPdfRegister')
        return redirect(request.referrer)
    
    if pdfBook and allowed_file(pdfBook.filename, 'pdf'):
        filename = secure_filename(pdfBook.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename
        filename = time
        pdfBook.save(os.path.join(app.config['UPLOAD_PDF_FOLDER'], filename))
    
    
    data = {
        'title': request.form['title'],
        'author': request.form['author'],
        'description': request.form['description'],
        'nrOfPages': request.form['nrOfPages'],
        'isbn': request.form['isbn'],
        'dateOfPublication': request.form['dateOfPublication'],
        'subjectArea': request.form['subjectArea'],
        'language': request.form['language'],
        'coverImage': filename1,
        'publishingHouse': request.form['publishingHouse'],
        'price': request.form['price'],
        'bookPdf': filename,
        'admin_id': session['user_id']
    }
    Book.create_book(data)
    flash('Book created successfully', 'bookSuccessRegister')
    return redirect(request.referrer)

@app.route('/admin/research/new')
def newResearch():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        return render_template('addResearch.html')
    return redirect('/logout')

@app.route('/admin/add/research', methods = ['POST'])
def addResearch():
    if 'user_id' not in session:
        return redirect('/')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    if admin and admin['role'] == 'admin':
        if not Research.validate_research(request.form):
            return redirect(request.referrer)
 
    if 'researchPdf' not in request.files:
        flash('No file part', 'researchPdfRegister')
        return redirect(request.referrer)
    pdfResearch = request.files['researchPdf']
    if not allowed_file(pdfResearch.filename, 'pdf'):
        flash('The file should be in pdf format!', 'researchPdfRegister')
        return redirect(request.referrer)
    
    if pdfResearch and allowed_file(pdfResearch.filename, 'pdf'):
        filename = secure_filename(pdfResearch.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename
        filename = time
        pdfResearch.save(os.path.join(app.config['UPLOAD_PDF_FOLDER'], filename))
    
    
    data = {
        'title': request.form['title'],
        'author': request.form['author'],
        'publicationDate': request.form['publicationDate'],
        'journalOrConference': request.form['journalOrConference'],
        'doi': request.form['doi'],
        'researchField': request.form['researchField'],
        'researchPdf': filename,
        'language': request.form['language'],
        'admin_id': session['user_id']
    }
    Research.create_research(data)
    flash('Scientific Research created successfully', 'researchSuccessRegister')
    return redirect(request.referrer)

@app.route('/admin/students')
def allStudentsPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    students = Student.get_all_students()
    if admin and admin['role'] == 'admin':
        return render_template('allStudents.html', loggedUser = admin, students = students)
    return redirect('/logout')

@app.route('/admin/guests')
def allGuestssPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    guests = Guest.get_all_guests()
    if admin and admin['role'] == 'admin':
        return render_template('allGuests.html', loggedUser = admin, guests = guests)
    return redirect('/logout')

@app.route('/admin/pedagogues')
def allPedagoguesPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    pedagogues = Pedagogue.get_all_pedagogues()
    if admin and admin['role'] == 'admin':
        return render_template('allPedagogues.html', loggedUser = admin, pedagogues = pedagogues)
    return redirect('/logout')

@app.route('/admin/books')
def allBooksPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    books = Book.get_all_books()
    if admin and admin['role'] == 'admin':
        return render_template('allBooks.html', loggedUser = admin, books = books)
    return redirect('/logout')

@app.route('/admin/researches')
def allResearchesPage():
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id': session['user_id']
    }
    admin = Admin.get_admin_by_id(data)
    researches = Research.get_all_researches()
    if admin and admin['role'] == 'admin':
        return render_template('allResearches.html', loggedUser = admin, researches = researches)
    return redirect('/logout')

@app.route('/admin/delete/book/<int:id>')
def deleteBook(id):
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        
        'book_id': id
    }
    book = Book.get_book_by_id(data)
    
    if book['admin_id'] == session['user_id']:
        Student.deleteDownloadGuestsPaymentBook(data)
        Student.deleteDownloadPaymentBook(data)
        Book.deleteBook(data)
    return redirect(request.referrer)

@app.route('/admin/delete/research/<int:id>')
def deleteResearch(id):
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        'id':session['user_id'],
        'research_id': id
    }
    research = Research.get_research_by_id(data)
    
    if research['admin_id'] == session['user_id']:
        Research.deleteResearch(data)
    return redirect(request.referrer)

@app.route('/admin/delete/student/<int:id>')
def deleteStudent(id):
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
        
        'id': id
    }
    student = Student.get_student_by_id(data)
    
    if student['admin_id'] == session['user_id']:
        Student.deleteStudentTestimonial(data)
        Student.deleteStudentComment(data)
        Student.deleteStudentBookPayment(data)
        Student.deleteStudent(data)
        
    return redirect(request.referrer)

@app.route('/admin/delete/pedagogue/<int:id>')
def deletePedagogue(id):
    if 'user_id' not in session:
        return redirect('/admin')
    data = {
    
        'id': id
    }
    pedagogue = Pedagogue.get_pedagogue_by_id(data)
    print(pedagogue)
    
    if pedagogue['admin_id'] == session['user_id']:
        Pedagogue.deletePedagogueComment(data)
        Pedagogue.deletePedagogue(data)
    return redirect(request.referrer)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.errorhandler(404) 
def invalid_route(e): 
    return render_template('404.html')

@app.route('/contact')
def contact_us():
    return render_template('contact.html')