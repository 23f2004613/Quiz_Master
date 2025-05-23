from flask import Flask
from models.models import db
from controllers.api_controller import *


app=None



def setup_app():
    app=Flask(__name__)
    app.secret_key = "your_secret_key"  # Secret key needed for session
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///quiz_master.sqlite3"
    db.init_app(app)
    api.init_app(app)
    app.app_context().push() #direct access to other models like database
    app.debug=True
    print("Quiz_master started...")

setup_app()


from controllers.controller import *
if __name__=="__main__":
    app.run(debug=True)




