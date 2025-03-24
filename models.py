from sqlalchemy import Column, Integer, String, ForeignKey
from config import Base


class ChatTabs(Base):
    __tablename__ = "chat_tabs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user = Column(String, nullable=False)
    model = Column(String, nullable=False)


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, nullable=False)
    response = Column(String, nullable=False)
    tab = Column(Integer, ForeignKey('chat_tabs.id'))
