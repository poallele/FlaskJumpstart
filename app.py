###################################################################################################
# [from flask import Flask]:
#                           Import the 'Flask' class.
#                           An instance of this class will be our Web Server Gateway Interface application.
###################################################################################################
from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



###################################################################################################
# [app = Flask(x)]:
#                  Create an instance of the 'Flask' class.
#                  The first argument is the name of the application’s module or package.
#
# [__name__]:
#            Since there is no main() function in Python,
#            when the command to run a python program is given to the interpreter,
#            the code that is at level 0 indentation is to be executed.
#            However, before doing that, it will define a few special variables.
#                   
#            __name__ is one such special variable.
#
#            If the source file is executed as the main program,
#            the interpreter sets the __name__ variable to have a value "__main__".
#            If this file is being imported from another module,
#            __name__ will be set to the module's name.
#                   
#            __name__ is needed so that Flask knows where to look for resources such as templates and static files.
################################################################################
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


################################################################################
# [class Todo(x)]:
#                 Classes are defined by the user.
#                 They are used for creating custom data types (objects) that bundle data together.
#                 In the class 'Todo', there are 3 events bundled together per 'object'.
#
# [db.Model]:
#            'db' is the SQLAlchemy database.
#            'Model' is a SQLAlchemy declarative model class;
#            subclass this to define database models.
# [id]:
#      A
#
# [name]:
#           A
#
# [data_created]:
#                A
################################################################################
class Todo(db.Model):
    id              = db.Column     (db.Integer,        primary_key = True)
    name            = db.Column     (db.String(200),    default="")
    room            = db.Column     (db.String(200),    default="")
    date            = db.Column     (db.String(200),    default="")
    time            = db.Column     (db.String(200),    default="")
    comment         = db.Column     (db.String(200),    default="")
    
    date_created    = db.Column     (db.DateTime,       default=datetime.utcnow)
    added_by        = db.Column     (db.String(200),    default="Administrator")
    
    def __repr__(self):
        return '<Event %r>' % self.id



################################################################################
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        
        name = request.form['name']
        room = request.form['room']
        date = request.form['date']
        time = request.form['time']
        comment = request.form['comment']
        
        new_event = Todo(
            name=name,
            room=room,
            date=date,
            time=time,
            comment=comment)
        
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
    event = Todo.query.get_or_404(id)
    
    if request.method == 'POST':
        
        event.name = request.form['name']
        event.room = request.form['room']
        event.date = request.form['date']
        event.time = request.form['time']
        event.comment = request.form['comment']
        
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
        
        event.name = request.form['name']
        event.room = request.form['room']
        event.date = request.form['date']
        event.time = request.form['time']
        event.comment = request.form['comment']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your event'
    else:
        return render_template('metadata.html', event=event)



################################################################################
# Without this, it cannot even run in VSCode when you press the 'Build' button.
################################################################################
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)