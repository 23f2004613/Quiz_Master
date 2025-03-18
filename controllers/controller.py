from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from models.models import *
from datetime import date,time,datetime,timedelta




@app.route("/")
def home():
    return render_template("index.html")

############################################## common fuctions for admin and user ####################################################

@app.route('/admin/<name>')
def admin_dashboard(name):
    subjects = get_subjects()
    return render_template("admin_dashboard.html",subjects=subjects,name=name)

@app.route('/user/<name>')
def user_dashboard(name):
    quizzes = get_quizs()
    return render_template("user_dashboard.html",quizs=quizzes,name=name)


@app.route('/quiz_dashboard/<name>')
def quiz_dashboard(name):
    # quizz=Quiz.query.join(Chapter).add_columns(Quiz.id, Chapter.id.label('chapter_id'), Chapter.name.label('chapter_name')).all()
    quizzes = get_quizs()
    return render_template("quiz_dashboard.html",quizs=quizzes,name=name)

# #################################################### login ########################################################

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


# ################################################### signup #############################################################

@app.route('/signup',methods=["GET","POST"])
def signup():
    min_dob = datetime.today().date() - timedelta(days=18 * 365)
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
        if date_obj >= min_dob:
            return render_template('signup.html',msg="age should be greatr then 18 years")
        # **Check if any field is empty**
        usr=User.query.filter_by(email=uname).first()
        if usr:
            return render_template('signup.html',msg="user alredy existed")
        new_usr=User(email=uname,password=pwd,fullname=fullname,qualification=qual,DOB=date_obj)
        db.session.add(new_usr)
        db.session.commit()
        return render_template('login.html',msg="Registration done successfully")
    return render_template("signup.html")




#  #########################################     adding a subject  #############################################

@app.route('/add_subject/<name>',methods=["GET","POST"])
def add_subject(name):
    if request.method=="POST":
        sub_name = request.form.get("name")
        sub_description = request.form.get("description")
        if not sub_name:
            return render_template("add_subject.html",name=name,msg="Subject name cant be empty")
        new_subj = Subject(name=sub_name,description=sub_description)
        db.session.add(new_subj)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_subject.html",name=name)


# ###########################################  editing of subject  #####################################################
@app.route('/edit_subject/<id>/<name>',methods=["GET","POST"])
def edit_subject(id,name):
    subj = get_subject(id)
    if request.method=="POST":
        new_sub_name = request.form.get("name")
        new_sub_description = request.form.get("description")
        if not new_sub_name:
            return render_template("edit_subject.html",subject=subj,name=name,msg="subject name cant be empty")
        subj.name = new_sub_name
        subj.description = new_sub_description
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("edit_subject.html",subject=subj,name=name)

# ####################################       delete of subject   ################################################

@app.route('/delete_subject/<id>/<name>',methods=["GET","POST"])
def delete_subject(id,name):
    subj= get_subject(id)
    db.session.delete(subj)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))
    
##################################         add of chApter #################################################

@app.route('/add_chapter/<id>/<name>',methods=["GET","POST"])
def add_chapter(id,name):
    subject = get_subject(id=id)
    if request.method=="POST":
        chap_name=request.form.get("name")
        chap_description = request.form.get("description")
        chapt = Chapter.query.filter_by(name=chap_name).first()
        if chapt:
            return render_template("add_chapter.html",subject=subject,name=name,msg="chapter name already exist")
        elif not chap_name:
            return render_template("add_chapter.html",subject=subject,name=name,msg="chapter name cant be empty")
        new_chapter = Chapter(name=chap_name,description=chap_description,Subject_id=subject.id)
        db.session.add(new_chapter)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_chapter.html",subject=subject,name=name)


##################################         edit of chApter #################################################

@app.route("/edit_chapter/<id>/<name>",methods=["GET","POST"])
def edit_chapter(id,name):
    chap = get_chapter(id)
    if request.method=="POST":
        new_chap_name = request.form.get("name")
        new_chap_description = request.form.get("description")
        if not new_chap_name:
            return render_template("edit_chapter.html",chapter=chap,name=name,msg="subject name cant be empty")
        chap.name = new_chap_name
        chap.description = new_chap_description
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("edit_chapter.html",chapter=chap,name=name)


##################################         delete of chApter #################################################

@app.route("/delete_chapter/<id>/<name>")
def delete_chapter(id,name):
    chap=get_chapter(id)
    db.session.delete(chap)
    db.session.commit()
    return redirect(url_for("admin_dashboard",name=name))



########################################   add quiz #############################################

@app.route('/add_quiz/<id>/<name>',methods=["GET","POST"])
def add_quiz(id,name):
    today = datetime.today().date()
    chap = get_chapter(id)
    if request.method=="POST":
        date_of_quiz = request.form.get("date_of_quiz")
        time_duration = request.form.get("time_duration")
        remarks = request.form.get("remarks")
        if not date_of_quiz or not time_duration :
            return render_template("add_quiz.html",chapter=chap,name=name,msg="Fill all inputs")
        year, month, day = map(int, date_of_quiz.split('-'))
        date_obj = date(year, month, day)
        hour, minute = map(int, time_duration.split(':'))
        time_obj = time(hour, minute)
        if date_obj <= today:
            return render_template("add_quiz.html",name=name,chapter=chap,msg="increase date")
        new_quiz=Quiz(date_of_quiz=date_obj,time_duration=time_obj,remarks=remarks,Chapter_id=id)
        db.session.add(new_quiz)
        db.session.commit()
        return redirect(url_for("admin_dashboard",name=name))
    return render_template("add_quiz.html",name=name,chapter=chap)


