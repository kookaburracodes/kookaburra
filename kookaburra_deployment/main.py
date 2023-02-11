import importlib
from typing import Union

from fastapi import Body, FastAPI, HTTPException
from langchain import ConversationChain, LLMChain, OpenAI
from langchain.agents import AgentExecutor
from pydantic import BaseModel, validator

app = FastAPI()
MOD_NAME = "kookaburra_deployment.kookaburra"


class HeyResponse(BaseModel):
    message: str

    @validator("message")
    def strip_message(cls, v: str) -> str:
        return v.strip()


class Message(BaseModel):
    message: str

    @validator("message")
    def strip_message(cls, v: str) -> str:
        return v.strip()


@app.post("/hey", response_model=HeyResponse)
async def hey(message: Message = Body(...)) -> HeyResponse:
    _message = message.message
    _kb = importlib.import_module(MOD_NAME)
    llm: Union[
        OpenAI,
        LLMChain,
        AgentExecutor,
        ConversationChain,
    ] = _kb.get_llm()
    if isinstance(llm, (OpenAI)):
        return HeyResponse(message=llm(_message))
    elif isinstance(llm, (LLMChain, AgentExecutor)):
        return HeyResponse(message=llm.run(_message))
    elif isinstance(llm, ConversationChain):
        return HeyResponse(message=llm.predict(_message))
    else:
        raise HTTPException(f"Unsupported LLM type {type(llm)}.")
