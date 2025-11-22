# Club.py
# Club.py
from flask import Flask, render_template, redirect, url_for, request, flash
from model import db, Member, Payment, Event, Project, Announcement
import Controller
from datetime import datetime

app = Flask(__name__)
app.secret_key = "dev-secret"  # change for production

# Config DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///club.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# Home
@app.route('/')
@app.route('/home')
def home():
    members = Controller.get_all_members()
    events = Controller.get_all_events()
    announcements = Controller.get_all_announcements()
    return render_template('home.html',
                           total_members=len(members),
                           overdue_payments=0,
                           upcoming_events=len(events),
                           notifications_count=len(announcements),
                           events=events)

# ---- Members ----
@app.route('/members')
def members_list():
    members = Controller.get_all_members()
    return render_template('members.html', members=members)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        try:
            Controller.add_member(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                role=request.form.get('role', 'member'),
                status=request.form.get('status', 'active')
            )
            flash('Member added', 'success')
            return redirect(url_for('members_list'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('member_form.html', member=None)

@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    member = Controller.get_member_by_id(member_id)
    if not member:
        flash('Member not found', 'danger')
        return redirect(url_for('members_list'))
    if request.method == 'POST':
        Controller.update_member(member_id,
                                 first_name=request.form['first_name'],
                                 last_name=request.form['last_name'],
                                 email=request.form['email'],
                                 role=request.form.get('role', member.role),
                                 status=request.form.get('status', member.status))
        flash('Member updated', 'success')
        return redirect(url_for('members_list'))
    return render_template('member_form.html', member=member)

@app.route('/members/delete/<int:member_id>')
def delete_member(member_id):
    Controller.delete_member(member_id)
    flash('Member deleted', 'info')
    return redirect(url_for('members_list'))

# ---- Payments ----
@app.route('/payments')
def payments_list():
    return render_template('payment_form.html')

@app.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        Controller.add_payment(int(request.form['member_id']), float(request.form['amount']), method=request.form.get('method','Cash'))
        flash('Payment added', 'success')
        return redirect(url_for('payments_table'))
    return render_template('payment_form.html')

@app.route('/payments/delete/<int:payment_id>')
def delete_payment(payment_id):
    Controller.delete_payment(payment_id)
    flash('Payment deleted', 'info')
    return redirect(url_for('payments_table'))


@app.route('/payments/list')
def payments_table():
    payments = Controller.get_all_payments()
    return render_template('payments_list.html', payments=payments)

# ---- Events ----
@app.route('/events')
def events_list():
    events = Controller.get_all_events()
    return render_template('events.html', events=events)

@app.route('/events/add', methods=['GET','POST'])
def add_event():
    if request.method == 'POST':
        date_value = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        Controller.add_event(request.form['title'], request.form.get('description',''), date_value, request.form.get('location',''), int(request.form.get('capacity',0)))
        flash('Event created', 'success')
        return redirect(url_for('events_list'))
    return render_template('event_form.html', event=None)

@app.route('/events/register', methods=['POST'])
def register_event():
    Controller.register_member_to_event(int(request.form['event_id']), int(request.form['member_id']))
    flash('Registered to event', 'success')
    return redirect(url_for('events_list'))


@app.route('/events/delete/<int:event_id>')
def delete_event(event_id):
    Controller.delete_event(event_id)
    flash('Event deleted', 'info')
    return redirect(url_for('events_list'))

# ---- Announcements ----
@app.route('/announcements')
def announcements_list():
    announcements = Controller.get_all_announcements()
    return render_template('announcements.html', announcements=announcements)

@app.route('/announcements/add', methods=['GET','POST'])
def add_announcement():
    if request.method == 'POST':
        Controller.add_announcement(request.form['title'], request.form['content'], request.form.get('author'))
        flash('Announcement published', 'success')
        return redirect(url_for('announcements_list'))
    return render_template('announcement_form.html')


@app.route('/announcements/<int:announcement_id>')
def view_announcement(announcement_id):
    a = Controller.get_announcement_by_id(announcement_id)
    if not a:
        flash('Announcement not found', 'danger')
        return redirect(url_for('announcements_list'))
    return render_template('announcement_detail.html', announcement=a)


@app.route('/announcements/delete/<int:announcement_id>')
def delete_announcement(announcement_id):
    Controller.delete_announcement(announcement_id)
    flash('Announcement deleted', 'info')
    return redirect(url_for('announcements_list'))

# ---- Projects ----
@app.route('/projects')
def projects_list():
    projects = Controller.get_all_projects()
    return render_template('projects.html', projects=projects)

@app.route('/projects/add', methods=['GET','POST'])
def add_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description') or None
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        responsible = request.form.get('responsible_member_id')
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        except Exception:
            sd = None
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        except Exception:
            ed = None
        resp_id = int(responsible) if responsible else None
        try:
            Controller.add_project(title, description=description, start_date=sd, end_date=ed, responsible_member_id=resp_id)
            flash('Project created', 'success')
            return redirect(url_for('projects_list'))
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('projects_form.html')
    return render_template('projects_form.html')


@app.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Controller.get_project_by_id(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('projects_list'))
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description') or None
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        responsible = request.form.get('responsible_member_id')
        try:
            sd = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        except Exception:
            sd = None
        try:
            ed = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        except Exception:
            ed = None
        resp_id = int(responsible) if responsible else None
        try:
            Controller.update_project(project_id, title=title, description=description, start_date=sd, end_date=ed, responsible_member_id=resp_id)
            flash('Project updated', 'success')
            return redirect(url_for('projects_list'))
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('projects_form.html', project=project)
    return render_template('projects_form.html', project=project)


@app.route('/projects/delete/<int:project_id>')
def delete_project(project_id):
    Controller.delete_project(project_id)
    flash('Project deleted', 'info')
    return redirect(url_for('projects_list'))

# ---- Profile / logout (simple placeholders) ----
@app.route('/profile')
def profile():
    return "<h1>Profile page (to implement)</h1>"

@app.route('/logout')
def logout():
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
