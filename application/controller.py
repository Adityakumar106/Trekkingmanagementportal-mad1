from flask import render_template,redirect,session,request,flash;
from datetime import datetime;
from sqlalchemy import or_
from werkzeug.security import generate_password_hash,check_password_hash;
from application.models import db, User,StaffProfile,Trek,Booking,UserProfile
from app import app

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
# register
def register():
    if request.method=='POST':
     
     data = request.form
     if not data.get('username')or not data.get('email')or not data.get('password')or not data.get('role'):
         return "error: all data is required",400
     already_user= User.query.filter_by(email=data['email']).first()
     if already_user:
            return "error : Email already registered", 409
     hash_pass=generate_password_hash(data['password'])
     user = User(
        username=data['username'],
        email=data['email'],
        role=data['role'],
        password=hash_pass
    )
     db.session.add(user)
     db.session.commit()
     
     if user.role == "user":
      user_profile = UserProfile(
        user_id=user.id,
      )
      db.session.add(user_profile)
      db.session.commit()
     if user.role == "staff":
      staff_profile = StaffProfile(
        user_id=user.id,
        approved=False,
        status="Pending"
      )

      db.session.add(staff_profile)
      db.session.commit()

     
     return redirect('/login')
    return render_template('register.html')
# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
     
     data = request.form
     if not data.get('email')or not data.get('password'):
         return "error: all data is required",400
     
     user = User.query.filter_by(email=data['email'],blacklist=False).first()
     if not user:
         return "error User not found or blacklisted please contact support@bytrek.com"
     if not check_password_hash(user.password, data['password']):
            return "errorInvalid password", 401
     
     session['id'] = user.id
     session['role'] = user.role
     if user.role == 'staff':
        return redirect('/staff')
     elif user.role == 'admin':
            return redirect('/admindashboard')
     elif user.role == 'user':
            return redirect('/user')
     else:
            return "doen't exist", 403

    return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.clear()   
    return redirect('/login')

@app.route('/admindashboard')
def admin():
    if session.get('role') != 'admin': 
     return redirect('/login')
    user=User.query.filter_by(role="user").all()
    staff=User.query.filter_by(role="staff").all()
    
    staff_profile=StaffProfile.query.all()

    trek=Trek.query.all()
    total_users = User.query.filter_by(role="user").count()
    total_staffs = StaffProfile.query.filter_by(approved=True).count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    return render_template('admin.html',user=user,staff_profile=staff_profile,staff=staff,
        trek=trek,total_users=total_users,total_staffs=total_staffs,total_treks=total_treks,total_bookings=total_bookings)

