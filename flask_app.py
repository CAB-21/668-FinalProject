
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="BarnesKershner",
    password="FinalProject",
    hostname="BarnesKershner.mysql.pythonanywhere-services.com",
    databasename="BarnesKershner$gradebook2",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db=SQLAlchemy(app)

app.secret_key="RUCUwyRsdkcVUyt"
login_manager=LoginManager()
login_manager.init_app(app)

class Student(db.Model):
        __tablename__="student"

        student_id=db.Column(db.Integer, primary_key=True)
        first_name=db.Column(db.String(4096))
        last_name=db.Column(db.String(4096))
        student_major=db.Column(db.String(4096))
        student_email=db.Column(db.String(4096))

class Assignment(db.Model):
        __tablename__="assignment"

        assignment_id=db.Column(db.Integer, primary_key=True)
        assignment_name=db.Column(db.String(4096))

class Graded_Assignment(db.Model):
        __tablename__="graded_assignment"

        ref_assignment_id=db.Column(db.Integer, db.ForeignKey('assignment.assignment_id'), primary_key=True)
        ref_assignment=db.relationship('Assignment', foreign_keys=ref_assignment_id)
        ref_student_id=db.Column(db.Integer, db.ForeignKey('student.student_id'), primary_key=True)
        ref_student=db.relationship('Student', foreign_keys=ref_student_id)
        grade=db.Column(db.Numeric)

class User(UserMixin, db.Model):

    __tablename__="users"

    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(128))
    password_hash=db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

@app.route('/')
def index():
    return render_template("gradebook.html", students=Student.query.all(), graded_assignments=Graded_Assignment.query.all())

@app.route('/edit/')
def edit():
    return render_template("edit.html", students=Student.query.all(), assignments=Assignment.query.all())

@app.route('/add_student/', methods=['POST'])
def add_student():
    new_student=Student(first_name=request.form["fname"], last_name=request.form["lname"], student_major=request.form["major"], student_email=request.form["email"])
    db.session.add(new_student)
    db.session.commit()
    for row in db.session.execute('SELECT * FROM assignment'):
        new_graded_assignment=Graded_Assignment(ref_assignment_id=row.assignment_id,ref_student_id=new_student.student_id,grade=0)
        db.session.add(new_graded_assignment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/remove_student/', methods=['POST'])
def remove_student():
    for row in db.session.execute('SELECT * FROM graded_assignment'):
        db.session.execute('DELETE FROM graded_assignment WHERE ref_student_id='+request.form['student_id'])
    db.session.execute('DELETE FROM student WHERE student_id='+request.form['student_id'])
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_grade/', methods=['POST'])
def edit_grade():
    db.session.execute('UPDATE graded_assignment SET grade='+request.form['new_grade']+' WHERE ref_student_id='+request.form['student_id']+' AND ref_assignment_id='+request.form['assignment_id'])
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_assignment/', methods=['POST'])
def add_assignment():
    new_assignment=Assignment(assignment_name=request.form["aname"])
    db.session.add(new_assignment)
    db.session.commit()

    for row in db.session.execute('SELECT * FROM student'):
        new_graded_assignment=Graded_Assignment(ref_assignment_id=new_assignment.assignment_id,ref_student_id=row.student_id,grade=0)
        db.session.add(new_graded_assignment)

    db.session.commit()
    return redirect(url_for('index'))

@app.route('/remove_assignment/', methods=['POST'])
def remove_assignment():
    for row in db.session.execute('SELECT * FROM graded_assignment'):
        db.session.execute('DELETE FROM graded_assignment WHERE ref_assignment_id='+request.form['assignment_id'])
    db.session.execute('DELETE FROM assignment WHERE assignment_id='+request.form['assignment_id'])
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=False)
    user = load_user(request.form["username"])
    if user is None:
        return render_template("login.html", error=True)
    if not user.check_password(request.form["password"]):
        return render_template("login.html", error=True)
    login_user(user)
    return redirect(url_for('index'))

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
   app.run(debug = True)