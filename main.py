
import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Literal
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="AI Support Agent",
    description="An AI-powered IT support assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY", "test-api-key")
)

class SupportRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)

class SupportResponse(BaseModel):
    message: str
    response: str
    category: str
    


class AIClassification(BaseModel):
    category: Literal[
        "email",
        "network",
        "performance",
        "account",
        "general",
    ]
    response: str






@app.get("/")
def home():
    return {"status": "AI Support Agent is running"}



@app.post("/support", response_model=SupportResponse)
def handle_support_request(request: SupportRequest):
    try:
        ai_response = client.responses.parse(
            model="gpt-4.1-mini",
            text_format=AIClassification,
            instructions=(
                "You are a professional IT support agent. "
                "Respond in the same language as the user's message. "
                "Classify the issue into exactly one category: "
                "email, network, performance, account, or general. "
                "Give clear, numbered troubleshooting steps. "
                "Start with the simplest and safest checks. "
                "Ask a clarifying question if essential information is missing. "
                "Never ask users to share passwords, API keys, or other secrets. "
                "Never claim to have performed an action you have not performed. "
                "Do not recommend disabling security controls or exposing sensitive data."
            ),
            input=request.message,
        )

        parsed = ai_response.output_parsed

        if parsed is None:
            raise ValueError("OpenAI did not return structured output.")

        category = parsed.category
        response = parsed.response

        parsed = ai_response.output_parsed

        if parsed is None:
            raise ValueError("OpenAI did not return structured output.")

        category = parsed.category
        response = parsed.response

        return SupportResponse(
            message=request.message,
            response=response,
            category=category,
        )



    except Exception as e:
        logger.exception("OpenAI request failed")       
        raise HTTPException(
            status_code=502,
            detail="The AI support service is temporarily unavailable.",
        )
