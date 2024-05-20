import click
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

cwd = os.getcwd()
print(f"sqlite://{cwd}/scribe.db")
engine = create_engine(f"sqlite:///{cwd}/scribe.db")
db_session = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import scribe.server.models
    Base.metadata.create_all(bind=engine)
