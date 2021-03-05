#!/usr/bin/python3
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret_key"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Tasks.db'
db = SQLAlchemy(app)


class Tasks(db.Model):
    __tablename__ = "Tasks"
    sr = db.Column(db.Integer, primary_key=True, unique=True)
    id = db.Column(db.Integer, nullable=False)
    task = db.Column(db.String(100), nullable=False)
    task_sr = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(50))
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)


class Task_Names(db.Model):
    __tablename__ = "Task_Names"
    sr = db.Column(db.Integer, primary_key=True, unique=True)
    id = db.Column(db.Integer)
    name = db.Column(db.String(100))


class Accounts(db.Model):
    __tablename__ = "Accounts"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(150))
    password = db.Column(db.String(150))


class Progress(db.Model):
    __tablename__ = "Progress"
    sr = db.Column(db.Integer, primary_key=True, unique=True)
    id = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.String(100), nullable=False)
    HowMuch = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False)


def to_normal(tasks):
    normal_tasks = []
    no = 1
    for task in tasks[::-1]:
        new = task.__dict__
        new['no'] = no
        no += 1
        normal_tasks.append(new)
    return normal_tasks


@app.route('/login', methods=['GET', "POST"])
def login():
    if session.get('id'):
        return redirect('/')
    if request.method == 'POST':
        username = request.form['USERNAME']
        password = request.form['PASSWORD']
        user = Accounts.query.filter(Accounts.username == username)
        user_pass = Accounts.query.filter(
            Accounts.username == username, Accounts.password == password)
        if user.count():
            if user_pass.count():
                session['id'] = user.first().id
                session['username'] = username
                # session['password'] = password
                # session.permanent = True
                return redirect('/')
            elif not user_pass.count():
                flash = ' Incorrect password for username '
                return render_template("login.html", flash=flash)
        else:
            flash = ' Not any username found '
            return render_template("login.html", flash=flash)
    return render_template('login.html')


