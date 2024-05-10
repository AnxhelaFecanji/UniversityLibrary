from flask_app import app
from flask import render_template, redirect, flash, session, request, url_for
from flask_bcrypt import Bcrypt
from flask_app.models.student import Student
from flask_app.models.book import Book
from flask_app.models.research import Research
from flask_app.models.notification import Notification
from flask_app.models.guest import Guest
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

@app.route('/guest')
def indexGuest():
    if 'guest_id' in session:
        return redirect('/guest/profile')
    return redirect('/logout')

@app.route('/loginRegister/guest')
def loginRegisterPageGuest():
    if 'guest_id' in session:
        return redirect('/guest')
    return render_template('guestLoginRegister.html')

@app.route('/register/guest', methods = ['POST'])
def registerGuest():
    if 'guest_id' in session:
        return redirect('/guest')
    if not Guest.validate_guestRegister(request.form):
        return redirect(request.referrer)
    guest = Guest.get_guest_by_email(request.form)
    if guest:
        flash('This account already exists', 'guestEmailRegister')
        return redirect(request.referrer)
    
    data = {
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'role_type': request.form['role_type'],
        'email': request.form['email'],
        'password': bcrypt.generate_password_hash(request.form['password'])
    }
    session['guest_id'] = Guest.create_guest(data)
    return redirect('/checkout/paypal/register/guest')

@app.route('/login/guest', methods = ['POST'])
def loginGuest():
    if 'guest_id' in session:
        return redirect('/guest')
    if not Guest.validate_guest(request.form):
        return redirect(request.referrer)
    guest = Guest.get_guest_by_email(request.form)
    if not guest:
        flash('This email doesnt exist', 'emailLoginGuest')
        return redirect(request.referrer)
    if not bcrypt.check_password_hash(guest['password'], request.form['password']):
        flash('Incorrect password', 'passwordLoginGuest')
        return redirect(request.referrer)
    session['guest_id']= guest['id']
    return redirect('/guest/profile')

@app.route('/guest/profile')
def profileGuest():
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id']
    }
    
    guest=Guest.get_guest_by_id(data)
    return render_template('guestProfile.html', guest=guest)

@app.route('/guest/update/profile/pic', methods = ['POST'])
def updateGuestProfilePic():
    if 'guest_id' not in session:
        return redirect('/guest')
    if 'profilePicGuest' not in request.files:
        flash('Please upload an image', 'profilePicGuest')
        return redirect(request.referrer)
    profile = request.files['profilePicGuest']
    if not allowed_file(profile.filename):
        flash('The file should be in png, jpg or jpeg format!', 'profilePicGuest')
        return redirect(request.referrer)
    if profile and allowed_file(profile.filename):
        filename1 = secure_filename(profile.filename)
        time = datetime.now().strftime("%d%m%Y%S%f")
        time += filename1
        filename1 = time
        profile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
        data = {
            'profilePic': filename1,
            'id': session['guest_id']
        }
        Guest.update_profile_pic_guest(data)
        return redirect(request.referrer)
    return redirect('/guest')

@app.route('/guest/books', methods=['GET', 'POST'])
def allBooksGuest():
    if request.method == 'GET':
        if 'guest_id' not in session:
            return redirect('/guest')
        data = {
            'id': session['guest_id']
        }
        guest=Guest.get_guest_by_id(data)
        books = Book.get_all_books()
        total_books = Book.get_books_number()
        total_pages = (total_books + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('guestViewBooks.html', guest=guest, books = books, page=page, total_pages=total_pages, total_books=total_books)
    else:
        if 'guest_id' not in session:
            return redirect('/guest')
        data = {
            'id': session['guest_id']
        }
        guest=Guest.get_guest_by_id(data)
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
        return render_template('guestViewBooks.html', guest=guest, books = books, page=page, total_pages=total_pages, total_books=total_books)
        

@app.route('/guest/book/<int:id>')
def showOneBookGuest(id):
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id'],
        'book_id': id
    }
    guest=Guest.get_guest_by_id(data)
    book = Book.get_book_by_id(data)
    
    return render_template('guestViewOneBook.html', book = book, guest = guest)

@app.route('/guest/download/book/<int:id>')
def downloadBookt(id):
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id'],
        'book_id': id
    }
    guest=Guest.get_guest_by_id(data)
    book = Book.get_book_by_id(data)
    
    return render_template('downloadBookGuest.html', book = book, guest = guest)

