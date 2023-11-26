from flask import Flask, render_template, request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import login_required,login_user,logout_user,LoginManager,current_user,UserMixin
import sqlite3 as s


app =  Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]= 'sqlite:///data.db'
app.config["SECRET_KEY"]='145fdg541d1f3dsf41'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view='login'
db= SQLAlchemy(app)

def get_db():
        conn = s.connect("database.db")
        conn.row_factory = s.Row
        return conn

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100),nullable=False)
    Email = db.Column(db.String(100),unique= True, nullable= False)
    Password = db.Column(db.String(100), nullable= False)


with app.app_context():
    db.create_all()


class RegistrationForm(FlaskForm):
    Name = StringField(validators=[InputRequired(), Length(min=4, max= 50)],render_kw={"placeholder":"Name"})
    Email=EmailField(validators=[InputRequired(), Length(min=4, max= 50)],render_kw={"placeholder":"Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=4, max= 20)],render_kw={"placeholder":"Password"})
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    Email=EmailField(validators=[InputRequired(), Length(min=4, max= 50)],render_kw={"placeholder":"Email"})
    Password = PasswordField(validators=[InputRequired(), Length(min=4, max= 20)],render_kw={"placeholder":"Password"})
    submit = SubmitField('Login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login',methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(Email=form.Email.data).first()
        print(f'Entered Password: {form.Password.data}')
        if user:
            if bcrypt.check_password_hash(user.Password,form.Password.data):
                login_user(user)
                flash('Logged in Successfully')
                return redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check your username and password', 'danger')
    return render_template('login.html',form=form)

@app.route("/dashboard",methods=["GET","POST"])
@login_required
def dashboard():
    with get_db() as db1:
        cursor = db1.cursor()
        cursor.execute("SELECT * FROM to_do")
        tasks=cursor.fetchall()
    return render_template('home1.html',tasks = tasks)

@app.route('/add', methods= ["POST"])
def add():
    Task = request.form.get('Task')
    Assignee = request.form.get('Assignee')
    Notes = request.form.get('Notes')
    Status = request.form.get('Status')
    with get_db() as db1:
        cursor = db1.cursor()
        cursor.execute('INSERT INTO to_do (Task, Assignee, Notes, Status) VALUES (?,?,?,?)',(Task, Assignee, Notes, Status))
        db1.commit()
    # db.close()
    return redirect(url_for('dashboard'))

@app.route('/update/<int:id>', methods = ["POST"])
def update(id):
    new_Task = request.form.get('new_Task')
    new_Assignee = request.form.get('new_Assignee')
    new_Note = request.form.get('new_Note')
    new_Status = request.form.get('new_Status')
    with get_db() as db1:
        cursor = db1.cursor()
        cursor.execute('UPDATE to_do SET Task = ?, Assignee = ?, Notes = ?, Status=? WHERE id =?', (new_Task, new_Assignee, new_Note, new_Status, id))
        db1.commit()
    # db.close()
    return redirect(url_for('dashboard'))

@app.route("/delete/<int:id>")
def delete(id):
     with get_db() as db1:
        cursor = db1.cursor()
        cursor.execute('DELETE FROM to_do WHERE id =?', (id,))
        db1.commit()
    #  db.close()
     return redirect(url_for('dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/register",  methods= ["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        email = User.query.filter_by(Email = form.Email.data)
        hashed_password = bcrypt.generate_password_hash(form.Password.data).decode('utf-8')
        user = User(Name= form.Name.data, Email=form.Email.data, Password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ =="__main__":
    app.run(debug=True)