@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['USERNAME']
    password = request.form['PASSWORD']
    user = Accounts.query.filter(Accounts.username == username).count()
    if user:
        flash = ' This username already exits '
        return render_template("login.html", flash=flash)
    new_user = Accounts(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash = ' Account has been created '
    return render_template("login.html", flash=flash)


def check_login(main):
    if not session.get('id'):
        return redirect('/login')
    else:
        return main()


@app.route('/delete/account')
def delete_account():
    def main():
        user_id = session.get('id')
        delete_it = (Accounts.query.filter(Accounts.id == user_id).all())
        delete_it += (Tasks.query.filter(Tasks.id == user_id).all())
        delete_it += (Task_Names.query.filter(Task_Names.id == user_id).all())
        for i in delete_it:
            db.session.delete(i)
        db.session.commit()
        return redirect('/logout')
    return check_login(main)


@app.route("/")
def index():
    def main():
        user_id = session.get('id')
        tasks = Tasks.query.filter(Tasks.id == user_id).all()
        tasks = to_normal(tasks)
        for i in tasks:
            updated_task_name = Task_Names.query.filter(
                Task_Names.id == user_id, Task_Names.sr == i['task_sr']).first().name
            if updated_task_name != i['task']:
                i['task'] = updated_task_name
                update_it = Tasks.query.filter(Tasks.sr == i['sr'], Tasks.id == user_id).first()
                update_it.task = updated_task_name
                db.session.commit()
        username = session.get('username')
        return render_template("index.html", tasks=tasks, username=username)
    return check_login(main)


@app.route("/add", methods=["GET", "POST"])
def add():
    def main():
        if request.method == "POST":
            user_id = session.get('id')
            task = request.form['task']
            task_sr = Task_Names.query.filter(
                Task_Names.name == task, Task_Names.id == user_id).first().sr
            quantity = request.form['quantity']
            unit = request.form['unit']
            date = request.form['date']
            time = request.form['time']
            new_task = Tasks(id=user_id, task=task, task_sr=task_sr,
                             quantity=quantity, unit=unit, date=date, time=time)
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        user_id = session.get('id')
        tasks_name = Task_Names.query.filter(Task_Names.id == user_id).all()
        return render_template("update.html", tasks_name=tasks_name, work="Adder", task={})
    return check_login(main)


@app.route('/delete/<int:sr>')
def tasks_delete(sr):
    def main():
        user_id = session.get('id')
        delete_it = Tasks.query.filter(Tasks.sr == sr, Tasks.id == user_id).first()
        if not delete_it:
            return redirect('/')
        db.session.delete(delete_it)
        db.session.commit()
        return redirect('/')
    return check_login(main)


@app.route('/update/<int:sr>', methods=["POST", "GET"])
def update(sr):
    def main():
        user_id = session.get('id')
        update_it = Tasks.query.filter(Tasks.sr == sr, Tasks.id == user_id).first()
        if not update_it:
            return redirect('/')
        if request.method == "POST":
            task = request.form['task']
            update_it.task = task
            update_it.quantity = request.form['quantity']
            update_it.unit = request.form['unit']
            update_it.date = request.form['date']
            update_it.time = request.form['time']
            db.session.commit()
            return redirect("/")
        user_id = session.get('id')
        tasks_name = Task_Names.query.filter(Task_Names.id == user_id).all()
        return render_template("update.html", tasks_name=tasks_name, task=update_it, work="Updater")
    return check_login(main)


@app.route('/search/tasks', methods=['GET', 'POST'])
def search_tasks():
    def main():
        if request.method == 'POST':
            user_id = session.get('id')
            search_by = request.form
            task = "%" + search_by['task'] + "%"
            quantity_min = search_by['quantity_min']
            quantity_max = search_by['quantity_max']
            unit = '%' + search_by['unit'] + '%'
            date_min = search_by['date_min']
            date_max = search_by['date_max']
            if not quantity_min:
                quantity_min = -1
            if not date_max:
                date_max = "a"
            tasks = Tasks.query.filter(Tasks.task.like(task), Tasks.quantity.between(quantity_min, quantity_max), Tasks.unit.like(
                unit), Tasks.date.between(date_min, date_max), Tasks.id == user_id).all()
            tasks = to_normal(tasks)
            username = session.get('username')
            return render_template("index.html", tasks=tasks, username=username)
        return render_template('search.html')
    return check_login(main)


@app.route('/add_name', methods=['GET', 'POST'])
def add_name():
    def main():
        if request.method == "POST":
            user_id = session.get('id')
            task_name = request.form['task_name'].title()
            if Task_Names.query.filter(Task_Names.name == task_name, Task_Names.id == user_id).count():
                return redirect('add_name')
            task_name = Task_Names(id=user_id, name=task_name)
            db.session.add(task_name)
            db.session.commit()
            return redirect('/add_name')
        user_id = session.get('id')
        task_names = Task_Names.query.filter(Task_Names.id == user_id).all()
        task_names = to_normal(task_names)
        return render_template('add_name.html', task_names=task_names)
    return check_login(main)


@app.route('/delete_name/<int:sr>')
def delete_name(sr):
    def main():
        user_id = session.get('id')
        delete_it = Task_Names.query.filter(Task_Names.sr == sr, Task_Names.id == user_id).first()
        if not delete_it:
            return redirect('/add_name')
        db.session.delete(delete_it)
        db.session.commit()
        return redirect('/add_name')
    return check_login(main)


@app.route('/update_name/<int:sr>', methods=["POST"])
def update_name(sr):
    def main():
        user_id = session.get('id')
        update_it = Task_Names.query.filter(Task_Names.sr == sr, Task_Names.id == user_id).first()
        if not update_it:
            return redirect("/add_name")
        if request.method == "POST":
            update_it.name = request.form['task_name'].title()
            db.session.commit()
            return redirect("/add_name")
    return check_login(main)


@app.route('/progress', methods=['GET', 'POST'])
def progess():
    user_id = session.get('id')
    if request.method == "POST":
        progress = request.form['progress']
        how_much = request.form['how_much']
        date = request.form['date']
        time = request.form['time']
        progress = Progress(id=user_id, progress=progress, HowMuch=how_much, date=date, time=time)
        db.session.add(progress)
        db.session.commit()
        return redirect('/progress')
    progress = Progress.query.filter(Progress.id == user_id).all()
    progress = to_normal(progress)
    return render_template('progress.html', progress=progress)


@app.route('/progress/delete/<int:sr>')
def progress_delete(sr):
    def main():
        user_id = session.get('id')
        delete_it = Progress.query.filter(Progress.sr == sr, Progress.id == user_id).first()
        if not delete_it:
            return redirect('/progress')
        db.session.delete(delete_it)
        db.session.commit()
        return redirect('/progress')
    return check_login(main)


@app.route('/progress/update/<int:sr>', methods=['POST'])
def progress_update(sr):
    def main():
        user_id = session.get('id')
        update_it = Progress.query.filter(Progress.sr == sr, Progress.id == user_id).first()
        if not update_name:
            return 'update it is not'
        update_it.progress = request.form['progress']
        update_it.HowMuch = request.form['how_much']
        update_it.date = request.form['date']
        update_it.time = request.form['time']
        db.session.commit()
        return redirect("/progress")
    return check_login(main)


@app.route('/logout')
def logout():
    session['id'] = None
    session['username'] = None
    # session['password'] = None
    return redirect('/login')


@app.route('/<path:unknown>', methods=['GET', 'POST'])
def student(unknown):
    return f"<h3><center>Hey there, The web page that you are finding <h1><i><u>{unknown}</u></i></h1> is not here.</center></h3>{request.form}"


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
