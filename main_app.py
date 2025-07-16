import streamlit as st
from backend.agents.summary_agent import SummaryAgent
from backend.agents.qa_agent import QAAgent
from backend.agents.task_agent import TaskAgent
from config import client  # your OpenAI client setup
from backend.task_executor import route_to_agent  # NEW: cleaner routing
from backend.agent_router import route_query
from dotenv import load_dotenv
import os

load_dotenv()

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔒 Mini Scrum Master Login")
        password = st.text_input("Enter password", type="password")
        if password == st.secrets["app_password"]:
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        elif password:
            st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

# --- Streamlit setup ---
st.set_page_config(page_title="Mini Scrum Master", layout="wide")
st.title("🤖 Mini Scrum Master")

# --- Transcript Upload ---
uploaded_file = st.file_uploader("Upload Webex Transcript (.txt)", type=["txt"])
transcript = ""

if uploaded_file:
    transcript = uploaded_file.read().decode("utf-8")
    st.text_area("📄 Transcript Preview", transcript[:2000], height=300)

# --- User Query Input ---
user_query = st.text_input("💬 Ask a question or give an instruction")

# --- Submit Query ---
if st.button("Submit Query") and user_query and transcript:
    with st.spinner("🕒 Getting response from AI... Please wait."):
        response = route_query(user_query, transcript)
    st.session_state["response"] = response

# --- Load Previous Response if Present ---
response = st.session_state.get("response", {})

# --- Handle Task Agent Flow ---
selected_tasks = []

if response.get("tasks"):
    st.markdown(response["message"])
    for idx, task in enumerate(response["tasks"]):
        label = task.get("label", f"Task {idx+1}")
        agent = task.get("agent", "none")
        if agent == "none":
            continue  # skip non-executable tasks
        checkbox_key = f"select_task_{idx}"
        assignee = task.get("params", {}).get("assignee", "Unassigned")
        if st.checkbox(f"✅ {label} (Agent: `{agent}` | Assignee: `{assignee}`)", key=checkbox_key):
            selected_tasks.append(task)

    if st.button("Run Selected Tasks") and selected_tasks:
        st.markdown("## 🚀 Executing Tasks...")
        for task in selected_tasks:
            try:
                result = route_to_agent(task["agent"], task["params"])
                st.success(f"✅ {task['label']} result:\n{result}")
            except Exception as e:
                st.error(f"❌ Failed to run '{task['label']}': {str(e)}")
    
    non_routable_tasks = [t for t in response.get("tasks", []) if t.get("agent") == "none"]
    if non_routable_tasks:
        st.markdown("### ⚠️ Tasks without automation support")
        for t in non_routable_tasks:
            label = t.get("label", "Unnamed Task")
            assignee = t.get("params", {}).get("assignee", "Unassigned")
            st.markdown(f"- **{label}** — Assignee: `{assignee}`")

# --- Handle SummaryAgent / QAAgent Flow ---
elif response.get("message"):
    st.markdown("### 💡 Response")
    st.markdown(response["message"])

elif response:
    st.warning("🤔 No valid response from LLM. Try again with a different query.")

if st.sidebar.button("Logout"):
    st.session_state["authenticated"] = False
    st.experimental_rerun()