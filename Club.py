# Club.py
from flask import Flask,render_template, redirect, url_for, request, flash, session
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
    payments=Controller.get_all_payments()
    return render_template('home.html',
                           total_members=len(members),
                           overdue_payments=len(payments),
                           upcoming_events=len(events),
                           notifications_count=len(announcements),
                           events=events)


def _is_admin():
    return session.get('user_role') == 'admin'

def _is_logged_in():
    return 'user_role' in session

# ---- Members ----
@app.route('/members')
def members_list():
    members = Controller.get_all_members()
    return render_template('members.html', members=members)

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
    if request.method == 'POST':
        try:
            Controller.add_member(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                email=request.form['email'],
                role=request.form.get('role', 'member'),
                status=request.form.get('status', 'active'),
                birth_date=datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
            )
            flash('Member added', 'success')
            return redirect(url_for('members_list'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('member_form.html', member=None)

@app.route('/members/edit/<int:member_id>', methods=['GET', 'POST'])
def edit_member(member_id):
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
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
                                 status=request.form.get('status', member.status),
                                    birth_date= datetime.strptime(request.form.get('birth_date'), '%Y-%m-%d').date() if request.form.get('birth_date') else None
                                 )
        flash('Member updated', 'success')
        return redirect(url_for('members_list'))
    return render_template('member_form.html', member=member)

@app.route('/members/delete/<int:member_id>')
def delete_member(member_id):
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
    Controller.delete_member(member_id)
    flash('Member deleted', 'info')
    return redirect(url_for('members_list'))

# ---- Payments ----
@app.route('/payments') #@ is a decorator
def payments_list():
    # payments form accessible to logged-in members or admin
    if not _is_logged_in():
        flash('Please login to add payments', 'danger')
        return redirect(url_for('error'))
    return render_template('payment_form.html')

@app.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    if request.method == 'POST':
        Controller.add_payment(int(request.form['member_id']), float(request.form['amount']), method=request.form.get('method','Cash'))
        flash('Payment added', 'success')
        if _is_admin():
         return redirect(url_for('payments_table'))
    return render_template('payment_form.html')

@app.route('/payments/delete/<int:payment_id>')
def delete_payment(payment_id):
    Controller.delete_payment(payment_id)
    flash('Payment deleted', 'info')
    return redirect(url_for('payments_table'))


@app.route('/payments/list')
def payments_table():
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
    payments = Controller.get_all_payments()
    return render_template('payments_list.html', payments=payments)

# ---- Events ----
@app.route('/events')
def events_list():
    events = Controller.get_all_events()
    # events listing visible to everyone (including members)
    return render_template('events.html', events=events)

@app.route('/events/add', methods=['GET','POST'])
def add_event():
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
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
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
    Controller.delete_event(event_id)
    flash('Event deleted', 'info')
    return redirect(url_for('events_list'))

# ---- Announcements ----
@app.route('/announcements')
def announcements_list():
    if not _is_logged_in():
        flash('Please login to view announcements', 'danger')
        return redirect(url_for('error'))
    announcements = Controller.get_all_announcements()
    return render_template('announcements.html', announcements=announcements)

@app.route('/announcements/add', methods=['GET','POST'])
def add_announcement():
    if not _is_logged_in():
        flash('Please login to add announcements', 'danger')
        return redirect(url_for('error'))
    if request.method == 'POST':
        Controller.add_announcement(request.form['title'], request.form['content'], request.form.get('author'))
        flash('Announcement published', 'success')
        return redirect(url_for('announcements_list'))
    return render_template('announcement_form.html')


@app.route('/announcements/<int:announcement_id>')
def view_announcement(announcement_id):
    if not _is_logged_in():
        flash('Please login to view announcements', 'danger')
        return redirect(url_for('error'))
    a = Controller.get_announcement_by_id(announcement_id)
    if not a:
        flash('Announcement not found', 'danger')
        return redirect(url_for('announcements_list'))
    return render_template('announcement_detail.html', announcement=a)


@app.route('/announcements/delete/<int:announcement_id>')
def delete_announcement(announcement_id):
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
    Controller.delete_announcement(announcement_id)
    flash('Announcement deleted', 'info')
    return redirect(url_for('announcements_list'))

# ---- Projects ----
@app.route('/projects')
def projects_list():
    if not _is_logged_in():
        flash('Please login to view projects', 'danger')
        return redirect(url_for('error'))
    projects = Controller.get_all_projects()
    return render_template('projects.html', projects=projects)

@app.route('/projects/add', methods=['GET','POST'])
def add_project():
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
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
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
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
    if not _is_admin():
        flash('Admin access required', 'danger')
        return redirect(url_for('error'))
    Controller.delete_project(project_id)
    flash('Project deleted', 'info')
    return redirect(url_for('projects_list'))

# ---- Profile / logout (simple placeholders) ----
@app.route('/profile')
def profile():
    if not _is_logged_in():
        flash('Please login first', 'danger')
        return redirect(url_for('error'))
    role = session.get('user_role')
    user_id = session.get('user_id')
    user = None
    if role == 'member' and user_id:
        user = Controller.get_member_by_id(user_id)
    return render_template('profile.html', user=user, role=role)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('home'))


# ---- Authentication: login / signup ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')
        secret = request.form.get('secret')
        # admin shortcut
        if identifier == 'admin' and secret == '12345678':
            session['user_role'] = 'admin'
            session['user_id'] = None
            flash('Logged in as admin', 'success')
            return redirect(url_for('home'))
        # try member login by email + birth_date
        m = Controller.get_member_by_email(identifier)
        if not m:
            flash('Member not found', 'danger')
            return render_template('login.html')
        # compare birth_date
        try:
            from datetime import datetime as _dt
            bd = _dt.strptime(secret, '%Y-%m-%d').date()
        except Exception:
            flash('Invalid date format, use YYYY-MM-DD', 'danger')
            return render_template('login.html')
        if m.birth_date and m.birth_date == bd:
            session['user_role'] = 'member'
            session['user_id'] = m.id
            flash('Logged in', 'success')
            return redirect(url_for('home'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        birth = request.form.get('birth_date')
       
        try:
            m = Controller.add_member(first_name, last_name, email, birth_date=datetime.strptime(birth, '%Y-%m-%d').date())
            session['user_role'] = 'member'
            session['user_id'] = m.id
            flash('Account created and logged in', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('signup.html')
@app.route('/error')
def error():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
