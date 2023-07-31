from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

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
