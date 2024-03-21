from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()

def connect(db_url):
    global session
    global engine

    disconnect()

    engine = create_engine(db_url, pool_pre_ping=True)
    Session  = sessionmaker(bind=engine)
    session = Session()




def disconnect():
    global session
    global engine

    if session is not None:
        session.close()

    if engine is not None:
        engine.dispose()

session : Optional[Session] = None
engine : Optional[Engine] = None

connect("postgresql:///task_manager_v4")