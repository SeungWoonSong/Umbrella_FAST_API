from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .database import Base
from pytz import timezone
from datetime import datetime



Base = declarative_base()
KST = timezone('Asia/Seoul')

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True)
    umbrellas = relationship("Umbrella", back_populates="owner")
    history = relationship("UmbrellaHistory", back_populates="user")

class Umbrella(Base):
    __tablename__ = 'umbrellas'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum('available', 'borrowed', 'lost'), default='available')
    location = Column(String(255))
    owner_name = Column(String(255), ForeignKey('users.name'))

    owner = relationship("User", back_populates="umbrellas")

class UmbrellaHistory(Base):
    __tablename__ = 'umbrella_history'

    id = Column(Integer, primary_key=True, index=True)
    umbrella_id = Column(Integer, ForeignKey('umbrellas.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    borrowed_at = Column(DateTime, default=datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S'))
    returned_at = Column(DateTime)

    umbrella = relationship("Umbrella")
    user = relationship("User", back_populates="history")
