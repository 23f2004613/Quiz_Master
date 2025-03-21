from flask import Flask,render_template,request,url_for,redirect,session
from flask import current_app as app
from models.models import *
from datetime import date,time,datetime,timedelta
import matplotlib
matplotlib.use("Agg")  # Use Agg backend (non-GUI)
import matplotlib.pyplot as plt




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
    quizzes = get_quizs()
    return render_template("quiz_dashboard.html",quizs=quizzes,name=name)

# #################################################### login ########################################################

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        uname= request.form.get("email")
        pwd=request.form.get("pwd")
        usr=User.query.filter_by(email=uname,password=pwd).first()
        if usr:
            session["user_id"] = usr.id  
            session["username"] = usr.fullname  
            session["role"] = usr.role  # Store role for later use
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
        qname = request.form.get("quiz_name")
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
        new_quiz=Quiz(name=qname,date_of_quiz=date_obj,time_duration=time_obj,remarks=remarks,Chapter_id=id)
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
        mod_name = request.form.get("quiz_name")
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
        quiz.name = mod_name
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
    chapter = Chapter.query.filter_by(id =quiz.Chapter_id).first()
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
    return render_template("add_question.html",quiz=quiz,name=name,chap=chapter.name)

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


############################## ########## start quiz ############################################

@app.route("/quiz_exam/<id>/<name>", methods=["GET", "POST"])
def give_quiz(id, name):
    quiz = Quiz.query.get_or_404(id)  # Fetch quiz details
    questions = Question.query.filter_by(quiz_id=quiz.id).all()  # Get all questions
    total_questions = len(questions)
    
    if request.method == "POST":
        user_answers = request.form.to_dict(flat=True)  # Get all submitted answers
        correct_answers = 0
        
        for question in questions:
            selected_option = user_answers.get(str(question.id))

            if selected_option and selected_option == str(question.correct_option):
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        if "user_id" in session:  # Ensure user is logged in
            new_score = Score(
                quiz_id=quiz.id,
                user_id=session["user_id"],
                total_scored=round(score, 2),
                time_stamp=datetime.utcnow()
            )
            db.session.add(new_score)
            db.session.commit()
        
        return render_template(
            "quiz_score.html",
            quiz=quiz,
            name=name,
            correct_answers=correct_answers,
            total_questions=total_questions,
            score=round(score, 2)
        )
    
    return render_template("quiz.html", quiz=quiz, name=name, questions=questions, total=total_questions)


@app.route("/restart_quiz/<id>/<name>")
def restart_quiz(id, name):
    # Redirect to restart the quiz (reloads the quiz page)
    return redirect(url_for("give_quiz", id=id, name=name))


@app.route("/user_scores/<name>")
def user_scores(name):
    user_id = session["user_id"]
    scores = Score.query.filter_by(user_id=user_id).all()
    num_questions = {}
    for score in scores:
        quiz_id = score.quiz_id  # Get quiz ID
        question_count = Question.query.filter_by(quiz_id=quiz_id).count()  # Count questions for that quiz
        num_questions[quiz_id] = question_count  # Store in dictionary

    return render_template("user_scores.html", name=name, scores=scores,num_questions=num_questions)


