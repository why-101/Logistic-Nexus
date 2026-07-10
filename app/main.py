import sys
import os

# Force Python to look in the root directory for modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from agents.orchestrator import handle_request, execute_final_query
import pygwalker as pyg
import pandas as pd
import json
from datetime import datetime
from agents.orchestrator import handle_request, execute_final_query
import pygwalker as pyg  # <--- ADD THIS LINE
from agents.orchestrator import handle_request, execute_final_query

if "draft" not in st.session_state:
    st.session_state.draft = None
if "agent" not in st.session_state:
    st.session_state.agent = ""
    
# 💡 ADD THIS NEW LINE:
if "db_error" not in st.session_state:
    st.session_state.db_error = None

st.set_page_config(page_title="Autonomous Logistics Expeditor", layout="wide")

# Custom CSS for UI polish
st.markdown("""
    <style>
    .stTextArea textarea { color: #000000 !important; font-family: monospace; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 Autonomous Logistics Expeditor")
st.caption("Multi-Agent Intelligence Hub")

# ====================================================================
# 💡 CRITICAL FIX: Safe Session State Initialization (Top of File)
# ====================================================================
if "draft" not in st.session_state: 
    st.session_state.draft = None
if "current_agent" not in st.session_state: 
    st.session_state.current_agent = ""
if "history" not in st.session_state: 
    st.session_state.history = []

# --- Search Input ---
user_query = st.text_input("Consult the Specialist Hub:", placeholder="e.g., Show me profit margin per route")

if st.button("🚀 Consult Agents") and user_query:
    with st.status("Orchestrating specialized agents...") as status:
        draft, agent_name = handle_request(user_query)
        st.session_state.current_agent = agent_name
        st.session_state.draft = draft
        status.update(label=f"Analysis Complete by: {agent_name}", state="complete")

# ====================================================================
# --- Execution & Formatting Block ---
# ====================================================================
if st.session_state.draft is not None:
    st.divider()
    st.subheader(f"🛠️ Agent Review: {st.session_state.current_agent}")
    st.info(f"**Strategy:** {st.session_state.draft.get('explanation')}")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        target_col = st.text_input("Target Collection", value=st.session_state.draft.get("collection"))
        intent = st.session_state.draft.get("intent")
        st.write(f"Detected Intent: `{intent.upper()}`")
    with col2:
        # Allows for manual refinement before hitting the database
        q_code = st.text_area("Generated MongoDB Logic", value=json.dumps(st.session_state.draft.get("query"), indent=2), height=200)

    # ... inside if st.session_state.draft: ...
    
    if st.button("✅ Confirm & Execute"):
        with st.spinner("Processing..."):
            try:
                final_query = json.loads(q_code)
                results = execute_final_query(intent, target_col, final_query)
                st.session_state.last_results = results  
                st.session_state.db_error = None
            except Exception as e:
                st.session_state.last_results = None
                st.session_state.db_error = str(e)

    # ==========================================
    # 📊 RESULTS, 🔄 SELF-HEALING LOOP & CHARTS
    # ==========================================
    
    # 1. HANDLE ERRORS AND SHOW DATA TABLE
    if getattr(st.session_state, "db_error", None):
        st.error(f"⚠️ Database Execution Failed: {st.session_state.db_error}")
        error_payload = st.session_state.db_error
        
    elif getattr(st.session_state, "last_results", None):
        results = st.session_state.last_results
        if isinstance(results, dict) and "error" in results:
            st.error(f"⚠️ Query Error: {results['error']}")
            error_payload = results['error']
        else:
            # Show the raw data table first
            df = pd.DataFrame(results)
            st.success(f"Analysis Complete: Found {len(results)} records.")
            st.dataframe(df, width="stretch")
            
            # Define the error payload for the rework agent (in case of silent logic bugs)
            error_payload = "No database crash occurred, but the user is reporting a data logic issue (e.g., missing data, all zeros, or wrong calculations)."

    # 2. 🛠️ ALWAYS SHOW THE REWORK PANEL NEXT
    if getattr(st.session_state, "db_error", None) or getattr(st.session_state, "last_results", None):
        st.divider()
        with st.expander("🛠️ Auto-Fix / Refine Pipeline", expanded=False):
            st.info("Did the query crash? Or does the data look wrong? Tell the Agent what to fix.")
            
            user_suggestion = st.text_input("Feedback for the Agent (Optional)", placeholder="e.g., The MPG column is all 0s, make sure to unwind the fuel array before summing.")
            
            if st.button("🔄 Refine & Regenerate Pipeline"):
                with st.spinner("Analyzing feedback and rewriting..."):
                    from agents.rework_agent import run_rework_agent
                    
                    new_draft = run_rework_agent(
                        failed_query=q_code, 
                        error_message=error_payload, 
                        user_suggestion=user_suggestion
                    )
                    
                    st.session_state.draft = new_draft
                    st.session_state.last_results = None # Clear old results to reset view
                    st.session_state.db_error = None
                    st.rerun() # Reload UI to show new draft

    # 3. 📈 THE VISUALIZATION AGENT (AT THE VERY BOTTOM)
    if getattr(st.session_state, "last_results", None):
        results = st.session_state.last_results
        # Only show the chart builder if we actually have valid data (no errors)
        if not (isinstance(results, dict) and "error" in results):
            st.divider()
            with st.expander("📊 Open Interactive Chart Builder", expanded=True):
                st.info("Drag and drop columns from the left panel into the X and Y axes below to build your chart.")
                import pygwalker as pyg
                # We recreate the dataframe here just to ensure PyGWalker has fresh data
                df_chart = pd.DataFrame(results)
                # Your existing code where you create the DataFrame
                df = pd.DataFrame(results)

                # --- ADD THESE TWO LINES ---
                # If the MongoDB '_id' column exists, convert it to a standard string
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
    
                # Now pass it to PyGWalker / Streamlit as normal
                pyg.walk(df)
                pyg_html = pyg.to_html(df_chart)
                st.components.v1.html(pyg_html, height=800, scrolling=True)
