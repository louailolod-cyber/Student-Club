# Controller.py
from model import db, Member, Payment, Event, EventParticipant, Project, Response, Announcement
from datetime import datetime, date

# -------------------------
# Members
# -------------------------
def get_all_members():
    return Member.query.order_by(Member.last_name).all()

def get_member_by_id(member_id):
    return Member.query.get(member_id)

def add_member(first_name, last_name, email, role='member', status='active', birth_date=None, password=None):
    # check email unique
    if Member.query.filter_by(email=email).first():
        raise ValueError("Email already exists")
    m = Member(
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        status=status,
        birth_date=birth_date,
        password=password
    )
    db.session.add(m)
    db.session.commit()
    return m

def update_member(member_id, **kwargs):
    m = get_member_by_id(member_id)
    if not m:
        return None
    for k, v in kwargs.items():
        if hasattr(m, k) and v is not None:
            setattr(m, k, v)
    db.session.commit()
    return m

def delete_member(member_id):
    m = get_member_by_id(member_id)
    if not m:
        return None
    db.session.delete(m)
    db.session.commit()
    return m

# -------------------------
# Payments
# -------------------------
def get_all_payments():
    return Payment.query.order_by(Payment.date.desc()).all()

def add_payment(member_id, amount, date_value=None, method='Cash', note=None):
    if date_value is None:
        date_value = date.today()
    p = Payment(member_id=member_id, amount=amount, date=date_value, method=method, note=note)
    db.session.add(p)
    db.session.commit()
    return p

def delete_payment(payment_id):
    p = Payment.query.get(payment_id)
    if not p:
        return None
    db.session.delete(p)
    db.session.commit()
    return p

# -------------------------
# Events
# -------------------------
def get_all_events():
    return Event.query.order_by(Event.date).all()

def get_event_by_id(event_id):
    return Event.query.get(event_id)

def add_event(title, description, date_value, location=None, capacity=0, responsible_member_id=None):
    e = Event(title=title, description=description, date=date_value, location=location, capacity=capacity, responsible_member_id=responsible_member_id)
    db.session.add(e)
    db.session.commit()
    return e

def update_event(event_id, **kwargs):
    e = get_event_by_id(event_id)
    if not e:
        return None
    for k, v in kwargs.items():
        if hasattr(e, k) and v is not None:
            setattr(e, k, v)
    db.session.commit()
    return e

def delete_event(event_id):
    e = get_event_by_id(event_id)
    if not e:
        return None
    db.session.delete(e)
    db.session.commit()
    return e

def register_member_to_event(event_id, member_id):
    # avoid duplicate registration
    exists = EventParticipant.query.filter_by(event_id=event_id, member_id=member_id).first()
    if exists:
        return exists
    ep = EventParticipant(event_id=event_id, member_id=member_id)
    db.session.add(ep)
    db.session.commit()
    return ep

def get_event_participants(event_id):
    return EventParticipant.query.filter_by(event_id=event_id).all()

# -------------------------
# Projects
# -------------------------
def get_all_projects():
    return Project.query.order_by(Project.start_date.desc()).all()

def get_project_by_id(project_id):
    return Project.query.get(project_id)

def add_project(title, description=None, start_date=None, end_date=None, responsible_member_id=None):
    # validate responsible member exists when provided
    if responsible_member_id is not None:
        if not Member.query.get(responsible_member_id):
            raise ValueError(f"Responsible member id {responsible_member_id} not found")
    pr = Project(title=title, description=description, start_date=start_date, end_date=end_date, responsible_member_id=responsible_member_id)
    db.session.add(pr)
    db.session.commit()
    return pr

def update_project(project_id, **kwargs):
    pr = get_project_by_id(project_id)
    if not pr:
        return None
    # validate responsible member id if being updated
    if 'responsible_member_id' in kwargs and kwargs.get('responsible_member_id') is not None:
        if not Member.query.get(kwargs.get('responsible_member_id')):
            raise ValueError(f"Responsible member id {kwargs.get('responsible_member_id')} not found")
    for k, v in kwargs.items():
        if hasattr(pr, k) and v is not None:
            setattr(pr, k, v)
    db.session.commit()
    return pr

def delete_project(project_id):
    pr = get_project_by_id(project_id)
    if not pr:
        return None
    db.session.delete(pr)
    db.session.commit()
    return pr

# -------------------------
# Responses (messages)
# -------------------------
def add_response(content, member_id, target_project_id=None):
    r = Response(content=content, member_id=member_id, target_project_id=target_project_id)
    db.session.add(r)
    db.session.commit()
    return r

# -------------------------
# Announcements
# -------------------------
def get_all_announcements():
    return Announcement.query.order_by(Announcement.date.desc()).all()

def add_announcement(title, content, author=None):
    a = Announcement(title=title, content=content, author=author, date=datetime.utcnow())
    db.session.add(a)
    db.session.commit()
    return a

def get_announcement_by_id(announcement_id):
    return Announcement.query.get(announcement_id)

def delete_announcement(announcement_id):
    a = Announcement.query.get(announcement_id)
    if not a:
        return None
    db.session.delete(a)
    db.session.commit()
    return a
