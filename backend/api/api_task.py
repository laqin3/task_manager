import datetime
from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
import sqlalchemy
from sqlalchemy import or_
from wtforms import  BooleanField, DateField, SelectField, StringField, widgets
from wtforms.validators import DataRequired, Length

from database import meta, model
from . import utils

task_bp = Blueprint("task", __name__, url_prefix="/task")



class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=80)])
    description = StringField("Description", validators=[DataRequired(), Length(max=250)])
    due_date = DateField("Due_date", validators=[DataRequired()])
    is_completed = BooleanField("Is_completed", default=False)
    is_deleted = BooleanField("Is_deleted", default=False)
    user_id = StringField("User Id", validators=[DataRequired()])
    assigned_to = SelectField("Assigned to", validators=[DataRequired()],
                              choices=["None",user_id])

class SearchForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])



@task_bp.route("/")
@login_required
def personal_tasks():
    user_name = (current_user.first_name+" "+current_user.last_name).strip()
    print("current user is "+user_name+ ", id is:")
    print(current_user.id)

    # or_statement 
    or_statement = [model.Task.user_id == current_user.id,
        model.Task.assigned_to==user_name.strip(),]
    

    all_tasks = (meta.session.query(
        model.Task
    ).filter(
        or_(
            *or_statement
        )
    )
    .order_by( 
        model.Task.is_completed.asc(),
        model.Task.due_date.desc(),
    )).all()

    context = {
        "all_tasks": all_tasks,
    }

    return render_template("tasks/personal_tasks.html", context=context)


@task_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_task():
    form = TaskForm()

    if form.validate_on_submit:
        title = form.title.data
        description = form.description.data
        due_date_string = form.due_date.data
        user_name = current_user.first_name+" "+current_user.last_name
        create_date = datetime.date.today()
        assigned_to = user_name
        

        new_task = model.Task(
            title = title,
            description = description,
            due_date = due_date_string,
            create_date = create_date,
            is_completed = False,
            is_deleted = False,
            user_id = current_user.id,
            assigned_to = assigned_to,
        )

        try:
            meta.session.add(new_task)
            meta.session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            meta.session.rollback()
            return render_template("tasks/create_task.html", form=form)

        return redirect(url_for("task.personal_tasks"))

    return render_template("tasks/create_task.html", form=form)

@task_bp.route("/<int:task_id>")
def task_detail(task_id):
    task = (
        meta.session.query(
            model.Task
        ).filter(model.Task.id==task_id)
    ).one_or_none()

    if task:
        context = {
            "task": task,
        }
        return render_template("tasks/task_detail.html", context=context)
    else :
        print("Task Not Exist")
        return redirect(url_for("task.personal_tasks"))
    

@task_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    
    # 1.  Get data from db
    task = (
        meta.session.query(
            model.Task
        ).filter(model.Task.id==task_id)
    ).one_or_none()

    if task:
        # 2.  Row to form: Pass the db data to the form
        edit_form = TaskForm(**task.__dict__)

        edit_form.assigned_to.choices = utils.get_task_related_group_users(task_id)

        if edit_form.validate_on_submit():
            # 3. Form to Dictionay: from edit form data create dictionary
            # user_assigned = (meta.session.query(
            #     model.User
            # ).filter(
            #     model.User.first_name==edit_form.assigned_to.data.strip().split(" ")[0],   
            # )).one_or_none()

            edited_task={
                "title" : edit_form.title.data.strip(),
                "description": edit_form.description.data.strip(),
                "due_date": edit_form.due_date.data,
                "assigned_to": edit_form.assigned_to.data.strip(),
                }

            # 4. Dictionary to Row: Pass the dictionary to model update() method
            task.update(edited_task)
            meta.session.flush()
            meta.session.commit()
            print(f'our task before edit is {task.__dict__}')
            meta.session.refresh(task)
            print(f'out task after edit is {task.__dict__}')
            return redirect(url_for("task.personal_tasks"))

        return render_template("tasks/edit_task.html", form=edit_form)
    
    print("Task Not Exist")
    return redirect(url_for("task.personal_tasks"))

@task_bp.route("/mark_complete/<int:task_id>")
@login_required
def is_complete(task_id):
    task = (
        meta.session.query(
            model.Task
        ).filter(model.Task.id==task_id)
    ).one_or_none()

    if task:
        task_status =task.is_completed
        if task_status == False:
            task.is_completed = True
        else:
            task.is_completed = False

        meta.session.commit()
        # print(f'our task before edit is {task.__dict__}')
        meta.session.refresh(task)
        # print(f'out task after edit is {task.__dict__}')
        return redirect(url_for("task.personal_tasks"))
    
    print("Task Not Exist")
    return redirect(url_for("task.personal_tasks"))

@task_bp.route("/mark_delete/<int:task_id>")
@login_required
def is_delete(task_id):
    task = (
        meta.session.query(
            model.Task
        ).filter(model.Task.id==task_id)
    ).one_or_none()

    if task:
        task_status =task.is_deleted
        if task_status == False:
            task.is_deleted = True
        else:
            task.is_deleted = False

        meta.session.commit()
        # print(f'our task before edit is {task.__dict__}')
        meta.session.refresh(task)
        # print(f'out task after edit is {task.__dict__}')
        return redirect(url_for("task.personal_tasks"))
    
    print("Task Not Exist")
    return redirect(url_for("task.personal_tasks"))

@task_bp.route("/search", methods=["GET", "POST"])
@login_required
def search():
    search_form = SearchForm()

    tasks = meta.session.query(
        model.Task
    )
    if search_form.validate_on_submit:
        
        input_search_data = search_form.title.data
        print(input_search_data)
        all_task_count = 0
        
        print(len(tasks.all()))
        if len((tasks.filter(model.Task.title.ilike(f"%{input_search_data.strip()}%"))).all()) > 0:
            tasks = tasks.filter(model.Task.title.ilike(f"%{input_search_data.strip()}%"), model.Task.user_id==current_user.id)
            print(f"number of title same as {input_search_data.strip()} is "+str(len(tasks.all())))
        elif len((tasks.filter(model.Task.description.ilike(f"%{input_search_data.strip()}%"))).all()) > 0:
            tasks = tasks.filter(model.Task.description(f"%{input_search_data.strip()}%"), model.Task.user_id==current_user.id)
            print(f"number of description same as {input_search_data.strip()} is "+str(len(tasks.all())))
        else:
            print("No Task Found")
            tasks = tasks.filter(model.Task.id==current_user.id)
            all_task_count = tasks.all().count
           

        context = {
            "tasks": tasks.all(),
            "all_task_count": all_task_count,
        }
        return render_template("tasks/search_result.html", context=context)

    print("else")
    return redirect(url_for('task.personal_tasks'))


    