###########################################    edit quiz #############################################


@app.route("/edit_quiz/<id>/<name>",methods=["GET","POST"])
def edit_quiz(id,name):
    today = datetime.today().date()
    quiz = get_quiz(id)
    if request.method=="POST":
        mod_date_of_quiz = request.form.get("date_of_quiz")
        mod_time_duration = request.form.get("time_duration")
        mod_remarks = request.form.get("remarks")
        if not mod_date_of_quiz or not mod_time_duration :
            return render_template("edit_quiz.html",quiz=quiz,name=name,msg="Fill all inputs")
        year, month, day = map(int, mod_date_of_quiz.split('-'))
        date_obj = date(year, month, day)
        time_parts = list(map(int, mod_time_duration.split(':')))
        hour, minute = time_parts[:2] 
        time_obj = time(hour, minute)
        if date_obj <= today:
            return render_template("edit_quiz.html",name=name,quiz=quiz,msg="increase date")
        quiz.date_of_quiz=date_obj
        quiz.time_duration=time_obj
        quiz.remarks=mod_remarks
        db.session.commit()
        return redirect(url_for("quiz_dashboard",name=name))
    return render_template("edit_quiz.html",quiz=quiz,name=name)


###############################################   delete quiz @@#################################################


@app.route("/delete_quiz/<id>/<name>")
def delete_quiz(id,name):
    quiz=get_quiz(id)
    db.session.delete(quiz)
    db.session.commit()
    return redirect(url_for("quiz_dashboard",name=name))



############################## ########## add question ############################################
@app.route("/add_question/<id>/<name>",methods=["GET","POST"])
def add_questions(id,name):
    quiz = get_quiz(id)
    if request.method=='POST':
        question_title = request.form.get('question_title')
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        new_question = Question(quiz_id=quiz.id,question_title=question_title,question_statement=question_statement,option1=option1,option2=option2,
                                option3=option3,option4=option4,correct_option=correct_option)
        db.session.add(new_question)
        db.session.commit()
        return redirect(url_for("quiz_dashboard",name=name))
    return render_template("add_question.html",quiz=quiz,name=name)

############################## ########## edit question ############################################



@app.route("/edit_question/<id>/<name>",methods=["GET","POST"])
def edit_questions(id,name):
    question = get_question(id)
    if request.method=='POST':
        mquestion_title = request.form.get('question_title')
        mquestion_statement = request.form.get('question_statement')
        moption1 = request.form.get('option1')
        moption2 = request.form.get('option2')
        moption3 = request.form.get('option3')
        moption4 = request.form.get('option4')
        mcorrect_option = request.form.get('correct_option')
        
        question.question_title = mquestion_title
        question.question_statement = mquestion_statement
        question.option1 = moption1
        question.option2 = moption2
        question.option3 = moption3
        question.option4 = moption4
        question.correct_option = mcorrect_option
        db.session.commit()
        return redirect(url_for("quiz_dashboard",name=name))
    return render_template("edit_question.html",question=question,name=name)

############################## ########## delete question ############################################


@app.route("/delete_question/<id>/<name>",methods=["GET","POST"])
def delete_question(id,name):
    question = get_question(id)
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for("quiz_dashboard",name=name))

############################## ########## view quiz ############################################

@app.route('/view_quiz/<id>/<name>')
def view_quiz(id,name):
    quiz = get_quiz(id)
    chapter = Chapter.query.filter_by(id=quiz.Chapter_id).first()
    subject = Subject.query.filter_by(id=chapter.Subject_id).first()
    return render_template("quiz_details.html",quiz=quiz,name=name,chapter=chapter,subject=subject)  

#############################################    search #################################################

@app.route("/search/<name>", methods=['GET','POST'])
def search(name):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        by_subj = search_by_subject(search_txt)
        # by_chap = search_by_chapter(search_txt)
        if by_subj:
            return render_template("admin_dashboard.html",name=name,subjects=by_subj)
        # elif by_chap:
        #     return render_template("admin_dashboard.html",name=name,subjects=by_chap)
    return redirect(url_for("admin_dashboard",name=name))


def search_by_subject(search_txt):
    subj = Subject.query.filter(Subject.name.ilike(f"%{search_txt}%")).all()
    return subj




# ##########################################        support fuctions      ##################################################  

# for getting all subject info for the admin dashboard

def get_subjects():
    subjects = Subject.query.all()
    return subjects 


def get_quizs():
    quizs = Quiz.query.all()
    return quizs 
    
def  get_subject(id):
    subject = Subject.query.filter_by(id=id).first() 
    return subject


def  get_chapter(id):
    chapter = Chapter.query.filter_by(id=id).first() 
    return chapter


def  get_quiz(id):
    quiz = Quiz.query.filter_by(id=id).first() 
    return quiz

def  get_question(id):
    question = Question.query.filter_by(id=id).first()
    return question