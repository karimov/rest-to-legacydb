from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def create(db_config):
    engine = create_engine(db_config)
    Base = declarative_base(engine)
    return Base, engine

def loadsession(db_conf):
    engine = create_engine(db_conf)
    Session = sessionmaker(bind=engine)
    return Session()


