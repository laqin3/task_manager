from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from database import model, meta

usergroup_bp = Blueprint("usergroup", __name__, url_prefix="/user_group")

class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])

@usergroup_bp.route("/add_member/<int:group_id>", methods=["GET", "POST"])
@login_required
def add_member(group_id):
    
    user_form = UserForm()
    if user_form.validate_on_submit:
        print("hi")
        user_email = user_form.email.data
        print(user_email)
        user = (meta.session.query(
            model.User
        ).filter(
            model.User.email==user_email
        )).one_or_none()

        if user:
            new_user_group = model.UserGroup(
                user_id=user.id,
                group_id = group_id,
            )
            print(new_user_group)
            meta.session.add(new_user_group)
            meta.session.commit()
            return redirect(url_for("group.group_detail", group_id=group_id))
        else:
            print("User Not Exist")
    
    return redirect(url_for("group.group_detail", group_id=group_id))

@usergroup_bp.route("/remove_member/<int:group_id>", methods=["GET", "POST"])
@login_required
def remove_member(group_id):
    
    user_form = UserForm()
    if user_form.validate_on_submit:
        user_email = user_form.email.data
        
        if user_email:
            print("user_email is ")
            print(user_email)
            user = (meta.session.query(
                model.User
            ).filter(
                model.User.email==user_email.strip()
            )).one_or_none()

            if user is not None and group_id is not None:
                user_in_group = (meta.session.query(
                    model.UserGroup
                ).filter(
                    model.UserGroup.user_id==user.id,
                    model.UserGroup.group_id==group_id,
                )).one_or_none()

                if user_in_group:
                    meta.session.delete(user_in_group)
                    meta.session.flush()
                    meta.session.commit()
                    return redirect(url_for("group.group_detail", group_id=group_id))
                else:
                    print(f"{user_email} or {group_id} NOT EXIST")

    return redirect(url_for("group.group_detail", group_id=group_id))
