# model.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)   # optional for now
    birth_date = db.Column(db.Date, nullable=True)
    role = db.Column(db.String(50), nullable=False, default='member')
    status = db.Column(db.String(50), nullable=False, default='active')
    join_date = db.Column(db.Date, nullable=False, default=date.today)

    payments = db.relationship('Payment', backref='member', cascade='all, delete-orphan')
    event_participations = db.relationship('EventParticipant', backref='member', cascade='all, delete-orphan')
    responses = db.relationship('Response', backref='member', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='responsible_member', cascade='all, delete-orphan')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Member {self.id} {self.email}>"

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    method = db.Column(db.String(50), nullable=True)
    note = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Payment {self.id} {self.amount}>"

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    responsible_member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)

    participants = db.relationship('EventParticipant', backref='event', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Event {self.id} {self.title}>"

class EventParticipant(db.Model):
    __tablename__ = 'event_participants'
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<EventParticipant e{self.event_id}-m{self.member_id}>"

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    responsible_member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=True)

    def __repr__(self):
        return f"<Project {self.id} {self.title}>"

class Response(db.Model):
    __tablename__ = 'responses'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    target_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)

    def __repr__(self):
        return f"<Response {self.id}>"

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Announcement {self.id} {self.title}>"
