select users.*, user_groups.group_id from users left join user_groups on users.id = user_groups.id where user_groups.group_id=4;

select * from tasks left join user_groups on tasks.user_id = user_groups.user_id where user_group.group_id=4;

select user_groups.* from user_groups left join users on user_groups.user_id=users.id left join groups on user_groups.group_id=groups.id left join tasks on tasks.user_id = users.id where tasks.title = 'Task2';

-- task_id related user_group
select tasks.title, user_groups.user_id, user_groups.group_id from tasks inner join user_groups on tasks.user_id=user_groups.user_id where tasks.id=1;

--  group_id from a task_id without join
select user_groups.group_id from user_groups where user_groups.user_id in (select tasks.user_id from tasks where tasks.id=1);
--  group_id from a task_id with join
select user_groups.group_id from tasks inner join user_groups on tasks.user_id=user_groups.user_id where tasks.id=1;

-- users in a group related to a task_id without join
select distinct user_groups.user_id from user_groups where user_groups.group_id =(select distinct user_groups.group_id from user_groups where user_groups.user_id in (select tasks.user_id from tasks where tasks.id=1));
-- users in a group related to a task_id with join
select user_groups.user_id from user_groups where user_groups.group_id =(select user_groups.group_id from tasks inner join user_groups on tasks.user_id=user_groups.user_id where tasks.id=1);

-- all task title in a group related to a task_id
select tasks.title from tasks where tasks.user_id in(select user_groups.user_id from user_groups where user_groups.group_id =(select user_groups.group_id from user_groups where user_groups.user_id in (select tasks.user_id from tasks where tasks.id=1)));
select tasks.title from tasks where tasks.user_id in (select user_groups.user_id from user_groups where user_groups.group_id =(select user_groups.group_id from tasks inner join user_groups on tasks.user_id=user_groups.user_id where tasks.id=1));
