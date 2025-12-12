"""
AI Assistant Module
Handles AI interactions for each domain with data integration
"""

import pandas as pd
from openai import OpenAI
import streamlit as st

def get_ai_response(api_key: str, system_prompt: str, user_message: str, context_data: str = "") -> str:
    """
    Get AI response from OpenAI API
    
    Args:
        api_key: OpenAI API key
        system_prompt: System prompt defining the AI's role
        user_message: User's question
        context_data: Additional context data (e.g., dataframe summary)
    
    Returns:
        AI response string
    """
    try:
        client = OpenAI(api_key=api_key)
        
        # Combine system prompt with context data
        full_system_prompt = system_prompt
        if context_data:
            full_system_prompt += f"\n\nCurrent Data Context:\n{context_data}"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency, change to "gpt-4" for better results
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}\n\nPlease check your API key in .env file and ensure it's valid."

def prepare_data_context(df: pd.DataFrame, max_rows: int = 50) -> str:
    """
    Prepare a summary of the dataframe for AI context
    
    Args:
        df: DataFrame to summarize
        max_rows: Maximum number of rows to include in summary
    
    Returns:
        String summary of the data
    """
    if df is None or df.empty:
        return "No data available."
    
    summary = f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns\n\n"
    summary += f"Columns: {', '.join(df.columns.tolist())}\n\n"
    
    # Add statistical summary for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        summary += "Numeric Summary:\n"
        summary += df[numeric_cols].describe().to_string()
        summary += "\n\n"
    
    # Add sample data (first few rows)
    summary += f"Sample Data (first {min(max_rows, len(df))} rows):\n"
    summary += df.head(max_rows).to_string()
    
    return summary

def cybersecurity_ai_chat(api_key: str, df_incidents: pd.DataFrame):
    """Cybersecurity AI Assistant Chat Interface"""
    
    st.markdown("### 🔒 Cybersecurity Expert Assistant")
    st.info("Ask questions about security incidents, threats, vulnerabilities, and get actionable recommendations.")
    
    # System prompt for Cybersecurity
    system_prompt = """You are a cybersecurity expert. Analyze incidents, threats, and vulnerabilities. 
Provide technical guidance using MITRE ATT&CK, CVE references. Prioritize actionable recommendations.
Focus on:
- Incident analysis & triage
- Threat intelligence lookup
- Security best practices
- Remediation recommendations
Only answer questions related to cybersecurity. If asked about other topics, politely redirect to cybersecurity."""
    
    # Prepare data context
    if df_incidents is not None and not df_incidents.empty:
        data_context = prepare_data_context(df_incidents)
    else:
        data_context = "No incident data available."
    
    # Initialize chat history
    if "cyber_chat_history" not in st.session_state:
        st.session_state.cyber_chat_history = []
    
    # Display chat history
    for message in st.session_state.cyber_chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask about security incidents, threats, or vulnerabilities...")
    
    if user_input:
        # Add user message to history
        st.session_state.cyber_chat_history.append({"role": "user", "content": user_input})
        
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = get_ai_response(api_key, system_prompt, user_input, data_context)
                st.write(response)
                st.session_state.cyber_chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("Clear Chat History", key="clear_cyber_chat"):
        st.session_state.cyber_chat_history = []
        st.rerun()

def datascience_ai_chat(api_key: str, df_datasets: pd.DataFrame):
    """Data Science AI Assistant Chat Interface"""
    
    st.markdown("### 📊 Data Science Expert Assistant")
    st.info("Ask questions about datasets, data analysis, visualization, statistical methods, and machine learning.")
    
    # System prompt for Data Science
    system_prompt = """You are a data science expert. Help with data analysis, visualization, statistical methods, and machine learning. 
Explain concepts clearly and suggest appropriate techniques.
Focus on:
- Dataset analysis & insights
- Visualization recommendations
- Statistical methods guidance
- ML model suggestions
Only answer questions related to data science. If asked about other topics, politely redirect to data science."""
    
    # Prepare data context
    if df_datasets is not None and not df_datasets.empty:
        data_context = prepare_data_context(df_datasets)
    else:
        data_context = "No dataset catalog data available."
    
    # Initialize chat history
    if "ds_chat_history" not in st.session_state:
        st.session_state.ds_chat_history = []
    
    # Display chat history
    for message in st.session_state.ds_chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask about datasets, analysis, or visualization...")
    
    if user_input:
        # Add user message to history
        st.session_state.ds_chat_history.append({"role": "user", "content": user_input})
        
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = get_ai_response(api_key, system_prompt, user_input, data_context)
                st.write(response)
                st.session_state.ds_chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("Clear Chat History", key="clear_ds_chat"):
        st.session_state.ds_chat_history = []
        st.rerun()

def itoperations_ai_chat(api_key: str, df_tickets: pd.DataFrame):
    """IT Operations AI Assistant Chat Interface"""
    
    st.markdown("### ⚙️ IT Operations Expert Assistant")
    st.info("Ask questions about tickets, troubleshooting, system optimization, and infrastructure guidance.")
    
    # System prompt for IT Operations
    system_prompt = """You are an IT operations expert. Help troubleshoot issues, optimize systems, manage tickets, and provide infrastructure guidance. 
Focus on practical solutions.
Focus on:
- Ticket triage & prioritization
- Troubleshooting guidance
- System optimization tips
- Infrastructure best practices
Only answer questions related to IT operations. If asked about other topics, politely redirect to IT operations."""
    
    # Prepare data context
    if df_tickets is not None and not df_tickets.empty:
        data_context = prepare_data_context(df_tickets)
    else:
        data_context = "No ticket data available."
    
    # Initialize chat history
    if "it_chat_history" not in st.session_state:
        st.session_state.it_chat_history = []
    
    # Display chat history
    for message in st.session_state.it_chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask about tickets, troubleshooting, or system optimization...")
    
    if user_input:
        # Add user message to history
        st.session_state.it_chat_history.append({"role": "user", "content": user_input})
        
        # Show user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = get_ai_response(api_key, system_prompt, user_input, data_context)
                st.write(response)
                st.session_state.it_chat_history.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("Clear Chat History", key="clear_it_chat"):
        st.session_state.it_chat_history = []
        st.rerun()

