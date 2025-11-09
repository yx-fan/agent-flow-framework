import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import CurrentConfig
from api.routes.chat_route import router as chat_router
from core.registry import AgentRegistry, NodeRegistry
from agents.hello_agent import HelloAgent
from nodes.greeting_node import GreetingNode

app = FastAPI(title="MCP Orchestrator API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

# CORS Configuration - use environment variable for production
cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
if cors_origins == "*":
    # Development: allow all origins
    allow_origins = ["*"]
else:
    # Production: use specific origins
    allow_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(chat_router)

# Register your Agents and Nodes here
AgentRegistry.register("HelloAgent", HelloAgent)
NodeRegistry.register("GreetingNode", GreetingNode)

@app.get("/health")
def health():
    return {"status": "ok"}