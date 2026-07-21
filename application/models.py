from application.database import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20)) 
    username=db.Column(db.String(30))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    blacklist=db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship("Booking",backref="user",lazy=True)
    staffprofile = db.relationship("StaffProfile",backref="user",uselist=False)
    userprofile = db.relationship("UserProfile",backref="user", uselist=False)

class UserProfile(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,unique=True)
    phone = db.Column(db.String(15))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(200))
    emergency_contact = db.Column(db.String(15))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)

class  StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    approved = db.Column(db.Boolean,default=False)
    status = db.Column(db.String(20),default="Pending")  
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    treks = db.relationship("Trek",backref="staff",lazy=True)

class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100),nullable=False)
    location = db.Column(db.String(100),nullable=False)
    difficulty = db.Column(db.String(20),nullable=False)
    duration_days = db.Column(db.Integer,nullable=False)
    available_slots = db.Column(db.Integer,nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.String(30),nullable=False)
    end_date = db.Column(db.String(30),nullable=False)
    status = db.Column(db.String(20),default="Pending")
    staff_id = db.Column(db.Integer,db.ForeignKey("staff_profile.id"))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    bookings = db.relationship("Booking",backref="trek",lazy=True,cascade="all, delete-orphan")


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey("trek.id"),nullable=False)
    booking_date = db.Column(db.DateTime,default=datetime.utcnow)
    status = db.Column(db.String(20),default="Booked")
    participants = db.Column(db.Integer,default=1)
    remarks = db.Column(db.Text)

