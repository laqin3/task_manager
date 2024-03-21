from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import login_user, current_user, logout_user

from flask_wtf import FlaskForm
import sqlalchemy
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Length

from database import meta, model

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=20)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=20)])

@auth_bp.route("/")
def index():
    return jsonify({"message":"Hello World"})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    print("Hello world")
    if not current_user.is_authenticated:
        user_form = UserForm()

        if user_form.validate_on_submit():
            email = user_form.email.data
            password = user_form.password.data

            print(f"{email=}, {password=}")

            user = (
                meta.session.query(
                    model.User
                    ).filter(
                        model.User.email == email
                        )
            ).one_or_none()

            user_error = None

            if user is None:
                print(f"{email} does not exist")
                user_error = "Invalid Credentials"
            elif not user.verify_password(user_form.password.data):
                print(f"Invalid passwrod for {email}")
                user_error = "Invalid Credentials"

            if user_error is not None:
                print("lets print the error")
                return render_template("auth/login.html", user_form=user_form, error=user_error)
            
            login_user(user, remember=True)

            next = request.args.get("next")

            return redirect(next or url_for("homepage"))

        return render_template("auth/login.html", user_form=user_form)
    
    return redirect(url_for("homepage"))

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if not current_user.is_authenticated:
        registration_form = RegistrationForm()

        if registration_form.validate_on_submit():
            first_name = registration_form.first_name.data
            last_name = registration_form.last_name.data
            email = registration_form.email.data
            password = registration_form.password.data

            print(f"{email=}, {password=}, {first_name=}, {last_name=}")
            new_user = model.User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
            )

            try:
                meta.session.add(new_user)
                meta.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                meta.session.rollback()
                return render_template("auth/register.html", registration_form=registration_form, error="This email is already taken")
            
            return redirect(url_for("auth.login"))
            
        return render_template("auth/register.html", registration_form = registration_form)
    
    return redirect(url_for("homepage"))

@auth_bp.route("/logout")
def logout():
    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for("homepage"))