@app.route('/admin/trek/add', methods=['GET', 'POST'])
def add_trek():

    if session.get('role') != 'admin':
        return redirect('/login')

    if request.method == 'POST':

        trek = Trek(
            trek_name=request.form['trek_name'],
            location=request.form['location'],
            difficulty=request.form['difficulty'],
            duration_days=int(request.form['duration_days']),
            available_slots=int(request.form['available_slots']),
            description=request.form['description'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            status=request.form['status'],
            staff_id=request.form['staff_id'] or None
        )

        db.session.add(trek)
        db.session.commit()

        return redirect('/admindashboard')

    staffs = StaffProfile.query.filter_by(
        approved=True
    ).all()

    return render_template(
        'trekaddedit.html',
        trek=None,
        staffs=staffs
    )


@app.route('/admin/trek/edit/<int:trek_id>', methods=['GET', 'POST'])
def edit_trek(trek_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':

        trek.trek_name = request.form['trek_name']
        trek.location = request.form['location']
        trek.difficulty = request.form['difficulty']
        trek.duration_days = int(request.form['duration_days'])
        trek.available_slots = int(request.form['available_slots'])
        trek.description = request.form['description']
        trek.start_date = request.form['start_date']
        trek.end_date = request.form['end_date']
        trek.status = request.form['status']
        trek.staff_id = request.form['staff_id'] or None

        db.session.commit()

        return redirect('/admindashboard')

    staffs = StaffProfile.query.filter_by(
        approved=True
    ).all()

    return render_template(
        'trekaddedit.html',
        trek=trek,
        staffs=staffs
    )     

@app.route('/user')
def user():
    if session.get('role')!="user":
        return redirect('/login')
    user = User.query.get(session.get('id'))
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    status = request.args.get('status', '')
    treks = Trek.query
    if search:
        treks = treks.filter( or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%")
            )
        )
    if difficulty:
        treks = treks.filter( Trek.difficulty == difficulty)

    if status:
        treks = treks.filter( Trek.status == status)
    treks = treks.all()

    return render_template(
        'userdash.html',user=user,treks=treks, search=search,difficulty=difficulty,status=status)

@app.route('/staff')
def staff():
    if session.get('role')!="staff":
        return redirect('/login')
    user = User.query.get(session['id'])
    staff_profile = StaffProfile.query.filter_by(user_id=user.id,approved=True).first()
    if not staff_profile:
        return "Waiting for admin approval"
    assigned_treks = Trek.query.filter_by(staff_id=staff_profile.id).all()
    total_assigned_treks = len(assigned_treks)
    open_treks = Trek.query.filter_by(staff_id=staff_profile.id,status="Open").count()
    total_participants = 0

    for trek in assigned_treks:
        total_participants += len(trek.bookings)

    return render_template('staffdash.html', staff=user, treks=assigned_treks,total_assigned_treks=total_assigned_treks,
        open_treks=open_treks,total_participants=total_participants)
    
@app.route('/admin/user/<int:user_id>/blacklist')
def blacklist_user(user_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    user = User.query.get_or_404(user_id)

    user.blacklist = True

    db.session.commit()

    return redirect('/admindashboard')

@app.route('/admin/staff/<int:user_id>/approve')
def approve_staff(user_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    staff_profile = StaffProfile.query.filter_by(
        user_id=user_id
    ).first_or_404()

    staff_profile.approved = True
    staff_profile.status = "Approved"

    db.session.commit()

    return redirect('/admindashboard')

@app.route('/admin/staff/<int:user_id>/reject')
def reject_staff(user_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    staff_profile = StaffProfile.query.filter_by(
        user_id=user_id
    ).first_or_404()

    staff_profile.approved = False
    staff_profile.status = "Rejected"

    db.session.commit()

    return redirect('/admindashboard')



@app.route('/admin/trek/<int:trek_id>/cancel')
def cancel_trek(trek_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)
    
    trek.status = "Cancelled"
    
    db.session.commit()
    return redirect('/admindashboard')

@app.route('/staff/profile', methods=['GET', 'POST'])
def staff_profile():

    if session.get('role') != 'staff':
        return redirect('/login')

    user = User.query.get(session.get('id'))

    if not user:
        return redirect('/login')

    profile = StaffProfile.query.filter_by(
        user_id=user.id
    ).first()

    if request.method == 'POST':

        profile.contact_number = request.form['contact_number']
        profile.address = request.form['address']

        db.session.commit()

        return redirect('/staff/profile')

    total_assigned_treks = Trek.query.filter_by(
        staff_id=profile.id
    ).count()

    total_started_treks = Trek.query.filter(
        Trek.staff_id == profile.id,
        Trek.status.in_(["Open", "Completed"])
    ).count()

    return render_template(
        'staffprofile.html',
        user=user,
        profile=profile,
        total_assigned_treks=total_assigned_treks,
        total_started_treks=total_started_treks
    )

@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():

    if session.get('role') != 'user':
        return redirect('/login')

    user = User.query.get(session.get('id'))

    profile = UserProfile.query.filter_by(
        user_id=user.id
    ).first()

    if not profile:
        profile = UserProfile(
            user_id=user.id
        )

        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':

        profile.phone = request.form['phone']
        profile.age = request.form['age']
        profile.gender = request.form['gender']
        profile.address = request.form['address']
        profile.emergency_contact = request.form['emergency_contact']

        db.session.commit()

        return redirect('/user/profile')

    return render_template(
        'userprofile.html',
        user=user,
        profile=profile
    )



@app.route('/admin/search')
def admin_search():

    if session.get('role') != 'admin':
        return redirect('/login')

    q = request.args.get('q', '').strip()

    users = []
    staffs = []
    treks = []

    if q:

        users = User.query.filter(
            User.role == "user",
            User.username.ilike(f"%{q}%")
        ).all()

        staffs = User.query.filter(
            User.role == "staff",
            User.username.ilike(f"%{q}%")
        ).all()

        treks = Trek.query.filter(
            Trek.trek_name.ilike(f"%{q}%")
        ).all()

    return render_template(
        'adminsearch.html',
        q=q,
        users=users,
        staffs=staffs,
        treks=treks
    )
@app.route('/admin/user/<int:user_id>')
def user_details(user_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    user = User.query.get_or_404(user_id)

    return render_template(
        'userdetails.html',
        user=user
    )

@app.route('/admin/staff/<int:staff_id>')
def staff_details(staff_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    staff = User.query.get_or_404(staff_id)

    return render_template(
        'staffdetails.html',
        staff=staff
    )

@app.route('/admin/trek/<int:trek_id>')
def trek_details(trek_id):

    if session.get('role') != 'admin':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    return render_template(
        'trekdetails.html',
        trek=trek
    )

@app.route('/staff/<int:trek_id>/manage', methods=['GET', 'POST'])
def manage_trek(trek_id):

    if session.get('role') != 'staff':
        return redirect('/login')

    user = User.query.get(session['id'])

    if not user.staffprofile:
        return redirect('/staff')

    trek = Trek.query.get_or_404(trek_id)

    
    if trek.staff_id != user.staffprofile.id:
        return "Unauthorized", 403

    if request.method == 'POST':

        trek.available_slots = int(
            request.form['available_slots']
        )

        trek.status = request.form['status']

        db.session.commit()

        return redirect('/staff')

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        'StaffTrekmanage.html',
        trek=trek,
        bookings=bookings
    )

@app.route('/staff/trek/<int:trek_id>/status', methods=['POST'])
def updatestatus(trek_id):

    if session.get('role') != 'staff':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    trek.status = request.form['status']

    db.session.commit()

    return redirect(f'/staff/{trek_id}/manage')

@app.route('/staff/<int:trek_id>/start')
def start_trek(trek_id):

    if session.get('role') != 'staff':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    trek.status = "Started"

    db.session.commit()

    return redirect(f'/staff/{trek_id}/manage')

@app.route('/staff/<int:trek_id>/complete')
def complete_trek(trek_id):

    if session.get('role') != 'staff':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    trek.status = "Closed"

    db.session.commit()

    return redirect(f'/staff/{trek_id}/manage')

@app.route('/mybookings')
def my_bookings():

    if session.get('role') != 'user':
        return redirect('/login')

    bookings = Booking.query.filter_by(
        user_id=session['id']
    ).all()

    return render_template(
        'userbooking.html',
        bookings=bookings
    )
@app.route('/trek/<int:trek_id>' , methods=['GET', 'POST']) 
def user_trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id) 
    
    
    return render_template( 'usertrekdetail.html', trek=trek )


@app.route('/booktrek/<int:trek_id>')
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    user_id = session['id']

    existing_booking = Booking.query.filter_by(
        user_id=user_id,
        trek_id=trek.id
    ).first()

    if existing_booking:
        return "Already booked"

    
    if trek.available_slots <= 0:
        return "No slots available"

    booking = Booking(
        user_id=user_id,
        trek_id=trek.id,
        participants=1,
        status="Booked"
    )

    db.session.add(booking)

    trek.available_slots -= 1

    db.session.commit()

    return "Trek has been booked successfully"


@app.route("/admin/trek/<int:trek_id>/bookings")
def admin_view_bookings(trek_id):

    if session.get("role") != "admin":
        flash("Unauthorized access", "danger")
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)
    
    bookings = Booking.query.filter_by(
        trek_id=trek_id
    ).all()

    return render_template(
        "viewbooking.html",
        trek=trek,
        bookings=bookings,
        
    )
