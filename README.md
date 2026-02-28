# 🚢 Titanic Dataset Chat Agent

A friendly chatbot that analyzes the Titanic dataset. Ask questions in plain English and get text answers and visual insights.

## Tech Stack

- **Backend**: Python + FastAPI
- **Agent**: LangChain (pandas-dataframe agent with Google Gemini)
- **Frontend**: Streamlit
- **Data Visualization**: Matplotlib + Seaborn

## Quick Start (Recommended)

### Option 1: Using the Launcher Script

The easiest way to start both servers:

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
python start.py
```

This will:
- ✅ Check all requirements
- ✅ Verify your .env configuration
- ✅ Start both backend and frontend servers
- ✅ Open the app in your browser automatically

### Option 2: Manual Start

If you prefer to start servers manually:

**Terminal 1 - Backend:**
```bash
uvicorn backend:app --reload
```

**Terminal 2 - Frontend:**
```bash
streamlit run app.py
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Google API Key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_google_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

### 3. Verify Setup (Optional but Recommended)

Run the test script to ensure everything is configured correctly:

```bash
python test_setup.py
```

### 4. Start the FastAPI backend

```bash
uvicorn backend:app --reload
```

The API will be running at `http://127.0.0.1:8000`.

### 5. Start the Streamlit frontend

In a **separate terminal**:

```bash
streamlit run app.py
```

The UI will open at `http://localhost:8501`.

## Example Questions

- "What percentage of passengers were male on the Titanic?"
- "Show me a histogram of passenger ages"
- "What was the average ticket fare?"
- "How many passengers embarked from each port?"
- "What was the survival rate by passenger class?"
- "Show a bar chart of survival by gender"

## Troubleshooting

### Charts Not Displaying

If charts are not showing up in the Streamlit interface:

1. Check the backend logs for any errors during chart generation
2. Ensure matplotlib and seaborn are properly installed
3. The code has been updated to use `use_column_width=True` for better compatibility

### Rate Limit Errors (429)

The backend includes automatic retry logic with exponential backoff. If you encounter rate limits:
- Wait a few seconds between requests
- The system will automatically retry with 30s and 60s delays

### API Key Issues

If you see "GOOGLE_API_KEY not found":
- Ensure your `.env` file is in the project root directory
- Verify the API key is valid and active
- Restart the backend server after updating the `.env` file

## Project Structure

```
.
├── backend.py          # FastAPI backend with LangChain agent
├── app.py              # Streamlit frontend
├── titanic.csv         # Titanic dataset
├── requirements.txt    # Python dependencies
├── test_setup.py       # Setup verification script
├── .env                # API keys (create this file)
└── README.md           # This file
```

## API Endpoints

### POST /chat
Send a question and receive an answer with optional chart.

**Request**:
```json
{
  "question": "What percentage of passengers were male?"
}
```

**Response**:
```json
{
  "answer": "64.76% of passengers were male.",
  "chart_base64": null
}
```

### GET /dataset/info
Get information about the Titanic dataset including column names, data types, and sample rows.

### GET /health
Health check endpoint to verify the API is running.

## Features

✅ Natural language queries about the Titanic dataset  
✅ Automatic visualization generation (histograms, bar charts, etc.)  
✅ Powered by Google's Gemini AI  
✅ Clean Streamlit interface  
✅ Automatic retry logic for rate limits  
✅ Base64-encoded chart transmission  

## License

This project is for educational purposes.
