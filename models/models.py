from conf import DB_CONFIG
from db import create
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base, engine = create(DB_CONFIG)

class bc10_clients(Base):
    __tablename__ = 'bc10_clients'
    __table_args__ = {'autoload': True}
    oasis = relationship('bc10_oasis', backref='bc10_oasis', lazy='dynamic')

    @property
    def serialize(self):
        return {
            'client_id': self.client_id,
            'name': self.name
        }

class bc10_transactions(Base):
    __tablename__ = 'bc10_transactions'
    __table_args__ = {'autoload': True}

    @property
    def serialize(self):
        return {
           # 'from': self.from,
           'id': self.id,
           'client_id': self.client_id,
           'content': self.content,
           'datetime': self.datetime,
           'operator_id': self.operator_id,
           'to': self.to,
           'status': self.status,
           'type': self.type,

        }


class bc10_oasis(Base):
    __tablename__ = 'bc10_oasis'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    oasis_id = Column(Integer, nullable=False, unique=True)
    oasis_name = Column(String(250), nullable=False, unique=True)
    bc10_clients_id = Column('bc10_clients_id', ForeignKey('bc10_clients.client_id'))
    status = Column('status', Enum('active', 'disabled'), nullable=False)

    @property
    def serialize(self):
        return {
            'bc10_client': self.bc10_oasis.client_id,
            'oasis_id': self.oasis_id,
            'oasis_name': self.oasis_name,
            'status': self.status
        }

Base.metadata.create_all(engine)
