from flask import Flask, flash, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
import psycopg2 as pg
import csv
from model import model_function

# database initialisation
app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/postgres'
    app.config['SQLALCHEMY_BINDS'] = {'two': 'postgresql://postgres:1234@localhost/postgres'}
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
    app.config['SQLALCHEMY_BINDS'] = {'two': ''}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class customer(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    personId = db.Column(db.String(20),primary_key=True)
    MaxEducation = db.Column(db.String(20))
    PrimaryOccupation = db.Column(db.String(20))
    Stage= db.Column(db.String(20))
    AnnualIncome = db.Column(db.String(20))
    leadquality = db.Column(db.String(20))



class users(db.Model):
    __bind_key__ = 'two'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    First_name = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(50))
    Phone_No = db.Column(db.String(50))
    Username = db.Column(db.String(50), nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    Date_Created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())


#sign up route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        flag=0
        fname=First_name=request.form['first_name']
        email=Email=request.form['email']
        phone_no= Phone_No=request.form['phone_no']
        username = Username=request.form['username']
        password = request.form['password']
        confirm_password = request.form["confirm_password"]

        check_user = users.query.filter_by(Username=username).first()
        check_email = users.query.filter_by(Email=email).first()
        
        if len(password)<8 or len(password)>16:
            flash("password must be between 8 and 16 characters")
            flag=1
        elif len(phone_no)!=10:
            flash("enter a valid phone number")
            flag=1
        elif check_email is not None:
            flash("This email is already registered")
            flag=1
        elif check_user is not None:
            flash("username already exists in the database")
            flag=1
        elif confirm_password!=password:
            flash("passwords do no match")
            flag=1

        if flag==0:
            pw=generate_password_hash(password)
            obj = users(First_name=fname, Email=email,Phone_No=phone_no, Username=username, Password=pw)
            db.session.add(obj)
            db.session.commit()
            return redirect(url_for('Login'))
    return render_template('signup.html')


#login route
@app.route('/', methods=['GET', 'POST'])
def Login():

    if request.method == 'POST':

        username = request.form['username']
        un = users.query.filter_by(Username=username).first()
        if un is None:
            flash("Incorrect Username or This User does not exist in our database")
        elif un.Username == request.form['username'] and check_password_hash(un.Password, request.form['password'])==True:
            return redirect(url_for("user", username=un.Username, name=un.First_name, email=un.Email, phone_no=un.Phone_No))
        elif check_password_hash(un.Password, request.form['password'])==False:
            flash("incorrect password",category="message")
    return render_template('login.html')

#guest main page route
@app.route("/guest",methods={'GET','POST'})
def guest():
    if request.method=='POST':
        personid = request.form['personid']
        maxeducation = request.form['maxeducation']
        annualincome = request.form['annualincome']
        stage = request.form['stage']
        primaryoccupation = request.form['primaryoccupation']
        
        conn = pg.connect(database="postgres", user="postgres", host="localhost", password="1234")
        scur= conn.cursor()
        query="select max(sno) from customer"
        scur.execute(query)
        SNO=scur.fetchall()
        obj = customer(sno=SNO[0][0]+1,personId=personid, MaxEducation=maxeducation,PrimaryOccupation=primaryoccupation,Stage=stage,AnnualIncome=annualincome)
        db.session.add(obj)
        db.session.commit()
        scur.close()
        conn.close()

        query = "select * from customer"

        conn = pg.connect(database="postgres", user="postgres", host="localhost", password="1234")
        cur = conn.cursor()
        cur.execute(query)

        with open('final.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(('sno','personId', 'MaxEducation', 'PrimaryOccupation', 'Stage', 'AnnualIncome', 'leadquality'))
            for row in cur.fetchall():
                writer.writerow(row)

        
        o=model_function()
        if o[0]==2:
            result='Best'
        if o[0]==1:
            result='Average'
        if o[0]==3:
            result='Poor'
        cur.close()

        conn.close()

        conn= pg.connect(database="postgres", user="postgres", host="localhost", password="1234")
        cur=conn.cursor()

        cur.execute(f"update customer set leadquality='{result}' where sno={SNO[0][0]+1}")
        conn.commit()
        cur.close()
        conn.close()
       

        return redirect(url_for("results",result=result))
        
    return render_template("guest.html")


#main page route
@app.route('/home/<username>/<name>/<email>/<phone_no>', methods={'GET', 'POST'})
def user(username, name, email, phone_no):

    query="select * from customer order by sno desc  limit 1000"

    con=pg.connect(database="postgres",user="postgres",host="localhost",password="1234")
    cur=con.cursor()
    cur.execute(query)
    detail=cur.fetchall()

    if request.method == 'POST':
        personid = request.form['personid']
        maxeducation = request.form['maxeducation']
        annualincome = request.form['annualincome']
        stage = request.form['stage']
        primaryoccupation = request.form['primaryoccupation']
        
        conn=pg.connect(database="postgres",user="postgres",host="localhost",password="1234")
        scur= conn.cursor()
        query="select max(sno) from customer"
        scur.execute(query)
        SNO=scur.fetchall()
        obj = customer(sno=SNO[0][0]+1,personId=personid, MaxEducation=maxeducation,PrimaryOccupation=primaryoccupation,Stage=stage,AnnualIncome=annualincome)
        db.session.add(obj)
        db.session.commit()
        scur.close()
        conn.close()

        query = "select * from customer"

        conn=pg.connect(database="postgres",user="postgres",host="localhost",password="1234")        
        cur = conn.cursor()
        cur.execute(query)

        with open('final.csv', 'w') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(('sno','personId', 'MaxEducation', 'PrimaryOccupation', 'Stage', 'AnnualIncome', 'leadquality'))
            for row in cur.fetchall():
                writer.writerow(row)

        
        o=model_function()
        if o[0]==2:
            result='Best'
        if o[0]==1:
            result='Average'
        if o[0]==3:
            result='Poor'
        cur.close()

        conn.close()

        conn=pg.connect(database="postgres",user="postgres",host="localhost",password="1234")
        cur=conn.cursor()

        cur.execute(f"update customer set leadquality='{result}' where sno={SNO[0][0]+1}")
        conn.commit()
        cur.close()
        conn.close()
       

        return redirect(url_for("results",result=result))    

    return render_template("Index.html", name=name, userid=username, email=email, phone_no=phone_no,people=detail)



@app.route("/results/<result>")
def results(result): 
    return render_template("results.html",result=result)

if __name__ == '__main__':
    app.run()
