from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from datetime import datetime
from zoneinfo import ZoneInfo

import os

ph = PasswordHasher()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'

app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-dev-only-key")
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_HASH = os.environ.get("ADMIN_PASSWORD_HASH") or ph.hash("local-dev-password")

# Temporary debug line - check your Render "Logs" tab after deploying!
print("DEBUG ENV KEYS:", [k for k in os.environ.keys() if "ADMIN" in k or "FLASK" in k])

db = SQLAlchemy(app)

################################################################################
class Todo(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    eventname    = db.Column(db.String(200), default="")
    room         = db.Column(db.String(200), default="")
    date         = db.Column(db.String(200), default="")
    time         = db.Column(db.String(200), default="")
    comment      = db.Column(db.String(200), default="")
    added_by     = db.Column(db.String(200), default="")
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/New_York")).replace(tzinfo=None))

with app.app_context():
    db.create_all()

################################################################################
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if not ADMIN_HASH:
            return "Server error: ADMIN_PASSWORD_HASH is not set."

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username == ADMIN_USERNAME:
            try:
                if ph.verify(ADMIN_HASH.strip(), password):
                    session['admin'] = True
                    return redirect('/')
            except VerifyMismatchError:
                pass

        return 'Invalid login.'

    return render_template('login.html')



################################################################################
@app.route('/logout/')
def logout():
    session.pop('admin', None)
    return redirect('/')


################################################################################################################################################################
@app.route('/', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        if not session.get('admin'):
            return redirect('/login/')

        new_event = Todo(
            eventname=request.form.get('eventname', ''),
            room=request.form.get('room', ''),
            date=request.form.get('date', ''),
            time=request.form.get('time', ''),
            comment=request.form.get('comment', ''),
            added_by=request.form.get('added_by', '')
        )

        try:
            db.session.add(new_event)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f'There was an issue adding your event: {e}'

    else:
        eventsList = Todo.query.order_by(Todo.id).all()
        return render_template('index.html', eventsList=eventsList)

################################################################################
@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('admin'):
        return redirect('/login/')

    event = Todo.query.get_or_404(id)

    try:
        db.session.delete(event)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'There was an issue removing your event: {e}'

################################################################################
@app.route('/modify/<int:id>', methods=['GET', 'POST'])
def modify(id):
    if not session.get('admin'):
        return redirect('/login/')

    event = Todo.query.get_or_404(id)

    if request.method == 'POST':
        event.eventname = request.form['eventname']
        event.room      = request.form['room']
        event.date      = request.form['date']
        event.time      = request.form['time']
        event.comment   = request.form['comment']

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'There was an issue modifying your event: {e}'
    else:
        return render_template('modify.html', event=event)

################################################################################
@app.route('/metadata/<int:id>', methods=['GET', 'POST'])
def metadata(id):
    event = Todo.query.get_or_404(id)

    if request.method == 'POST':
        if not session.get('admin'):
            return redirect('/login/')

        event.eventname = request.form.get('eventname', '')
        event.room      = request.form.get('room', '')
        event.date      = request.form.get('date', '')
        event.time      = request.form.get('time', '')
        event.comment   = request.form.get('comment', '')
        event.added_by  = request.form.get('added_by', '')

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f'There was an issue updating the metadata of your event: {e}'
    else:
        return render_template('metadata.html', event=event)
    
################################################################################
@app.route('/up/<int:id>', methods=['GET', 'POST'])
def up(id):
    if not session.get('admin'):
        return redirect('/login/')

    event = Todo.query.get_or_404(id)
    other = Todo.query.filter(Todo.id < id).order_by(Todo.id.desc()).first()

    if not other:
        return redirect('/')

    try:
        target_id = other.id
        event.id = -1
        db.session.commit()
        other.id = id
        db.session.commit()
        event.id = target_id
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()
        return f'There was an issue moving your event up: {e}'
    
################################################################################
@app.route('/down/<int:id>', methods=['GET', 'POST'])
def down(id):
    if not session.get('admin'):
        return redirect('/login/')

    event = Todo.query.get_or_404(id)
    other = Todo.query.filter(Todo.id > id).order_by(Todo.id.asc()).first()

    if not other:
        return redirect('/')

    try:
        target_id = other.id
        event.id = -1
        db.session.commit()
        other.id = id
        db.session.commit()
        event.id = target_id
        db.session.commit()
        return redirect('/')
    except Exception as e:
        db.session.rollback()
        return f'There was an issue moving your event down: {e}'

################################################################################
if __name__ == "__main__":
    app.run(debug=True)
    
    #python -m pip freeze > requirements.txt
    #python -c "import secrets; from argon2 import PasswordHasher; print('FLASK_SECRET_KEY:', secrets.token_hex(32)); print('ADMIN_PASSWORD_HASH:', PasswordHasher().hash('PUT_YOUR_REAL_PASSWORD_HERE'))"