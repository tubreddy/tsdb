import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Habitat(Base):
    __tablename__ = 'habitat'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    code = Column(Integer, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    panchayat_code = Column(Integer, nullable=True)
    mandal_code = Column(Integer, nullable=True)
    district_code = Column(Integer, nullable=True)


engine = create_engine('sqlite:///telanganahabitatdb.db')
Base.metadata.create_all(engine)

def display():
    a= [1,2,3,4]
    print(a)


