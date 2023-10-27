from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
     app = Flask(__name__)
     Bootstrap(app)
     app.debug = True
     
     # bootstrap = Bootstrap(app)
     app.secret_key = 'BetterSecretNeeded123'

     #set the app configuration data 
     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
     
     # initialise db with flask app - necessary because scope of app
     # is only here in create_app, but db is defined globally
     db.init_app(app)
    

     from . import views
     app.register_blueprint(views.main_bp)
     from . import admin
     app.register_blueprint(admin.admin_bp)
     
     @app.errorhandler(404) 
     # Inbuilt function (to Flask) which takes error as parameter
     def not_found(e): 
          return render_template("error.html", error=e)

     # Handles server errors (look-up 'HTTP response status codes')
     @app.errorhandler(500)
     def internal_error(e):
          return render_template("error.html", error=e)
   
     return app
     