from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
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
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

################################################################################
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if not ADMIN_HASH:
            return "FAIL: ADMIN_HASH is empty/None"

        username = request.form.get('username', '')
        password = request.form.get('password', '')

        if username != ADMIN_USERNAME:
            return f"FAIL: Username mismatch. Typed '{username}', expected '{ADMIN_USERNAME}'"

        try:
            ph.verify(ADMIN_HASH.strip(), password)
            session['admin'] = True
            return redirect('/')
        except Exception as e:
            return f"FAIL: Argon2 error -> {type(e).__name__}: {e} | Hash len: {len(ADMIN_HASH)}"

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
            eventname=request.form['eventname'],
            room=request.form['room'],
            date=request.form['date'],
            time=request.form['time'],
            comment=request.form['comment'],
            added_by=request.form['comment']
        )

        try:
            db.session.add(new_event)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your event'

    else:
        eventsList = Todo.query.order_by(Todo.date_created).all()
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
    except:
        return 'There was a problem deleting that event'

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
        event.added_by  = request.form['comment']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your event'
    else:
        return render_template('modify.html', event=event)

################################################################################
@app.route('/metadata/<int:id>', methods=['GET', 'POST'])
def metadata(id):
    event = Todo.query.get_or_404(id)

    if request.method == 'POST':
        if not session.get('admin'):
            return redirect('/login/')

        event.eventname = request.form['eventname']
        event.room      = request.form['room']
        event.date      = request.form['date']
        event.time      = request.form['time']
        event.comment   = request.form['comment']
        event.added_by  = request.form['comment']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your event'
    else:
        return render_template('metadata.html', event=event)

################################################################################
if __name__ == "__main__":
    
    #python -m pip freeze > requirements.txt
    #python -c "import secrets; from argon2 import PasswordHasher; print('FLASK_SECRET_KEY:', secrets.token_hex(32)); print('ADMIN_PASSWORD_HASH:', PasswordHasher().hash('PUT_YOUR_REAL_PASSWORD_HERE'))"

    
    with app.app_context():
        db.create_all()

    app.run(debug=True)