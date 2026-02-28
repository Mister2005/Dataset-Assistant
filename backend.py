import os
import io
import base64
import uuid
import time
import logging
from contextlib import asynccontextmanager

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Verify API key is set
if not os.getenv("GOOGLE_API_KEY"):
    logger.error("GOOGLE_API_KEY not found in environment variables!")
    raise ValueError("GOOGLE_API_KEY must be set in .env file")

# ---------------------------------------------------------------------------
# App lifecycle management
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("Starting Titanic Chat Agent API...")
    logger.info(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
    yield
    logger.info("Shutting down Titanic Chat Agent API...")
    # Cleanup any remaining matplotlib figures
    plt.close('all')

# ---------------------------------------------------------------------------
# App & data setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Titanic Chat Agent API",
    description="AI-powered chatbot for analyzing the Titanic dataset",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."}
    )

DATA_PATH = os.path.join(os.path.dirname(__file__), "titanic.csv")

try:
    df = pd.read_csv(DATA_PATH)
    logger.info(f"Successfully loaded dataset from {DATA_PATH}")
except Exception as e:
    logger.error(f"Failed to load dataset: {e}")
    raise

# ---------------------------------------------------------------------------
# LangChain agent
# ---------------------------------------------------------------------------

def _get_agent():
    """Return a LangChain pandas-dataframe agent backed by Gemini."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        max_retries=5,
    )

    SYSTEM_PREFIX = (
        "You are a helpful data-analysis assistant. You have access to a pandas "
        "DataFrame called `df` that contains the Titanic passenger dataset.\n\n"
        "Columns: PassengerId, Survived (0/1), Pclass (1/2/3), Name, Sex, Age, "
        "SibSp, Parch, Ticket, Fare, Cabin, Embarked (C/Q/S).\n\n"
        "When the user asks for a visualization (chart, plot, histogram, bar chart, "
        "pie chart, etc.), generate the matplotlib/seaborn code to create it. "
        "IMPORTANT: Always use `plt.savefig('__chart__.png', bbox_inches='tight', dpi=100)` "
        "to save the chart. Always call `plt.close()` after saving to prevent memory issues.\n\n"
        "For text answers, be concise and include the relevant numbers/statistics."
    )

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        allow_dangerous_code=True,
        prefix=SYSTEM_PREFIX,
    )
    return agent


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    chart_base64: str | None = None  # base64-encoded PNG, if a chart was generated


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "dataset_loaded": len(df) > 0,
        "rows": len(df),
        "columns": len(df.columns)
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Process a chat question about the Titanic dataset"""
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")
    
    logger.info(f"Received question: {question}")

    agent = _get_agent()

    # Unique temp filename so concurrent requests don't collide
    chart_filename = f"__chart_{uuid.uuid4().hex[:8]}__.png"

    # Retry with exponential backoff for rate-limit (429) errors
    max_retries = 3
    result = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Processing question (attempt {attempt + 1}/{max_retries})...")
            result = agent.invoke(
                {"input": question.replace("__chart__.png", chart_filename)}
            )
            logger.info("Question processed successfully")
            break
        except Exception as exc:
            err_str = str(exc)
            logger.error(f"Error on attempt {attempt + 1}: {err_str}")
            
            if "429" in err_str and attempt < max_retries - 1:
                wait = (attempt + 1) * 30  # 30s, 60s backoff
                logger.warning(f"Rate limited, retrying in {wait}s...")
                time.sleep(wait)
                agent = _get_agent()  # fresh agent instance
                continue
            
            # If it's the last attempt or not a rate limit error, raise
            if attempt == max_retries - 1:
                logger.error(f"Failed after {max_retries} attempts")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to process question: {err_str}"
                )

    if result is None:
        raise HTTPException(status_code=500, detail="Failed to get response from agent")

    answer_text = result.get("output", "")
    logger.info(f"Generated answer: {answer_text[:100]}...")

    # Check if a chart file was produced
    chart_b64: str | None = None
    
    # First check for the UUID-based filename
    if os.path.isfile(chart_filename):
        logger.info(f"Found chart file: {chart_filename}")
        with open(chart_filename, "rb") as f:
            chart_b64 = base64.b64encode(f.read()).decode()
        os.remove(chart_filename)
        logger.info("Chart encoded and file cleaned up")
    # Then check for the generic name
    elif os.path.isfile("__chart__.png"):
        logger.info("Found generic chart file: __chart__.png")
        with open("__chart__.png", "rb") as f:
            chart_b64 = base64.b64encode(f.read()).decode()
        os.remove("__chart__.png")
        logger.info("Chart encoded and file cleaned up")
    # Fallback: check if matplotlib has any open figures
    elif plt.get_fignums():
        logger.info("Capturing chart from matplotlib buffer")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        buf.seek(0)
        chart_b64 = base64.b64encode(buf.read()).decode()
        plt.close("all")
        buf.close()
        logger.info("Chart captured from buffer")
    else:
        logger.info("No chart generated for this question")

    return ChatResponse(answer=answer_text, chart_base64=chart_b64)


@app.get("/dataset/info")
def dataset_info():
    """Return summary info about the Titanic dataset."""
    # Replace NaN with None so the response is JSON-serializable
    sample = df.head(5).where(df.head(5).notna(), None).to_dict(orient="records")
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample": sample,
    }
