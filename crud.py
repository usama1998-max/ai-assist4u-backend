from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ChatHistory, ChatTabs
from sqlalchemy.exc import SQLAlchemyError


async def save_chat_tab(session: AsyncSession, name: str, user: str, model: str):
    try:
        chat_message = ChatTabs(name=name, user=user, model=model)
        session.add(chat_message)
        await session.commit()
        await session.refresh(chat_message)
        return chat_message
    finally:
        await session.close()


async def get_all_chat_tabs(session: AsyncSession, user: str):
    result = await session.execute(select(ChatTabs).where(ChatTabs.user == user))
    chats = result.scalars().all()
    return [chat.__dict__ for chat in chats]


async def delete_chat_tab(session: AsyncSession, tab_id: int):
    try:
        # Delete all messages related to the given tab_id
        await session.execute(
            ChatTabs.__table__.delete().where(ChatTabs.id == tab_id)
        )
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"Error deleting chat history: {e}")
        return False


async def save_chat(session: AsyncSession, tab_id: int, prompt: str, response: str):
    print(prompt, response, tab_id)
    chat_message = ChatHistory(prompt=prompt, tab=tab_id, response=response)
    session.add(chat_message)
    await session.commit()
    await session.refresh(chat_message)
    return chat_message


async def get_all_chats(session: AsyncSession, tab_id: int):
    result = await session.execute(select(ChatHistory).where(ChatHistory.tab == tab_id))
    chats = result.scalars().all()
    return [chat.__dict__ for chat in chats]


async def delete_chat_history(session: AsyncSession, tab_id: int):
    try:
        # Delete all messages related to the given tab_id
        await session.execute(
            ChatHistory.__table__.delete().where(ChatHistory.tab == tab_id)
        )
        await session.commit()
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        print(f"Error deleting chat history: {e}")
        return False