@app.route("/user_summary/<name>")
def user_summary(name):
    if "user_id" not in session:
        return redirect(url_for("login"))  # Redirect to login if session is empty
    
    user_id = session["user_id"]  # Get user ID from session

    # Fetch all quiz attempts by the user
    user_scores = Score.query.filter_by(user_id=user_id).all()

    # Count total quizzes attempted
    total_quizzes_attempted = len(user_scores)

    # Count how many times the user got a full score (assuming full score is 100)
    full_score_quizzes = sum(1 for score in user_scores if score.total_scored == 100)

    # Get unique quiz IDs attempted by the user
    unique_quiz_ids = list(set(score.quiz_id for score in user_scores))

    # Calculate average scores for each quiz
    quiz_names = []
    avg_scores = []
    for quiz_id in unique_quiz_ids:
        quiz = Quiz.query.get(quiz_id)  # Fetch quiz details
        quiz_name = quiz.name if quiz else f"Quiz {quiz_id}"
        scores = [score.total_scored for score in user_scores if score.quiz_id == quiz_id]
        avg_score = sum(scores) / len(scores) if scores else 0

        quiz_names.append(quiz_name)
        avg_scores.append(avg_score)

    plt.figure(figsize=(8, 5))
    plt.bar(quiz_names, avg_scores, color="royalblue")
    plt.xlabel("Quizzes")
    plt.ylabel("Average Score (%)")
    plt.title("Quiz Performance Summary")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)  # 🔹 Fixing y-axis from 0 to 100%
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Save the chart to static/images/
    chart_path = f"static/images/user_{user_id}_chart.png"
    plt.savefig(chart_path, format="png", bbox_inches="tight")
    plt.close()

    # Pass summary stats and chart path to the template
    return render_template(
        "user_summary.html",
        name=name,
        total_quizzes=total_quizzes_attempted,
        full_scores=full_score_quizzes,
        chart_path=chart_path
    )


@app.route('/admin_summary/<name>')
def admin_summary(name):
    total_users = User.query.count()
    attempted_users = Score.query.distinct(Score.user_id).count()
    full_score_users = Score.query.filter(Score.total_scored == 100).distinct(Score.user_id).count()

    # Avoid division by zero
    attempted_percent = round((attempted_users / total_users) * 100, 2) if total_users else 0
    full_score_percent = round((full_score_users / attempted_users) * 100, 2) if total_users else 0

    # Get average score per quiz
    quiz_data = db.session.query(
        Quiz.name, db.func.avg(Score.total_scored)
    ).join(Score).group_by(Quiz.id).all()

    quiz_names = [q[0] for q in quiz_data]
    avg_scores = [round(q[1], 2) for q in quiz_data]

    # Generate Bar Chart
    plt.figure(figsize=(8, 5))
    plt.bar(quiz_names, avg_scores, color="royalblue")
    plt.xlabel("Quizzes")
    plt.ylabel("Average Score (%)")
    plt.title("Quiz Performance Summary")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 100)  # Fix Y-axis to 100
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Add percentage labels inside bars
    for i, v in enumerate(avg_scores):
        plt.text(i, v - 5, f"{v}%", ha="center", va="bottom", color="white", fontweight="bold")

    # Save the chart
    chart_path = "static/images/admin_summary_chart.png"
    plt.savefig(chart_path, format="png", bbox_inches="tight")
    plt.close()

    return render_template("admin_summary.html",name=name, 
                           total_users=total_users, 
                           attempted_users=attempted_users, 
                           full_score_users=full_score_users, 
                           full_score_percent=full_score_percent, 
                           chart_path=chart_path)



@app.route('/view_user/<id>/<name>',methods=["GET","POST"])
def edit_user(name,id):
    user = User.query.filter_by(id=id).first()
    return render_template("edit_users.html",name=name,user=user)

@app.route('/delete_user/<id>/<name>',methods=["GET","POST"])
def delete_user(id,name):
    user = User.query.filter_by(id=id).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin_user",name=name))


@app.route('/admin_users/<name>')
def admin_user(name):
    users = User.query.filter_by(role=1).all()  # Fetch only users with role = 1
    return render_template("admin_users.html", name=name, users=users)



#############################################    search #################################################

@app.route("/search1/<name>", methods=['GET','POST'])
def search1(name):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        by_subj = search_by_subject(search_txt)
        if by_subj:
            return render_template("admin_dashboard.html",name=name,subjects=by_subj)
    return redirect(url_for("admin_dashboard",name=name))


def search_by_subject(search_txt):
    subj = Subject.query.filter(Subject.name.ilike(f"%{search_txt}%")).all()
    return subj


@app.route("/search2/<name>", methods=['GET','POST'])
def search2(name):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        by_quiz = search_by_quiz(search_txt)
        if by_quiz:
            return render_template("quiz_dashboard.html",name=name,quizs=by_quiz)
    return redirect(url_for("quiz_dashboard",name=name))

def search_by_quiz(search_txt):
    quiz = Quiz.query.filter(Quiz.name.ilike(f"%{search_txt}%")).all()
    return quiz


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