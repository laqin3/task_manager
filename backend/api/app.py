from database import meta, model

from flask import Flask, render_template
from flask_login import LoginManager


from .api_auth import auth_bp
from .api_task import task_bp
from .api_group import group_bp
from .api_user_group import usergroup_bp
from .api_profile import profile_bp

login_manager = LoginManager()

app = Flask(__name__, template_folder="../../frontend/templates")

app.config["SECRET_KEY"] = "-CP3A8JgRnyxni7vtbrZLC0uGqXjxyEg8qqPJSk12iE"

login_manager.init_app(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth_bp)
app.register_blueprint(task_bp)
app.register_blueprint(group_bp)
app.register_blueprint(usergroup_bp)
app.register_blueprint(profile_bp)


@app.route("/")
def homepage():
    return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
    return meta.session.query(model.User).get(user_id)