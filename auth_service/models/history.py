from db.postgres import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import CRUDMixin, IDMixin


class History(Base, IDMixin, CRUDMixin):
    __tablename__ = 'history'

    user_agent = Column(String(255), nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'))
    user = relationship('User', back_populates='history')

    def __init__(self, user_agent: str) -> None:
        self.user_agent = user_agent

    def __repr__(self) -> str:
        return f'<History element {self.user_agent}>'
