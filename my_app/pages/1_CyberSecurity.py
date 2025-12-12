import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_app.utilities.data_generators import SecurityIncidentGenerator
from my_app.repositories.incident_repository import SecurityIncidentRepository
from my_app.services.incident_service import SecurityIncidentService
from my_app.AI.ai_assistant import cybersecurity_ai_chat
from my_app.models.incident import SecurityIncident
from app.data.incidents import insert_incident, update_incident_status, delete_incident
from app.data.db import connect_database
from datetime import datetime

# Get API key from environment variable
CYBERSECURITY_API_KEY = os.getenv("CYBERSECURITY_API_KEY", "")

st.set_page_config(page_title="Cyber Security", page_icon="🔒", layout="wide")

# Set light pink background for this page
st.markdown("""
    <style>
    .stApp {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    .main .block-container {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    body {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFDDF4 !important;
        background: #FFDDF4 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background-color: #FFDDF4 !important;
        background: #FFDDF4 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #FFDDF4 !important;
        background: #FFDDF4 !important;
    }
    header[data-testid="stHeader"] {
        background-color: #FFE5F1 !important;
        background: #FFE5F1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Ensure state keys exist (in case user opens this page first)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""

# ========== SIDEBAR ==========
with st.sidebar:
    # Navigation Categories
    st.markdown("### Navigation")
    nav_options = {
        "app": ("🏠 Home", "Home.py"),
        "cybersecurity": ("🔒 Cyber Security", "pages/1_CyberSecurity.py"),
        "datascience": ("📊 Data Science", "pages/2_DataScience.py"),
        "it operations": ("⚙️ IT Operations", "pages/3_IToperations.py")
    }
    
    for key, (label, page) in nav_options.items():
        if key == "cybersecurity":
            st.info(f"**{label}** (Current Page)")
        else:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.switch_page(page)
    
    st.markdown("---")
    
    # Current Section Display
    with st.container():
        st.markdown("### 🔒 Cybersecurity")
        st.markdown("**Incident Response Center**")
    
    st.markdown("---")
    
    # User Information Card
    username = st.session_state.username if st.session_state.username else "Guest"
    user_role = st.session_state.user_role if st.session_state.user_role else "No Role"
    with st.container():
        st.markdown("**Logged in as**")
        st.markdown(f"👤 **{username}**")
        st.markdown(f"💼 {user_role}")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### Quick Actions")
    
    # Refresh Data Button
    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_data"):
        st.rerun()
    
    # Logout Button
    if st.button("🚪 Logout", use_container_width=True, key="logout_sidebar"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.info("You have been logged out.")
        st.switch_page("Home.py")

# Guard: if not logged in, send user back
if not st.session_state.logged_in:
    st.error("You must be logged in to view the dashboard.")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# Guard: check if user has the correct role
if st.session_state.user_role != "Cyber Security":
    st.error(f"⚠️ Access Denied: This page is only accessible to Cyber Security users. Your role is: {st.session_state.user_role}")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# ========== HEADER ==========
st.title("🔒 Cybersecurity Dashboard")
st.success(f"Welcome, **{st.session_state.username}**! Monitoring security incidents in real-time.")

# ========== TABS ==========
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 AI Assistant", "✏️ Manage Incidents", "🔍 Filter & Search"])

# Generate data using OOP structure
# Try to load from database first, fallback to generated data if empty
repository = SecurityIncidentRepository(use_database=True)
if repository.count() == 0:
    # No data in database, generate sample data
    generator = SecurityIncidentGenerator(seed=42)
    incidents = generator.generate(days=30)
    repository = SecurityIncidentRepository(incidents, use_database=False)
service = SecurityIncidentService(repository)
df_incidents = service.to_dataframe()

# ========== DASHBOARD TAB ==========
with tab1:
    # ========== PROBLEM STATEMENT ==========
    st.markdown("---")
    st.markdown("### 🚨 Core Problem: Incident Response Bottleneck")
    st.warning("**Critical Issue**: The security team is facing a recent, targeted surge in Phishing incidents, leading to a growing backlog of high-severity, unresolved cases.")

    # ========== KEY METRICS ==========
st.markdown("---")
st.markdown("### 📊 Key Metrics")

# Get metrics from service
metrics = service.get_metrics()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Incidents (30 days)", metrics["total_incidents"], delta=None)
with col2:
    st.metric("High-Severity Unresolved", metrics["unresolved_high"], delta=f"+{metrics['unresolved_high']}", delta_color="inverse")
with col3:
    st.metric("Phishing Incidents", metrics["phishing_total"], delta=f"+{metrics['phishing_total'] - 60}", delta_color="inverse")
with col4:
    st.metric("Phishing Unresolved", metrics["phishing_unresolved"], delta=f"{metrics['phishing_unresolved']}", delta_color="inverse")

# ========== THREAT TREND ANALYSIS ==========
st.markdown("---")
st.markdown("### 📈 High-Value Insight: Threat Trend Analysis")

# Phishing spike visualization
st.markdown("#### 🔍 Specific Threat Trend: Phishing Spike")

# Prepare data for line chart - pivot by date and threat category
daily_incidents = df_incidents.groupby(["Date", "Threat Category"]).size().reset_index(name="Count")
daily_pivot = daily_incidents.pivot(index="Date", columns="Threat Category", values="Count").fillna(0)
daily_pivot.index = pd.to_datetime(daily_pivot.index)

st.line_chart(daily_pivot, height=400)

# Highlight the surge using service
surge_analysis = service.get_phishing_surge_analysis(days=7)
st.info(f"**📊 Phishing Surge Analysis**: In the last 7 days, there were **{surge_analysis['recent_count']} phishing incidents**, representing a **{surge_analysis['surge_percentage']:.1f}% increase** compared to the previous week.")

# Additional breakdown by category
st.markdown("#### Total Incidents by Threat Category (Last 30 Days)")
category_totals = df_incidents.groupby("Threat Category").size().sort_values(ascending=False)
category_df = pd.DataFrame({
    "Threat Category": category_totals.index,
    "Count": category_totals.values
})
st.bar_chart(category_df.set_index("Threat Category"), height=300)

# ========== RESPONSE BOTTLENECK ANALYSIS ==========
st.markdown("---")
st.markdown("### ⏱️ Response Bottleneck Analysis")

# Get bottleneck analysis from service
bottleneck = service.get_resolution_bottleneck()
if bottleneck:
    # Create DataFrame from service data for visualization
    all_averages = bottleneck["all_averages"]
    resolution_df = pd.DataFrame({
        "Threat Category": list(all_averages.keys()),
        "Avg Resolution Time (hours)": list(all_averages.values())
    }).sort_values("Avg Resolution Time (hours)", ascending=False)
    
    # Get resolved incidents for additional stats
    resolved_incidents = df_incidents[df_incidents["Status"] == "Resolved"].copy()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Average Resolution Time by Threat Category")
        resolution_chart_df = resolution_df.set_index("Threat Category")[["Avg Resolution Time (hours)"]]
        st.bar_chart(resolution_chart_df, height=400)
        st.dataframe(resolution_df, use_container_width=True)
    
    with col2:
        st.markdown("#### Resolution Time Statistics")
        if len(resolved_incidents) > 0:
            resolution_stats = resolved_incidents.groupby("Threat Category")["Resolution Time (hours)"].agg([
                'mean', 'min', 'max', 'count'
            ]).round(1)
            resolution_stats.columns = ["Mean (hrs)", "Min (hrs)", "Max (hrs)", "Count"]
            resolution_stats = resolution_stats.sort_values("Mean (hrs)", ascending=False)
            st.dataframe(resolution_stats, use_container_width=True)
            
            st.markdown("#### Resolution Time Range")
            for category in resolution_stats.index:
                category_data = resolved_incidents[resolved_incidents["Threat Category"] == category]["Resolution Time (hours)"]
                mean_time = category_data.mean()
                st.write(f"**{category}**: {category_data.min():.0f} - {category_data.max():.0f} hrs (avg: {mean_time:.1f} hrs)")
    
    # Key insight
    st.error(f"**🚨 Critical Finding**: **{bottleneck['category']}** has the longest average resolution time at **{bottleneck['avg_resolution_time']:.1f} hours**, indicating a significant response bottleneck for this threat category.")
else:
    st.warning("No resolved incidents available for resolution time analysis.")

# ========== BACKLOG ANALYSIS ==========
st.markdown("---")
st.markdown("### 📋 Incident Backlog Analysis")

# Get backlog summary from service
backlog_summary = service.get_backlog_summary()
unresolved = df_incidents[df_incidents["Status"] == "Unresolved"].copy()
if backlog_summary["total_unresolved"] > 0:
    backlog_by_category = unresolved.groupby(["Threat Category", "Severity"]).size().reset_index(name="Count")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Unresolved Incidents by Category")
        # Create a stacked bar chart by pivoting the data
        backlog_pivot = backlog_by_category.pivot(index="Threat Category", columns="Severity", values="Count").fillna(0)
        backlog_pivot = backlog_pivot.reindex(columns=["High", "Medium", "Low"], fill_value=0)
        st.bar_chart(backlog_pivot, height=400)
        
        # Show detailed breakdown
        st.dataframe(backlog_by_category.pivot(index="Threat Category", columns="Severity", values="Count").fillna(0), use_container_width=True)
    
    with col2:
        st.markdown("#### High-Severity Unresolved Cases")
        high_severity_unresolved = unresolved[unresolved["Severity"] == "High"]
        high_by_category = high_severity_unresolved.groupby("Threat Category").size().reset_index(name="Count")
        high_by_category = high_by_category.sort_values("Count", ascending=False)
        
        # Use bar chart instead of pie chart
        high_chart_df = high_by_category.set_index("Threat Category")[["Count"]]
        st.bar_chart(high_chart_df, height=300)
        
        # Show percentage breakdown
        st.markdown("**Distribution:**")
        total_high = high_by_category["Count"].sum()
        for _, row in high_by_category.iterrows():
            percentage = (row["Count"] / total_high * 100) if total_high > 0 else 0
            st.write(f"• **{row['Threat Category']}**: {row['Count']} ({percentage:.1f}%)")
    
    # Summary using service data
    st.warning(f"**⚠️ Backlog Summary**: There are currently **{backlog_summary['total_unresolved']} unresolved incidents**, with **{backlog_summary['high_severity_unresolved']} high-severity cases** requiring immediate attention.")
    
    # Show top categories in backlog
    by_category = backlog_summary["by_category"]
    sorted_categories = sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:3]
    st.info(f"**Top 3 Categories in Backlog**: {', '.join([f'{cat} ({count})' for cat, count in sorted_categories])}")
else:
    st.success("✅ No unresolved incidents in the backlog!")

# ========== DETAILED DATA TABLE ==========
st.markdown("---")
with st.expander("📄 View Detailed Incident Data"):
    st.dataframe(
        df_incidents.sort_values("Date", ascending=False),
        use_container_width=True,
        height=400
    )

# ========== RECOMMENDATIONS ==========
st.markdown("---")
st.markdown("### 💡 Recommendations")
st.markdown("""
1. **Immediate Action**: Allocate additional resources to handle the Phishing incident surge
2. **Process Optimization**: Review and streamline the response process for the category with longest resolution time
3. **Priority Management**: Focus on resolving high-severity unresolved cases first
4. **Capacity Planning**: Consider scaling the security team to handle increased incident volume
5. **Automation**: Implement automated response workflows for common threat patterns
""")

# ========== AI ASSISTANT TAB ==========
with tab2:
    st.markdown("---")
    if CYBERSECURITY_API_KEY and CYBERSECURITY_API_KEY != "":
        cybersecurity_ai_chat(CYBERSECURITY_API_KEY, df_incidents)
    else:
        st.error("⚠️ API Key Not Configured")
        st.warning("Please add your OpenAI API key to `.env` file in the project root.")
        st.info("""
        **Instructions:**
        1. Copy `.env.example` to `.env` in the project root directory
        2. Open `.env` file and replace `your-cybersecurity-api-key-here` with your actual API key
        3. Get your API key from: https://platform.openai.com/api-keys
        4. Restart the application
        5. **Important**: The `.env` file is already in `.gitignore` and will not be committed to GitHub
        """)

# ========== MANAGE INCIDENTS TAB ==========
with tab3:
    st.markdown("---")
    st.markdown("### ✏️ Manage Incidents")
    
    # Sub-tabs for different operations
    manage_tab1, manage_tab2, manage_tab3 = st.tabs(["➕ Add New", "✏️ Update", "🗑️ Delete"])
    
    with manage_tab1:
        st.markdown("#### Add New Incident")
        with st.form("add_incident_form"):
            col1, col2 = st.columns(2)
            with col1:
                incident_date = st.date_input("Date", value=datetime.now().date())
                threat_category = st.selectbox("Threat Category", 
                    ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Data Breach", "Other"])
                severity = st.selectbox("Severity", ["High", "Medium", "Low"])
            with col2:
                status = st.selectbox("Status", ["Unresolved", "In Progress", "Resolved"])
                description = st.text_area("Description", height=100)
                reported_by = st.text_input("Reported By", value=st.session_state.username)
            
            resolution_time = None
            if status == "Resolved":
                resolution_time = st.number_input("Resolution Time (hours)", min_value=0.0, value=0.0, step=0.1)
            
            submitted = st.form_submit_button("Add Incident", use_container_width=True)
            
            if submitted:
                try:
                    # Create incident object
                    incident = SecurityIncident(
                        date=datetime.combine(incident_date, datetime.min.time()),
                        threat_category=threat_category,
                        severity=severity,
                        status=status,
                        resolution_time_hours=resolution_time if status == "Resolved" else None
                    )
                    
                    # Insert into database
                    incident_id = insert_incident(
                        str(incident_date),
                        threat_category,
                        severity,
                        status,
                        description,
                        reported_by
                    )
                    
                    # Add to repository
                    repository.add(incident)
                    
                    st.success(f"✅ Incident #{incident_id} added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding incident: {str(e)}")
    
    with manage_tab2:
        st.markdown("#### Update Incident")
        
        # Get all incidents for selection
        all_incidents = repository.get_all()
        if len(all_incidents) > 0:
            df_all = repository.to_dataframe()
            df_all['Index'] = range(len(df_all))
            
            selected_idx = st.selectbox("Select Incident to Update", 
                options=range(len(df_all)),
                format_func=lambda x: f"{df_all.iloc[x]['Date']} - {df_all.iloc[x]['Threat Category']} ({df_all.iloc[x]['Status']})")
            
            selected_incident = all_incidents[selected_idx]
            
            with st.form("update_incident_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_status = st.selectbox("Status", 
                        ["Unresolved", "In Progress", "Resolved"],
                        index=["Unresolved", "In Progress", "Resolved"].index(selected_incident.status))
                    new_severity = st.selectbox("Severity",
                        ["High", "Medium", "Low"],
                        index=["High", "Medium", "Low"].index(selected_incident.severity))
                with col2:
                    new_category = st.text_input("Threat Category", value=selected_incident.threat_category)
                    new_resolution_time = st.number_input("Resolution Time (hours)", 
                        min_value=0.0, 
                        value=float(selected_incident.resolution_time_hours) if selected_incident.resolution_time_hours else 0.0,
                        step=0.1)
                
                submitted = st.form_submit_button("Update Incident", use_container_width=True)
                
                if submitted:
                    try:
                        # Update in database (we need to get the ID from dataframe)
                        conn = connect_database()
                        df_db = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
                        conn.close()
                        
                        # Find matching incident in DB (by date and category)
                        matching = df_db[
                            (df_db['date'] == selected_incident.date.strftime('%Y-%m-%d')) &
                            (df_db['incident_type'] == selected_incident.threat_category)
                        ]
                        
                        if len(matching) > 0:
                            incident_id = matching.iloc[0]['id']
                            conn = connect_database()
                            update_incident_status(conn, incident_id, new_status)
                            conn.close()
                            
                            # Update in repository
                            selected_incident.status = new_status
                            selected_incident.severity = new_severity
                            selected_incident.threat_category = new_category
                            if new_status == "Resolved":
                                selected_incident.resolution_time_hours = new_resolution_time
                            
                            st.success("✅ Incident updated successfully!")
                            st.rerun()
                        else:
                            st.warning("⚠️ Could not find incident in database to update.")
                    except Exception as e:
                        st.error(f"❌ Error updating incident: {str(e)}")
        else:
            st.info("No incidents available to update.")
    
    with manage_tab3:
        st.markdown("#### Delete Incident")
        
        all_incidents = repository.get_all()
        if len(all_incidents) > 0:
            df_all = repository.to_dataframe()
            df_all['Index'] = range(len(df_all))
            
            selected_idx = st.selectbox("Select Incident to Delete", 
                options=range(len(df_all)),
                format_func=lambda x: f"{df_all.iloc[x]['Date']} - {df_all.iloc[x]['Threat Category']} ({df_all.iloc[x]['Status']})")
            
            selected_incident = all_incidents[selected_idx]
            
            st.warning(f"⚠️ You are about to delete: **{selected_incident.threat_category}** incident from **{selected_incident.date.strftime('%Y-%m-%d')}**")
            
            if st.button("🗑️ Delete Incident", use_container_width=True, type="primary"):
                try:
                    # Delete from database
                    conn = connect_database()
                    df_db = pd.read_sql_query("SELECT * FROM cyber_incidents", conn)
                    conn.close()
                    
                    # Find matching incident in DB
                    matching = df_db[
                        (df_db['date'] == selected_incident.date.strftime('%Y-%m-%d')) &
                        (df_db['incident_type'] == selected_incident.threat_category)
                    ]
                    
                    if len(matching) > 0:
                        incident_id = matching.iloc[0]['id']
                        conn = connect_database()
                        delete_incident(conn, incident_id)
                        conn.close()
                        
                        # Remove from repository
                        repository._incidents.remove(selected_incident)
                        
                        st.success("✅ Incident deleted successfully!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Could not find incident in database to delete.")
                except Exception as e:
                    st.error(f"❌ Error deleting incident: {str(e)}")
        else:
            st.info("No incidents available to delete.")

# ========== FILTER & SEARCH TAB ==========
with tab4:
    st.markdown("---")
    st.markdown("### 🔍 Filter & Search Incidents")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.multiselect("Filter by Status", 
            ["Unresolved", "In Progress", "Resolved"],
            default=[])
        filter_severity = st.multiselect("Filter by Severity",
            ["High", "Medium", "Low"],
            default=[])
    
    with col2:
        filter_category = st.multiselect("Filter by Threat Category",
            df_incidents["Threat Category"].unique().tolist() if not df_incidents.empty else [],
            default=[])
        search_text = st.text_input("🔍 Search (Description/Category)", "")
    
    with col3:
        date_range = st.date_input("Date Range",
            value=(datetime.now().date() - pd.Timedelta(days=30), datetime.now().date()),
            max_value=datetime.now().date())
    
    # Apply filters
    filtered_df = df_incidents.copy()
    
    if filter_status:
        filtered_df = filtered_df[filtered_df["Status"].isin(filter_status)]
    if filter_severity:
        filtered_df = filtered_df[filtered_df["Severity"].isin(filter_severity)]
    if filter_category:
        filtered_df = filtered_df[filtered_df["Threat Category"].isin(filter_category)]
    if search_text:
        mask = (
            filtered_df["Threat Category"].str.contains(search_text, case=False, na=False) |
            (filtered_df.get("Description", pd.Series([""] * len(filtered_df))).astype(str).str.contains(search_text, case=False, na=False))
        )
        filtered_df = filtered_df[mask]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        if pd.api.types.is_datetime64_any_dtype(filtered_df["Date"]):
            filtered_df = filtered_df[
                (filtered_df["Date"].dt.date >= date_range[0]) &
                (filtered_df["Date"].dt.date <= date_range[1])
            ]
    
    st.markdown(f"**Found {len(filtered_df)} incident(s)**")
    
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Export option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Results (CSV)",
            data=csv,
            file_name=f"incidents_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No incidents match the selected filters.")

# ========== LOGOUT ==========
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")
