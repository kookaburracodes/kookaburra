import importlib
from typing import List, Tuple, Union

from fastapi import Body, FastAPI, HTTPException
from langchain import OpenAI
from langchain.chains import ChatVectorDBChain
from pydantic import BaseModel, validator

app = FastAPI()
MOD_NAME = "kookaburra_deployment.kookaburra"
DEFAULT_REQUEST_PATH = "/sms"


class HeyResponse(BaseModel):
    message: str

    @validator("message")
    def strip_message(cls, v: str) -> str:
        return v.strip()


class Message(BaseModel):
    message: str
    chat_history: List[Tuple[str, str]] = []

    @validator("message")
    def strip_message(cls, v: str) -> str:
        return v.strip()


@app.post("/hey", response_model=HeyResponse)
async def hey(
    message: Message = Body(...),
) -> HeyResponse:
    _kb = importlib.import_module(MOD_NAME)
    llm: Union[OpenAI, ChatVectorDBChain] = _kb.get_llm()
    _in: str = message.message
    _out: str
    if isinstance(llm, (OpenAI)):
        _out = llm(_in)
    elif isinstance(llm, ChatVectorDBChain):
        _out = llm(
            {
                "question": _in,
                "chat_history": message.chat_history,
            }
        )["answer"]
    else:
        raise HTTPException(f"Unsupported LLM type {type(llm)}.")
    return HeyResponse(message=_out)
