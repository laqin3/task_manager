from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from database import model, meta

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

class UserForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name  = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])

@profile_bp.route("/view")
@login_required
def view_profile():
    profile = (meta.session.query(
        model.User
    ).filter(
        model.User.id == current_user.id
    )).one()

    user_form = UserForm(
        **profile.__dict__
    )

    context = {
        "user_form": user_form,
        "is_editible": False,
    }
    return render_template("profile/view_profile.html", context=context)

@profile_bp.route("/update", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = (meta.session.query(
        model.User
    ).filter(
        model.User.id == current_user.id
    )).one()

    edit_form = UserForm(
        **profile.__dict__
    )

    if edit_form.validate_on_submit():
        profile.first_name = edit_form.first_name.data.strip()
        profile.last_name = edit_form.last_name.data.strip()
        profile.email = edit_form.email.data.strip()
        meta.session.commit()
        return redirect(url_for('profile.view_profile'))
    
    context = {
        "user_form": edit_form,
        "is_editible": True,
    }
    return render_template("profile/view_profile.html", context=context)

