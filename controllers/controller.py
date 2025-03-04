from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from models.models import *
from datetime import date



@app.route("/")
def home():
    return render_template("index.html")



@app.route("/admin/<name>")
def admin_dashboard(name):
    subjects = get_subjects()
    return render_template("admin_dashboard.html",name=name,subjects=subjects)
    
@app.route("/user/<name>")
def user_dashboard(name):
    return render_template("user_dashboard.html",name=name)
    

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        uname= request.form.get("email")
        pwd=request.form.get("pwd")
        usr=User.query.filter_by(email=uname,password=pwd).first()
        if usr and usr.role==0:
            return redirect(url_for("admin_dashboard",name=usr.fullname))
        if usr and usr.role==1:
            return redirect(url_for("user_dashboard",name=usr.fullname))
        return render_template("login.html",msg="wrong credentials!!")
    return render_template("login.html")


@app.route('/signup',methods=["GET","POST"])
def signup():
    if request.method=="POST":
        uname= request.form.get("email")
        pwd=request.form.get("pwd")
        fullname=request.form.get("fullname")
        qual=request.form.get("qual")
        dob=request.form.get('dob')
        if not uname or not pwd or not fullname or not qual or not dob:
            return render_template("signup.html",msg="fill all inputs properly")
        year, month, day = map(int, dob.split('-'))
        date_obj = date(year, month, day)
        # **Check if any field is empty**
        usr=User.query.filter_by(email=uname).first()
        if usr:
            return render_template('signup.html',msg="user alredy existed")
        new_usr=User(email=uname,password=pwd,fullname=fullname,qualification=qual,DOB=date_obj)
        db.session.add(new_usr)
        db.session.commit()
        return render_template('login.html',msg="Registration done successfully")
    return render_template("signup.html")



@app.route("/subject/<name>",methods=["GET","POST"])
def add_subj(name):
    if request.method=="POST":
        sname = request.form.get("name")
        sdescription = request.form.get("description")
        if not sname:
           return render_template("add_subject.html",name=name,msg="fill all inputs properly")
        new_subj=Subject(name=sname,description=sdescription)
        db.session.add(new_subj)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_subject.html",name=name)


@app.route("/chapter/<sub_id>/<name>",methods=["GET","POST"])
def add_chapter(sub_id,name):
    if request.method=="POST":
        cname = request.form.get("name")
        cdescription = request.form.get("description")
        if not cname:
           return render_template("add_subject.html",name=name,msg="fill all inputs properly")
        new_chapter=Chapter(name=cname,description=cdescription,Subject_id=sub_id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_chapter.html",name=name,subject_id=sub_id)

# seacrh



# supported fuction

def get_subjects():
    subjects = Subject.query.all()
    return subjects