@app.route('/guest/researches', methods=['GET', 'POST'])
def allResearchesGuest():
    if request.method == 'GET':
        if 'guest_id' not in session:
            return redirect('/guest')
        data = {
            'id': session['guest_id']
        }
        guest=Guest.get_guest_by_id(data)
        researches = Research.get_all_researches()
        total_researches = Research.get_researches_number()
        total_pages = (total_researches + 5) // 6
        page = request.args.get('page', 1, type=int)
        return render_template('guestViewResearches.html', guest=guest, researches = researches, page=page, total_pages=total_pages, total_researches=total_researches)
    else:
        if 'guest_id' not in session:
            return redirect('/guest')
        data = {
            'id': session['guest_id']
        }
        guest=Guest.get_guest_by_id(data)
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
        return render_template('guestViewResearches.html', guest=guest, researches = researches, page=page, total_pages=total_pages, total_researches=total_researches)

@app.route('/guest/research/<int:id>')
def showOneResearchGuest(id):
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id'],
        'research_id': id
    }
    guest=Guest.get_guest_by_id(data)
    research = Research.get_research_by_id(data)
    
    return render_template('guestViewOneResearch.html', research = research, guest = guest)

@app.route('/make/donation')
def makeDonation():
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id']
    }
    guest=Guest.get_guest_by_id(data)
    
    return render_template('makeDonation.html', guest = guest)


@app.route('/checkout/paypal', methods=['GET', 'POST'])
def checkoutPaypal():
    if 'guest_id' not in session:
        return redirect('/guest')
    cmimi = request.form['ammount']
    
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
                "description": f"Donacion per kerkimin shkencor."
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccess', _external=True, cmimi=cmimi),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)

@app.route("/success", methods=["GET"])
def paymentSuccess():
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
            guest_id = session['guest_id']
            data = {
                'ammount': ammount,
                'status': status,
                'guest_id': guest_id
            }
            Guest.makeDonation(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/guest/profile')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/businessOwner')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/make/payment')


@app.route("/cancel", methods=["GET"])
def paymentCancel():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/make/donation')


@app.route('/checkout/paypal/register/guest')
def checkoutPaypalRegisterGuest():
    if 'guest_id' not in session:
        return redirect('/guest')
    cmimi = 20
    
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
                "description": f"Pagesa e regjistrimit."
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccessGuest', _external=True, cmimi=cmimi),
                "cancel_url": "http://example.com/cancel"
            }
        })

        if payment.create():
            approval_url = next(link.href for link in payment.links if link.rel == 'approval_url')
            return redirect(approval_url)
        else:
            flash('Something went wrong with your payment', 'creditCardDetails')
            return redirect(request.referrer)
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'creditCardDetails')
        return redirect(request.referrer)

@app.route("/success/guest", methods=["GET"])
def paymentSuccessGuest():
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
            guest_id = session['guest_id']
            data = {
                'ammount': ammount,
                'status': status,
                'guest_id': guest_id
            }
            Guest.registrationPayment(data)
           
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect('/guest/profile')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect('/loginRegister/guest')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect('/loginRegister/guest')


@app.route("/cancel/payment", methods=["GET"])
def paymentCancelGuest():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/loginRegister/guest')

@app.route('/guest/testimonials/new')
def newTestimonial():
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id']
    }
    guest = Guest.get_guest_by_id(data)
    return render_template('newTestimonialGuest.html',guest=guest)

@app.route('/guest/testimonials/new', methods = ['POST'])
def createTestimonial():
    if 'guest_id' not in session:
        return redirect('/guest')
    data = {
        'id': session['guest_id']
    }
    guest = Guest.get_guest_by_id(data)
    if guest:
        if not Guest.validate_testimonial_guest(request.form):
            return redirect(request.referrer)
    data = {
        'testimonial': request.form['testimonial'],
        'guest_id': session['guest_id']
    }
    Guest.addTestimonialGuest(data)
    flash('Testimonial created successfully', 'testimonialSuccessCreated')
    return redirect(request.referrer)

@app.route('/checkout/paypal/download/book/<int:id>')
def checkoutPaypalDownloadBook(id):
    if 'guest_id' not in session:
        return redirect('/guest')
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
                "description": f"Payment for book with ID {id}"
            }],
            "redirect_urls": {
                "return_url": url_for('paymentSuccessBook', _external=True, book_id=id, cmimi=cmimi),
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

@app.route("/success/guest/download/book")
def paymentSuccessBook():
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
            guest_id = session['guest_id']
            book_id = request.args.get('book_id')
            data = {
                'ammount': ammount,
                'status': status,
                'guest_id': guest_id,
                'book_id': book_id
            }
            Guest.bookPayment(data)
            
            flash('Your payment was successful!', 'paymentSuccessful')
            return redirect(f'/guest/download/book/{book_id}')
        else:
            flash('Something went wrong with your payment', 'paymentNotSuccessful')
            return redirect(f'/guest/book/{book_id}')
    except paypalrestsdk.ResourceNotFound as e:
        flash('Something went wrong with your payment', 'paymentNotSuccessful')
        return redirect(f'/guest/book/{book_id}')


@app.route("/cancel/payment/book")
def paymentCancelDownloadBook():
    flash('Payment was canceled', 'paymentCanceled')
    return redirect('/guest/books')


