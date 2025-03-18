from flask_sqlalchemy import SQLAlchemy



db=SQLAlchemy()


class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.Integer,nullable=False)
    role=db.Column(db.Integer,default=1)
    fullname=db.Column(db.String,nullable=False)
    qualification=db.Column(db.String,nullable=False)
    DOB = db.Column(db.Date(),nullable=False)
    scores = db.relationship("Score",cascade="all,delete",backref="user",lazy=True)


class Subject(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,unique=True,nullable=False)
    description=db.Column(db.String)
    chapters = db.relationship("Chapter",cascade="all,delete",backref="subject",lazy=True)
    


class Chapter(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,unique=True,nullable=False)
    description=db.Column(db.String)
    Subject_id = db.Column(db.Integer,db.ForeignKey("subject.id"),nullable=False)
    quizes = db.relationship("Quiz",cascade="all,delete",backref="chapter",lazy=True)
    

class Quiz(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    Chapter_id = db.Column(db.Integer,db.ForeignKey("chapter.id"),nullable=False)
    date_of_quiz = db.Column(db.Date(),nullable=False)
    time_duration = db.Column(db.Time(),nullable =False)
    remarks=db.Column(db.String)
    scores= db.relationship("Score",cascade="all,delete",backref="quiz",lazy=True)
    questions = db.relationship("Question",cascade="all,delete",backref="quiz",lazy=True)
    
class Score(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    quiz_id = db.Column(db.Integer,db.ForeignKey("quiz.id"),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    time_stamp = db.Column(db.Integer,nullable=False)
    total_scored = db.Column(db.Integer,nullable=False)

class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    quiz_id = db.Column(db.Integer,db.ForeignKey("quiz.id"),nullable=False)
    question_title = db.Column(db.String,nullable=False)
    question_statement = db.Column(db.String,nullable=False)
    option1 = db.Column(db.String,nullable=False)
    option2 = db.Column(db.String,nullable=False)
    option3 = db.Column(db.String,nullable=False)
    option4 = db.Column(db.String,nullable=False)
    correct_option = db.Column(db.Integer,nullable=False)
