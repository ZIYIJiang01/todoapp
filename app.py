import sys
from flask import Flask, jsonify, redirect, render_template, request, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# simply create an application after the name of file
app = Flask(__name__)
#connect our flask app to particular database
#this would not create database for you, so create database manually 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@127.0.0.1:5432/todoapp'
#link SQLAlchemy to flask app
db = SQLAlchemy(app)

#initializing migration
migrate = Migrate(app,db)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    #foreignkey
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)
    #debug
    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'
#parent model
class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='list', lazy=True)
    
    def __repr__(self):
        return f'<TodoList {self.id} {self.name}>'

#to ensure tables created
#if use migration, there is no need using create_all()
#with app.app_context():    
#    db.create_all()

#define a route listen to /todos/create
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False 
    body = {}
    try:
        #description = request.form.get('description','')
        #get data use json instead of form
        description = request.get_json()['description']
        #add an object
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)
        #return jsonify({
            #jsonify will return the json data to the client
            #'description': todo.description})
        #redirect to the index and show, if use json there is no need to redirect
        #return redirect(url_for('index'))

#listen to the update completed post request 
@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        print('completed', completed)
        todo = Todo.query.get(todo_id)
        todo.completed = completed 
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

#delete
@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})

#allow user to visit homepage
#@app.route('/')
#route handler
#def index():
#render template to spicify the template when user visit 
    #pass variables to use in template
    #return render_template('index.html', data=Todo.query.order_by('id').all())

#define a route listen to /lists/create
@app.route('/lists/create', methods=['POST'])
def create_list():
    error = False 
    body = {}
    try:
        name = request.get_json()['name']
        #add an object
        list = TodoList(name=name)
        db.session.add(list)
        db.session.commit()
        body['name'] = list.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify(body)




#go to a particular todolist
@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html',
    lists=TodoList.query.all(),
    active_list = TodoList.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())
#home page
@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))
