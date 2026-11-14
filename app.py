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
#                 In the class 'Todo', there are 3 items bundled together per 'object'.
#
# [db.Model]:
#            'db' is the SQLAlchemy database.
#            'Model' is a SQLAlchemy declarative model class;
#            subclass this to define database models.
# [id]:
#      A
#
# [content]:
#           A
#
# [data_created]:
#                A
################################################################################
class Todo(db.Model):
    id              = db.Column     (db.Integer,        primary_key = True)
    content         = db.Column     (db.String(200),    nullable=False)
    date_created    = db.Column     (db.DateTime,       default=datetime.utcnow)
    
    def __repr__(self):
        return '<Task %r>' % self.id



################################################################################
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)
        
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
        
    else:
        tasksList = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasksList=tasksList)

################################################################################
@app.route('/delete/<int:id>')
def delete(id):

    task_to_delete = Todo.query.get_or_404(id)
    
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'



################################################################################
@app.route('/modify/<int:id>', methods=['GET', 'POST'])
def modify(id):
    task = Todo.query.get_or_404(id)
    
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)


################################################################################
# Without this, it cannot even run in VSCode when you press the 'Build' button.
################################################################################
if __name__ == "__main__":
    app.run(debug=True)