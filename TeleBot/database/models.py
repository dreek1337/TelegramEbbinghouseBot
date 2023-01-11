from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class RepeatInformation(DeclarativeBase):
    __tablename__ = 'repitinformation'

    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer)
    header = Column('header', String)
    information = Column('information', String)

    def __repr__(self):
        return "".format(self.header)
