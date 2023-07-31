from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import DateTime

from .database import Base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    umbrellas = relationship("Umbrella", back_populates="owner")


class Umbrella(Base):
    __tablename__ = 'umbrellas'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum('available', 'borrowed'), default='available')
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="umbrellas")

class UmbrellaHistory(Base):
    __tablename__ = 'umbrella_history'

    id = Column(Integer, primary_key=True, index=True)
    umbrella_id = Column(Integer, ForeignKey('umbrellas.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    borrowed_at = Column(DateTime, nullable=False)
    returned_at = Column(DateTime)

    umbrella = relationship("Umbrella")
    user = relationship("User")
