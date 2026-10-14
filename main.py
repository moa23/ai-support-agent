
import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="AI Support Agent",
    description="An AI-powered IT support assistant",
    version="1.0.0",
)

client = OpenAI()

class SupportRequest(BaseModel):
    message: str = Field(min_length=3, max_length=2000)

class SupportResponse(BaseModel):
    message: str
    response: str
    category: str


def categorize_request(message: str) -> tuple[str, str]:
    text = message.lower()

    if any(word in text for word in ["outlook", "email", "e-mail"]):
        return "email", "Check your mailbox access."

    if any(word in text for word in ["wi-fi", "wifi", "internet", "network"]):
        return "network", "Check your network connection."

    if any(word in text for word in ["slow", "slowly", "performance"]):
        return "performance", "Check resource usage and restart if appropriate."

    if any(word in text for word in ["password", "login", "sign in", "locked"]):
        return "account", "Check your credentials and account status."

    return "general", "Gather more information about the issue."


@app.get("/")
def home():
    return {"status": "AI Support Agent is running"}



@app.post("/support", response_model=SupportResponse)
def handle_support_request(request: SupportRequest):
    try:
        ai_response = client.responses.create(
            model="gpt-4.1-mini",

        instructions=(
            "You are a professional IT support agent. "
            "Respond in the same language as the user's message. "
            "Classify the issue into exactly one category: "
            "email, network, performance, account, or general. "
            "Return your answer in this exact format:\n"
            "CATEGORY: <category>\n"
            "RESPONSE: <helpful troubleshooting response>\n"
            "Give clear, numbered troubleshooting steps. "
            "Start with the simplest and safest checks. "
            "Ask a clarifying question if essential information is missing. "
            "Never ask users to share passwords, API keys, or other secrets. "
            "Never claim to have performed an action you have not performed. "
            "Do not recommend disabling security controls or exposing sensitive data."
        ),

            input=request.message,
        )

        result = ai_response.output_text.strip()

        category = "general"
        response = result

        for line in result.splitlines():
            if line.upper().startswith("CATEGORY:"):
                proposed_category = line.split(":", 1)[1].strip().lower()
                allowed_categories = {
                    "email", "network", "performance", "account", "general"
                }
                if proposed_category in allowed_categories:
                    category = proposed_category

        if "RESPONSE:" in result:
            response = result.split("RESPONSE:", 1)[1].strip()

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
