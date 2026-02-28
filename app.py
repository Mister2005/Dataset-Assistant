import streamlit as st
import requests
import base64
import time
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Titanic Chat Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend configuration
BACKEND_URL = "http://localhost:8000"
MAX_RETRIES = 3
RETRY_DELAY = 2

# Custom CSS for professional dark theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(59, 130, 246, 0.2);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Main content text */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Chat input styling */
    .stChatInput {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    
    .stChatInput input {
        background: transparent !important;
        color: #e2e8f0 !important;
        border: none !important;
    }
    
    .stChatInput input::placeholder {
        color: #94a3b8 !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
        margin: 10px 0;
    }
    
    .stChatMessage p {
        color: #e2e8f0 !important;
    }
    
    /* User message */
    [data-testid="stChatMessageContent"] {
        background: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 6px rgba(59, 130, 246, 0.2) !important;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        box-shadow: 0 6px 12px rgba(59, 130, 246, 0.3) !important;
        transform: translateY(-2px);
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
        color: #e2e8f0 !important;
    }
    
    /* Success box */
    .stSuccess {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(22, 163, 74, 0.1) 100%) !important;
        border: 1px solid rgba(34, 197, 94, 0.3) !important;
    }
    
    /* Error box */
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
    
    /* Info box */
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%) !important;
        border: 1px solid rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #3b82f6 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        border-top: none !important;
        color: #e2e8f0 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #2563eb 0%, #1d4ed8 100%);
    }
    
    /* Status indicator */
    .status-box {
        padding: 12px 20px;
        border-radius: 10px;
        margin: 10px 0;
        display: inline-block;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    .status-connected {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(22, 163, 74, 0.2) 100%);
        border: 1px solid rgba(34, 197, 94, 0.4);
        color: #86efac;
    }
    
    .status-disconnected {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        color: #fca5a5;
    }
    
    /* Example questions */
    .example-question {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #e2e8f0;
        backdrop-filter: blur(10px);
    }
    
    .example-question:hover {
        background: rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateX(5px);
    }
    
    /* Download button */
    .stDownloadButton button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        transform: translateY(-2px);
    }
    
    /* Divider */
    hr {
        border-color: rgba(59, 130, 246, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def check_backend_health():
    """Check if backend is healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_question_with_retry(question):
    """Send question to backend with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"question": question},
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            else:
                raise e

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "backend_status" not in st.session_state:
    st.session_state.backend_status = check_backend_health()

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Sidebar
with st.sidebar:
    st.title("🚢 Titanic Chat Agent")
    st.markdown("---")
    
    # Backend status
    st.subheader("Connection Status")
    is_connected = check_backend_health()
    st.session_state.backend_status = is_connected
    
    if is_connected:
        st.markdown(
            '<div class="status-box status-connected">● Connected</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-box status-disconnected">● Disconnected</div>',
            unsafe_allow_html=True
        )
        st.error("Backend is not responding. Please start the backend server.")
    
    st.markdown("---")
    
    # Example questions
    st.subheader("💡 Example Questions")
    
    # Data Exploration
    with st.expander("📊 Data Exploration", expanded=True):
        data_questions = [
            "How many passengers survived?",
            "What was the survival rate by class?",
            "What was the average fare by class?",
            "Show me passenger demographics"
        ]
        for question in data_questions:
            if st.button(question, key=f"data_{question}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()
    
    # Visualizations
    with st.expander("📈 Visualizations"):
        viz_questions = [
            "Show me the age distribution",
            "Create a bar chart of survivors by gender",
            "Show survival rate by embarkation port",
            "Create a pie chart of passenger classes"
        ]
        for question in viz_questions:
            if st.button(question, key=f"viz_{question}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()
    
    # Statistical Analysis
    with st.expander("🔢 Statistical Analysis"):
        stats_questions = [
            "What is the correlation between age and survival?",
            "Compare survival rates across different classes",
            "Show statistics for fare prices"
        ]
        for question in stats_questions:
            if st.button(question, key=f"stats_{question}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()
    
    st.markdown("---")
    
    # Dataset info
    with st.expander("📊 Dataset Information"):
        try:
            info = requests.get(f"{BACKEND_URL}/dataset/info", timeout=5).json()
            st.metric("Total Rows", info["rows"])
            st.metric("Total Columns", len(info["columns"]))
            st.write("**Columns:**")
            st.write(", ".join(info["columns"]))
        except:
            st.write("Unable to fetch dataset info")
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("🚢 Titanic Dataset Chat Agent")
st.markdown("Ask questions about the Titanic dataset and get AI-powered insights with visualizations.")

# Process pending question from example buttons
if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None  # Clear it
    
    if st.session_state.backend_status:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get assistant response
        try:
            result = send_question_with_retry(prompt)
            answer = result.get("answer", "No response")
            chart_b64 = result.get("chart_base64")
            
            # Save assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "chart": chart_b64
            })
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })
    else:
        st.error("⚠️ Backend is not connected. Please start the backend server first.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display chart if available
        if "chart" in message and message["chart"]:
            # Decode base64 string to bytes for display
            img_bytes = base64.b64decode(message["chart"])
            st.image(img_bytes, use_column_width=True)
            
            # Add download button for chart
            st.download_button(
                label="📥 Download Chart",
                data=img_bytes,
                file_name="titanic_chart.png",
                mime="image/png"
            )

# Chat input
if prompt := st.chat_input("Ask a question about the Titanic dataset..."):
    if not st.session_state.backend_status:
        st.error("⚠️ Backend is not connected. Please start the backend server first.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = send_question_with_retry(prompt)
                    answer = result.get("answer", "No response")
                    chart_b64 = result.get("chart_base64")
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Display chart if available
                    if chart_b64:
                        # Decode base64 to bytes for display
                        img_bytes = base64.b64decode(chart_b64)
                        st.image(img_bytes, use_column_width=True)
                        
                        # Add download button
                        st.download_button(
                            label="📥 Download Chart",
                            data=img_bytes,
                            file_name="titanic_chart.png",
                            mime="image/png"
                        )
                    
                    # Save assistant message
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "chart": chart_b64
                    })
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b;'>Powered by Google Gemini & LangChain</p>",
    unsafe_allow_html=True
)
