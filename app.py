import json
from fastapi import FastAPI, Depends, Body
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging
import asyncio
from asyncpg.exceptions import InterfaceError
from sqlalchemy.ext.asyncio import AsyncSession
# from validate import ChatHistoryRequest
from config import engine, Base, get_db
from contextlib import asynccontextmanager
import crud
import uvicorn

load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_MODEL = "gemini-2.0-flash-001"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# async def reset_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)
#         await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())
        await init_db()  # Ensures the DB is initialized in the same loop
        yield
    except InterfaceError:
        logger.error("Database connection failed, retrying...")
        await asyncio.sleep(5)  # ✅ Wait before retrying
        await init_db()
    yield

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


@app.get("/")
async def home():
    return JSONResponse(content={"message": "hello world"}, status_code=200)


async def generate_response_stream(prompt: str):
    try:
        yield json.dumps({"message": "", "status": "ready"})
        response = model.generate_content(prompt, stream=True)
        for chunk in response:
            yield json.dumps({"message": chunk.text, "status": "stream"})
            await asyncio.sleep(0.01)

        yield json.dumps({"message": "", "status": "stop"})

    except Exception as e:
        logger.error(str(e))
        yield json.dumps({"status": 500, "error": "Something went wrong!"})


@app.post("/chat")
async def chat(request: dict = Body(...)):
    prompt = request.get("prompt", "")

    return StreamingResponse(generate_response_stream(prompt), media_type="application/json")


# CHAT HISTORY
@app.post("/chat-history/save")
async def save_chat_history(
        request: dict = Body(...),
        session: AsyncSession = Depends(get_db)
):
    try:
        prompt = request.get("prompt", "default prompt")
        response = request.get("response", "default response")
        tab_id = request.get("tab_id", 1)

        await crud.save_chat(session=session, prompt=prompt, response=response, tab_id=tab_id)
        return JSONResponse(content={"message": "successfully saved!"}, status_code=200)
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(content={"error": "Something went wrong!"}, status_code=500)


@app.get("/chat-history/get")
async def get_chat_history(tab: int, session: AsyncSession = Depends(get_db)):
    tmp = await crud.get_all_chats(session=session, tab_id=tab)
    tmp_serializable = jsonable_encoder(tmp)
    return JSONResponse(content={"message": tmp_serializable}, status_code=200)


@app.delete("/chat-history/clear")
async def clear_chat_history(tab: int, session: AsyncSession = Depends(get_db)):
    success = await crud.delete_chat_history(session=session, tab_id=tab)

    if success:
        return JSONResponse(content={"message": "Chat tab removed successfully!"}, status_code=200)
    return JSONResponse(content={"error": "Failed to remove chat tab!"}, status_code=500)


# CHAT TABS
@app.post("/chat-tab/save")
async def save_chat_tab(
        request: dict = Body(...),
        session: AsyncSession = Depends(get_db)
):
    try:
        name = request.get("name", "new chat")
        user = request.get("user", "new user")
        ai_model = request.get("model", GEMINI_MODEL)

        await crud.save_chat_tab(session=session, name=name, user=user, model=ai_model)
        return JSONResponse(content={"message": "successfully saved!"}, status_code=200)
    except Exception as e:
        logger.error(str(e))
        return JSONResponse(content={"error": "Something went wrong!"}, status_code=500)


@app.get("/chat-tab/get")
async def get_chat_tabs(user: str, session: AsyncSession = Depends(get_db)):
    tmp = await crud.get_all_chat_tabs(session=session, user=user)
    tmp_serializable = jsonable_encoder(tmp)
    return JSONResponse(content={"message": tmp_serializable}, status_code=200)


@app.delete("/chat-tab/clear")
async def clear_chat_tab(tab: int, session: AsyncSession = Depends(get_db)):
    success = await crud.delete_chat_tab(session=session, tab_id=tab)

    if success:
        return JSONResponse(content={"message": "Chat tab removed successfully!"}, status_code=200)
    return JSONResponse(content={"error": "Failed to remove chat tab!"}, status_code=500)

if __name__ == "__main__":
    asyncio.run(uvicorn.run(app, host="0.0.0.0", port=8000))