from database import model, meta


def get_members(group_id):
    '''
    select users.*, user_groups.group_id from users left join user_groups on users.id = user_groups.id where user_groups.group_id=4;
    '''
    members = meta.session.query(
        model.User
    ).select_from(
        model.User
    ).outerjoin(
        model.UserGroup,
        model.User.id == model.UserGroup.user_id
    ).filter(
        model.UserGroup.group_id==group_id
    ).order_by(
        model.User.id.asc()
    )

    return members

def get_tasks(group_id):
    '''
    select * from tasks left join user_groups on tasks.user_id = user_groups.user_id where user_group.group_id=4;
    '''
    tasks = meta.session.query(
        model.Task
    ).select_from(
        model.Task
    ).outerjoin(
        model.UserGroup,
        model.Task.user_id == model.UserGroup.user_id,
    ).filter(
        model.UserGroup.group_id==group_id,
    ).order_by(
        model.Task.is_completed.asc(),
        model.Task.due_date.asc(),
    )

    return tasks

'''
    select distinct user_groups.user_id from user_groups 
    where user_groups.group_id =(
        select distinct user_groups.group_id from user_groups
          where user_groups.user_id in (
            select tasks.user_id from tasks where tasks.id=1
            ));
    '''
def get_task_related_group_users(task_id):   
    task = (meta.session.query(
        model.Task
    ).filter(model.Task.id==task_id)).one_or_none()
    print(task.user_id) #1


    user_group = (meta.session.query(
        model.UserGroup
    ).distinct(model.UserGroup.user_id).filter(model.UserGroup.user_id==task.user_id)).one_or_none()
    try:
        print(user_group.group_id) #2
    except AttributeError:
        print("user does not belong to any group")
        return ["None", task.get_user_name(task.user_id).first_name +" "+task.get_user_name(task.user_id).last_name]

    # select distinct user_groups.user_id from user_groups  where user_groups.group_id=2;
    group_id_related_user_groups = (meta.session.query(
        model.UserGroup
        ).distinct(model.UserGroup.user_id)
             .filter(model.UserGroup.group_id==user_group.group_id)).all()
    print(group_id_related_user_groups)

    user_name_list = []
    for user_group  in group_id_related_user_groups:
        user = (meta.session.query(
            model.User
        ).filter(model.User.id==user_group.user_id)).one_or_none()
        user_name_list.append(user.first_name + " "+ user.last_name)
    
    print(user_name_list)
    return user_name_list

# below one doesn't work
def get_task_related_group_users1(task_id):
    group_id = (meta.session.query(
        (model.UserGroup.group_id).label("user_group_id")
        ).select_from(
            model.UserGroup
        ).join(
            model.Task,
            model.UserGroup.user_id==model.Task.user_id
        ).filter(
            model.Task.id==task_id
        )    
    ).one_or_none()
    print("gorup id is ")
    print(group_id)

    user_ids = (meta.session.query(
        (model.UserGroup.user_id).label("group_user_ids")
    ).select_from(
        model.UserGroup
    ).filter(
        model.UserGroup.group_id==group_id.c.user_group_id
    )).subquery("user_ids")

    group_users = (meta.session.query(
        model.User
    ).filter(
        model.User.id==user_ids.c.group_user_ids
    )).scalar()

    return [group_users]


