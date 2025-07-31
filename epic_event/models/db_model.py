from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from epic_event.settings import DB_PATH


engine = create_engine(DB_PATH)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


def initialize_database():
    Base.metadata.create_all(engine)



