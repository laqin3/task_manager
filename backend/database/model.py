from flask_login import UserMixin
from sqlalchemy import BIGINT, VARCHAR, Boolean, Column, DateTime, ForeignKey, Integer, Text, func
from werkzeug.security import generate_password_hash, check_password_hash

from . import meta
from .meta import Base



class User(UserMixin, Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True)
    first_name = Column(Text, nullable=False)
    last_name = Column(Text, nullable=False)
    email = Column(VARCHAR(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not readabble")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Task(Base):
    __tablename__= "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    due_date = Column(
        DateTime(timezone=False), 
        nullable=False,
        )
    create_date = Column(
        DateTime(timezone=False), 
        nullable=False,
        default=func.now(),
        server_default=func.now(),
        )
    completed_date = Column(
        DateTime(timezone=False), 
        nullable=True,
        default=None,
        server_default=None,
        )
    is_deleted = Column(Boolean, default=False)
    is_completed = Column(Boolean, default=False)
    user_id = Column(BIGINT, ForeignKey("users.id", name="created_by"), nullable=False, )
    assigned_to = Column(Text, nullable=False)

# The id, is_deleted, user_id of the task should not be editable (pop from the update() function of model.py) 
    def update(self, data):
        data.pop("id", None)
        data.pop("is_deleted", None)
        data.pop("user_id", None)

        for key, value in data.items():
            setattr(self, key, value)
        
        meta.session.flush()
        return self

    @staticmethod
    def get_user_name(user_id):
        user = None
        user = (meta.session.query(
            User
        ).filter(
            User.id==user_id
            )
        ).one_or_none()

        return user
    
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    organizer_id = Column(BIGINT, ForeignKey("users.id"), nullable=False, )


class UserGroup(Base):
    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))
    group_id = Column(BIGINT, ForeignKey("groups.id", ondelete="CASCADE"))
