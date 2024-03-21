from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
import sqlalchemy
from wtforms import BooleanField, SelectField, StringField
from wtforms.validators import DataRequired, Length


from database import meta, model
from . import utils 

group_bp = Blueprint("group", __name__, url_prefix="/group")

class GroupForm(FlaskForm):
    name = StringField("GroupName", validators=[DataRequired(),Length(max=80)])

# temporarily added
# class TaskForm(FlaskForm):
#     title = StringField("Title", validators=[DataRequired()])
#     is_completed = BooleanField(False, validators=[DataRequired()])
#     assigned_to = SelectField("assigned_to",
#                               validators=[DataRequired()],
#                               choices=[])
    
@group_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_group():
    group_form = GroupForm()

    if group_form.validate_on_submit():
        name = group_form.name.data
        organizer_id = current_user.id

        new_group = model.Group(
            name = name,
            organizer_id = organizer_id,
        )
        
        meta.session.add(new_group)
        meta.session.commit()
        return redirect(url_for('group.view_groups'))

    return render_template("group/add.html", group_form=group_form)

@group_bp.route("/")
@login_required
def view_groups():

    all_groups = (meta.session.query(
        model.Group
    )).all()

    context={
        "all_groups": all_groups,
    }

    return render_template("group/all_groups.html", context=context)

@group_bp.route("/<int:group_id>")
def group_detail(group_id):

    members = []
    group = (
        meta.session.query(
            model.Group
        ).filter(model.Group.id==group_id)
    ).one_or_none()

    members = utils.get_members(group_id)

    tasks = utils.get_tasks(group_id)

    if group:
        context={
            "group": group,
            "members": members,
            "tasks": tasks,
        }
        return render_template("group/group_detail.html", context=context)
    else :
        return redirect(url_for("group.view_groups"))
    

@group_bp.route("/<int:group_id>")
def group_detail1(group_id):

    members = []
    group = (
        meta.session.query(
            model.Group
        ).filter(model.Group.id==group_id)
    ).one_or_none()

    members = utils.get_members(group_id)

    tasks = utils.get_tasks(group_id)


         
    if group:
        context={
            "group": group,
            "members": members,
            "tasks": tasks,
        }
        return render_template("group/group_detail.html", context=context)
    else :
        return redirect(url_for("group.view_groups")) 

@group_bp.route("/edit/<int:group_id>", methods=["GET", "POST"])
def edit_group(group_id):
    
    # 1.  Get data from db
    group = (
        meta.session.query(
            model.Group
        ).filter(model.Group.id==group_id)
    ).one_or_none()

    if group:
        # 2.  Row to form: Pass the db data to the form
        edit_form = GroupForm(**group.__dict__)

        if edit_form.validate_on_submit():
            
            # 3. Form to Dictionay: from edit form data create dictionary
            group.name = edit_form.name.data.strip()
                # 4. Dictionary to Row: Pass the dictionary to model update() method
            try:
                meta.session.commit()
                # print("error2")
                print(f'our task before edit is {group.__dict__}')
                
            except sqlalchemy.exc.IntegrityError:
                return redirect(url_for("group.view_groups"))
            
            meta.session.refresh(group)
            print(f'out task after edit is {group.__dict__}')
            return redirect(url_for("group.view_groups"))

        return render_template("group/edit_group.html", form=edit_form)
    
    print(f"Group id {group_id} Not Exist")
    return redirect(url_for("group.view_groups")) 

@group_bp.route("/delete/<int:group_id>")
@login_required
def delete_group(group_id):

    group = (meta.session.query(
        model.Group
    ).filter(
        model.Group.id == group_id
    ))

    user_group = (meta.session.query(
        model.UserGroup
    ).filter(
        model.UserGroup.user_id == current_user.id,
        model.UserGroup.group_id == group_id,
    )
    )

    # print(user_group.user_id)
    # print(user_group.group_id)

    if group:
        # group.delete()
        user_group.delete()
        group.delete()
        try:
            meta.session.flush()
            meta.session.commit()
        except sqlalchemy.exc.InternalError as e:
                meta.session.rollback()
                return redirect(url_for('group.view_groups'))
            

    return redirect(url_for('group.view_groups'))