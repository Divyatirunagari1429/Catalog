import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class FoundationCName(Base):
    __tablename__ = 'foundationcname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="foundationcname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class FName(Base):
    __tablename__ = 'foundationname'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    shade = Column(String(100))
    quantity = Column(String(10))
    price = Column(String(10))
    skintype = Column(String(100))
    date = Column(DateTime, nullable=False)
    foundationcnameid = Column(Integer, ForeignKey('foundationcname.id'))
    foundationcname = relationship(
        FoundationCName, backref=backref(
            'foundationname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="foundationname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'shade': self. shade,
            'quantity': self. quantity,
            'skintype': self. skintype,
            'price': self. price,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///found.db')
Base.metadata.create_all(engin)
