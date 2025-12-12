import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_app.utilities.data_generators import ITTicketGenerator
from my_app.repositories.it_ticket_repository import ITTicketRepository
from my_app.services.it_ticket_service import ITTicketService
from my_app.AI.ai_assistant import itoperations_ai_chat
from my_app.models.it_ticket import ITTicket
from app.data.db import connect_database
from datetime import datetime, date, timedelta

# Get API key from environment variable
IT_OPERATIONS_API_KEY = os.getenv("IT_OPERATIONS_API_KEY", "")

st.set_page_config(page_title="IT Operations", page_icon="⚙️", layout="wide")

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
        if key == "it operations":
            st.info(f"**{label}** (Current Page)")
        else:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.switch_page(page)
    
    st.markdown("---")
    
    # Current Section Display
    with st.container():
        st.markdown("### ⚙️ IT Operations")
        st.markdown("**Service Desk Center**")
    
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
if st.session_state.user_role != "IT Operations":
    st.error(f"⚠️ Access Denied: This page is only accessible to IT Operations users. Your role is: {st.session_state.user_role}")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# ========== HEADER ==========
st.title("⚙️ IT Operations Dashboard")
st.success(f"Welcome, **{st.session_state.username}**! Service Desk Performance Analytics.")

# ========== TABS ==========
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 AI Assistant", "✏️ Manage Tickets", "🔍 Filter & Search"])

# Generate data using OOP structure
# Try to load from database first, fallback to generated data if empty
repository = ITTicketRepository(use_database=True)
if repository.count() == 0:
    # No data in database, generate sample data
    generator = ITTicketGenerator(seed=42)
    tickets = generator.generate(num_tickets=150)
    repository = ITTicketRepository(tickets, use_database=False)
service = ITTicketService(repository)
df_tickets = service.to_dataframe()

# ========== DASHBOARD TAB ==========
with tab1:
    # ========== PROBLEM STATEMENT ==========
    st.markdown("---")
    st.markdown("### 🚨 Core Problem: Service Desk Performance")
    st.warning("**Critical Issue**: The IT support team is struggling with slow resolution times, and the manager suspects a staff performance anomaly and process inefficiencies.")

    # ========== KEY METRICS ==========
    st.markdown("---")
    st.markdown("### 📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    # Get metrics from service
    metrics = service.get_metrics()

    with col1:
        st.metric("Total Tickets", metrics["total_tickets"], delta=None)
    with col2:
        st.metric("Open Tickets", metrics["open_tickets"], delta=f"{metrics['open_tickets']}", delta_color="inverse")
    with col3:
        st.metric("Avg Resolution Time", f"{metrics['avg_resolution_time']:.1f} hrs", delta=f"{metrics['avg_resolution_time']:.1f} hrs", delta_color="inverse")
    with col4:
        st.metric("Waiting for User", metrics["tickets_waiting_user"], delta=f"{metrics['tickets_waiting_user']}", delta_color="inverse")

# ========== STAFF PERFORMANCE ANALYSIS ==========
st.markdown("---")
st.markdown("### 👥 High-Value Insight: Staff Performance Analysis")

# Calculate average resolution time by staff
resolved_tickets = df_tickets[df_tickets["Status"] == "Resolved"].copy()
if len(resolved_tickets) > 0:
    staff_performance = resolved_tickets.groupby("Assigned Staff").agg({
        "Total Resolution Time (hours)": ["mean", "median", "count"],
        "Ticket ID": "count"
    }).round(2)
    staff_performance.columns = ["Avg Resolution Time (hrs)", "Median Resolution Time (hrs)", "Ticket Count", "Total Tickets"]
    staff_performance = staff_performance.sort_values("Avg Resolution Time (hrs)", ascending=False)
    
    # Identify the bottleneck staff member
    slowest_staff = staff_performance.iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Average Resolution Time by Staff Member")
        staff_chart_df = staff_performance[["Avg Resolution Time (hrs)"]]
        st.bar_chart(staff_chart_df, height=400)
        
        # Show detailed statistics
        st.dataframe(staff_performance, use_container_width=True)
    
    with col2:
        st.markdown("#### Staff Performance Statistics")
        for staff in staff_performance.index:
            staff_data = resolved_tickets[resolved_tickets["Assigned Staff"] == staff]
            avg_time = staff_data["Total Resolution Time (hours)"].mean()
            median_time = staff_data["Total Resolution Time (hours)"].median()
            count = len(staff_data)
            st.write(f"**{staff}**: Avg: {avg_time:.1f} hrs, Median: {median_time:.1f} hrs, Tickets: {count}")
        
        # Show distribution
        st.markdown("#### Resolution Time Distribution by Staff")
        for staff in staff_performance.index[:3]:  # Top 3
            staff_times = resolved_tickets[resolved_tickets["Assigned Staff"] == staff]["Total Resolution Time (hours)"]
            st.write(f"**{staff}**: {staff_times.min():.1f} - {staff_times.max():.1f} hrs (avg: {staff_times.mean():.1f} hrs)")
    
    # Key insight
    st.error(f"**🚨 Critical Finding**: **{slowest_staff.name}** has the longest average resolution time at **{slowest_staff['Avg Resolution Time (hrs)']:.1f} hours**, indicating a potential staff performance anomaly.")
    
    # Compare to team average
    team_avg = resolved_tickets["Total Resolution Time (hours)"].mean()
    performance_delta = slowest_staff['Avg Resolution Time (hrs)'] - team_avg
    performance_pct = (performance_delta / team_avg) * 100
    st.warning(f"**Performance Gap**: {slowest_staff.name} is **{performance_pct:.1f}% slower** than the team average ({team_avg:.1f} hrs).")
else:
    st.warning("No resolved tickets available for staff performance analysis.")

# ========== PROCESS STAGE BOTTLENECK ANALYSIS ==========
st.markdown("---")
st.markdown("### ⏱️ High-Value Insight: Process Stage Bottleneck Analysis")

# Calculate average time spent in each stage
stage_columns = [col for col in df_tickets.columns if "Time in" in col]
stage_analysis = {}

for col in stage_columns:
    stage_name = col.replace("Time in ", "").replace(" (hours)", "")
    avg_time = df_tickets[col].mean()
    total_time = df_tickets[col].sum()
    max_time = df_tickets[col].max()
    tickets_in_stage = len(df_tickets[df_tickets[col] > 0])
    
    stage_analysis[stage_name] = {
        "Avg Time (hrs)": round(avg_time, 2),
        "Total Time (hrs)": round(total_time, 2),
        "Max Time (hrs)": round(max_time, 2),
        "Tickets Affected": tickets_in_stage,
        "Percentage of Total": round((total_time / df_tickets[stage_columns].sum().sum()) * 100, 2)
    }

stage_df = pd.DataFrame(stage_analysis).T
stage_df = stage_df.sort_values("Avg Time (hrs)", ascending=False)

# Identify the bottleneck stage
bottleneck_stage = stage_df.iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Average Time Spent in Each Process Stage")
    stage_chart_df = stage_df[["Avg Time (hrs)"]]
    st.bar_chart(stage_chart_df, height=400)
    
    # Show detailed breakdown
    st.dataframe(stage_df, use_container_width=True)

with col2:
    st.markdown("#### Total Time Spent by Stage")
    total_time_chart = stage_df[["Total Time (hrs)"]]
    st.bar_chart(total_time_chart, height=300)
    
    st.markdown("#### Stage Impact Analysis")
    impact_df = stage_df[["Avg Time (hrs)", "Tickets Affected", "Percentage of Total"]].sort_values("Percentage of Total", ascending=False)
    st.dataframe(impact_df, use_container_width=True)
    
    # Show which stages cause most delay
    st.markdown("#### Top Delay Contributors")
    for idx, (stage, row) in enumerate(stage_df.head(3).iterrows(), 1):
        st.write(f"{idx}. **{stage}**: {row['Avg Time (hrs)']:.1f} hrs avg, {row['Percentage of Total']:.1f}% of total time")

# Key insight
st.error(f"**🚨 Critical Finding**: **{bottleneck_stage.name}** stage causes the greatest delay with an average of **{bottleneck_stage['Avg Time (hrs)']:.1f} hours** per ticket, accounting for **{bottleneck_stage['Percentage of Total']:.1f}%** of total resolution time.")

# Detailed analysis of the bottleneck stage
if bottleneck_stage.name == "Waiting for User":
    waiting_tickets = df_tickets[df_tickets["Time in Waiting for User (hours)"] > 0]
    st.markdown("#### Detailed Analysis: Waiting for User Stage")
    st.warning(f"**{len(waiting_tickets)} tickets** have been in 'Waiting for User' stage, with an average wait time of **{waiting_tickets['Time in Waiting for User (hours)'].mean():.1f} hours**.")
    
    # Show tickets stuck in this stage
    stuck_tickets = waiting_tickets.nlargest(10, "Time in Waiting for User (hours)")[
        ["Ticket ID", "Assigned Staff", "Priority", "Time in Waiting for User (hours)", "Total Resolution Time (hours)"]
    ]
    st.dataframe(stuck_tickets, use_container_width=True)

# ========== COMBINED ANALYSIS: STAFF vs STAGE ==========
st.markdown("---")
st.markdown("### 🔍 Combined Analysis: Staff Performance by Process Stage")

# Get unique staff members from the dataframe
staff_members = df_tickets["Assigned Staff"].unique().tolist()

# Analyze which staff members spend most time in each stage
staff_stage_analysis = []
for staff in staff_members:
    staff_tickets = df_tickets[df_tickets["Assigned Staff"] == staff]
    for stage_col in stage_columns:
        stage_name = stage_col.replace("Time in ", "").replace(" (hours)", "")
        avg_time = staff_tickets[stage_col].mean()
        staff_stage_analysis.append({
            "Staff": staff,
            "Stage": stage_name,
            "Avg Time (hrs)": round(avg_time, 2)
        })

staff_stage_df = pd.DataFrame(staff_stage_analysis)
staff_stage_pivot = staff_stage_df.pivot(index="Staff", columns="Stage", values="Avg Time (hrs)").fillna(0)

st.markdown("#### Average Time Spent by Staff in Each Stage")
st.dataframe(staff_stage_pivot, use_container_width=True)

# Identify problematic combinations
st.markdown("#### Problematic Staff-Stage Combinations")
problematic = staff_stage_df.nlargest(5, "Avg Time (hrs)")
st.dataframe(problematic, use_container_width=True)

# ========== TICKET STATUS BREAKDOWN ==========
st.markdown("---")
st.markdown("### 📋 Ticket Status Breakdown")

status_summary = df_tickets["Status"].value_counts()
status_df = pd.DataFrame({
    "Status": status_summary.index,
    "Count": status_summary.values
})

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Tickets by Status")
    st.bar_chart(status_df.set_index("Status"), height=300)
    st.dataframe(status_df, use_container_width=True)

with col2:
    st.markdown("#### Tickets by Priority")
    priority_summary = df_tickets["Priority"].value_counts()
    priority_df = pd.DataFrame({
        "Priority": priority_summary.index,
        "Count": priority_summary.values
    })
    st.bar_chart(priority_df.set_index("Priority"), height=300)
    st.dataframe(priority_df, use_container_width=True)

# ========== RESOLUTION TIME TRENDS ==========
st.markdown("---")
st.markdown("### 📈 Resolution Time Trends")

# Resolution time by priority
priority_resolution = resolved_tickets.groupby("Priority")["Total Resolution Time (hours)"].agg(['mean', 'median', 'count']).round(2)
priority_resolution.columns = ["Avg Time (hrs)", "Median Time (hrs)", "Ticket Count"]
priority_resolution = priority_resolution.sort_values("Avg Time (hrs)", ascending=False)

st.markdown("#### Resolution Time by Priority")
st.bar_chart(priority_resolution[["Avg Time (hrs)"]], height=300)
st.dataframe(priority_resolution, use_container_width=True)

# ========== DETAILED TICKET DATA ==========
st.markdown("---")
with st.expander("📄 View Detailed Ticket Data"):
    st.dataframe(
        df_tickets.sort_values("Total Resolution Time (hours)", ascending=False),
        use_container_width=True,
        height=400
    )

# ========== RECOMMENDATIONS ==========
st.markdown("---")
st.markdown("### 💡 Recommendations")
st.markdown(f"""
1. **Staff Performance**: Address performance issues with **{slowest_staff.name}** who has {performance_pct:.1f}% slower resolution times than team average
2. **Process Bottleneck**: **{bottleneck_stage.name}** stage is the primary bottleneck - implement automated follow-ups and escalation procedures
3. **Waiting for User**: Establish clear SLAs and automated reminders for tickets waiting on user response
4. **Training**: Provide additional training to staff members with below-average performance
5. **Process Optimization**: Review and streamline the **{bottleneck_stage.name}** stage workflow
6. **Monitoring**: Implement real-time alerts for tickets stuck in any stage beyond expected timeframes
7. **Escalation Policy**: Create automatic escalation rules for tickets exceeding stage-specific time thresholds
""")

# ========== AI ASSISTANT TAB ==========
with tab2:
    st.markdown("---")
    if IT_OPERATIONS_API_KEY and IT_OPERATIONS_API_KEY != "":
        itoperations_ai_chat(IT_OPERATIONS_API_KEY, df_tickets)
    else:
        st.error("⚠️ API Key Not Configured")
        st.warning("Please add your OpenAI API key to `.env` file in the project root.")
        st.info("""
        **Instructions:**
        1. Copy `.env.example` to `.env` in the project root directory
        2. Open `.env` file and replace `your-it-operations-api-key-here` with your actual API key
        3. Get your API key from: https://platform.openai.com/api-keys
        4. Restart the application
        5. **Important**: The `.env` file is already in `.gitignore` and will not be committed to GitHub
        """)

# ========== MANAGE TICKETS TAB ==========
with tab3:
    st.markdown("---")
    st.markdown("### ✏️ Manage Tickets")
    
    # Sub-tabs for different operations
    manage_tab1, manage_tab2, manage_tab3 = st.tabs(["➕ Add New", "✏️ Update", "🗑️ Delete"])
    
    with manage_tab1:
        st.markdown("#### Add New Ticket")
        with st.form("add_ticket_form"):
            col1, col2 = st.columns(2)
            with col1:
                ticket_id = st.text_input("Ticket ID", value=f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}")
                assigned_staff = st.selectbox("Assigned Staff",
                    ["tech_support_01", "tech_support_02", "tech_support_03", "Unassigned"])
                priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
                created_date = st.date_input("Created Date", value=datetime.now().date())
            with col2:
                status = st.selectbox("Status",
                    ["New", "Assigned", "In Progress", "Waiting for User", "Resolved"])
                category = st.text_input("Category", value="General")
                subject = st.text_input("Subject")
                description = st.text_area("Description", height=100)
            
            resolution_date = None
            resolution_time = 0.0
            if status == "Resolved":
                resolution_date = st.date_input("Resolution Date", value=datetime.now().date())
                if resolution_date and created_date:
                    delta = resolution_date - created_date
                    resolution_time = delta.total_seconds() / 3600
            
            submitted = st.form_submit_button("Add Ticket", use_container_width=True)
            
            if submitted:
                try:
                    # Create stage times distribution
                    stage_times = {}
                    if resolution_time > 0:
                        stage_times = {
                            "New": resolution_time * 0.1,
                            "Assigned": resolution_time * 0.1,
                            "In Progress": resolution_time * 0.3,
                            "Waiting for User": resolution_time * 0.3,
                            "Resolved": resolution_time * 0.2
                        }
                    
                    ticket = ITTicket(
                        ticket_id=ticket_id,
                        assigned_staff=assigned_staff,
                        priority=priority,
                        created_date=created_date,
                        status=status,
                        total_resolution_time_hours=round(resolution_time, 2),
                        resolution_date=resolution_date,
                        stage_times=stage_times
                    )
                    
                    # Insert into database
                    conn = connect_database()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO it_tickets 
                        (ticket_id, priority, status, category, subject, description, created_date, resolved_date, assigned_to)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        ticket_id,
                        priority,
                        status,
                        category,
                        subject,
                        description,
                        str(created_date),
                        str(resolution_date) if resolution_date else None,
                        assigned_staff
                    ))
                    conn.commit()
                    ticket_db_id = cursor.lastrowid
                    conn.close()
                    
                    # Add to repository
                    repository.add(ticket)
                    
                    st.success(f"✅ Ticket '{ticket_id}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding ticket: {str(e)}")
    
    with manage_tab2:
        st.markdown("#### Update Ticket")
        
        all_tickets = repository.get_all()
        if len(all_tickets) > 0:
            df_all = repository.to_dataframe()
            df_all['Index'] = range(len(df_all))
            
            selected_idx = st.selectbox("Select Ticket to Update", 
                options=range(len(df_all)),
                format_func=lambda x: f"{df_all.iloc[x]['Ticket ID']} - {df_all.iloc[x]['Status']} ({df_all.iloc[x]['Priority']})")
            
            selected_ticket = all_tickets[selected_idx]
            
            with st.form("update_ticket_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_status = st.selectbox("Status",
                        ["New", "Assigned", "In Progress", "Waiting for User", "Resolved"],
                        index=["New", "Assigned", "In Progress", "Waiting for User", "Resolved"].index(selected_ticket.status))
                    new_priority = st.selectbox("Priority",
                        ["Critical", "High", "Medium", "Low"],
                        index=["Critical", "High", "Medium", "Low"].index(selected_ticket.priority))
                    new_staff = st.selectbox("Assigned Staff",
                        ["tech_support_01", "tech_support_02", "tech_support_03", "Unassigned"],
                        index=["tech_support_01", "tech_support_02", "tech_support_03", "Unassigned"].index(selected_ticket.assigned_staff) if selected_ticket.assigned_staff in ["tech_support_01", "tech_support_02", "tech_support_03", "Unassigned"] else 3)
                with col2:
                    new_resolution_date = None
                    if new_status == "Resolved":
                        new_resolution_date = st.date_input("Resolution Date", 
                            value=selected_ticket.resolution_date if selected_ticket.resolution_date else datetime.now().date())
                    else:
                        new_resolution_date = st.date_input("Resolution Date", 
                            value=selected_ticket.resolution_date if selected_ticket.resolution_date else None,
                            disabled=True)
                
                submitted = st.form_submit_button("Update Ticket", use_container_width=True)
                
                if submitted:
                    try:
                        # Calculate resolution time if resolved
                        new_resolution_time = 0.0
                        new_stage_times = {}
                        if new_status == "Resolved" and new_resolution_date:
                            delta = new_resolution_date - selected_ticket.created_date
                            new_resolution_time = delta.total_seconds() / 3600
                            new_stage_times = {
                                "New": new_resolution_time * 0.1,
                                "Assigned": new_resolution_time * 0.1,
                                "In Progress": new_resolution_time * 0.3,
                                "Waiting for User": new_resolution_time * 0.3,
                                "Resolved": new_resolution_time * 0.2
                            }
                        
                        # Update in database
                        conn = connect_database()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE it_tickets 
                            SET priority = ?, status = ?, resolved_date = ?, assigned_to = ?
                            WHERE ticket_id = ?
                        """, (
                            new_priority,
                            new_status,
                            str(new_resolution_date) if new_resolution_date else None,
                            new_staff,
                            selected_ticket.ticket_id
                        ))
                        conn.commit()
                        conn.close()
                        
                        # Update in repository
                        selected_ticket.status = new_status
                        selected_ticket.priority = new_priority
                        selected_ticket.assigned_staff = new_staff
                        selected_ticket.resolution_date = new_resolution_date
                        selected_ticket.total_resolution_time_hours = round(new_resolution_time, 2)
                        selected_ticket.stage_times = new_stage_times
                        
                        st.success("✅ Ticket updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating ticket: {str(e)}")
        else:
            st.info("No tickets available to update.")
    
    with manage_tab3:
        st.markdown("#### Delete Ticket")
        
        all_tickets = repository.get_all()
        if len(all_tickets) > 0:
            df_all = repository.to_dataframe()
            df_all['Index'] = range(len(df_all))
            
            selected_idx = st.selectbox("Select Ticket to Delete", 
                options=range(len(df_all)),
                format_func=lambda x: f"{df_all.iloc[x]['Ticket ID']} - {df_all.iloc[x]['Status']} ({df_all.iloc[x]['Priority']})")
            
            selected_ticket = all_tickets[selected_idx]
            
            st.warning(f"⚠️ You are about to delete: **{selected_ticket.ticket_id}** ({selected_ticket.status})")
            
            if st.button("🗑️ Delete Ticket", use_container_width=True, type="primary"):
                try:
                    # Delete from database
                    conn = connect_database()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM it_tickets WHERE ticket_id = ?", (selected_ticket.ticket_id,))
                    conn.commit()
                    conn.close()
                    
                    # Remove from repository
                    repository._tickets.remove(selected_ticket)
                    
                    st.success("✅ Ticket deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting ticket: {str(e)}")
        else:
            st.info("No tickets available to delete.")

# ========== FILTER & SEARCH TAB ==========
with tab4:
    st.markdown("---")
    st.markdown("### 🔍 Filter & Search Tickets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.multiselect("Filter by Status",
            ["New", "Assigned", "In Progress", "Waiting for User", "Resolved"],
            default=[])
        filter_priority = st.multiselect("Filter by Priority",
            ["Critical", "High", "Medium", "Low"],
            default=[])
    
    with col2:
        filter_staff = st.multiselect("Filter by Assigned Staff",
            df_tickets["Assigned Staff"].unique().tolist() if not df_tickets.empty else [],
            default=[])
        search_text = st.text_input("🔍 Search (Ticket ID)", "")
    
    with col3:
        date_range = st.date_input("Created Date Range",
            value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
            max_value=datetime.now().date())
        min_resolution_time = st.number_input("Min Resolution Time (hours)", min_value=0.0, value=0.0, step=0.1)
        max_resolution_time = st.number_input("Max Resolution Time (hours)", min_value=0.0, value=float(df_tickets["Total Resolution Time (hours)"].max()) if not df_tickets.empty else 100.0, step=0.1)
    
    # Apply filters
    filtered_df = df_tickets.copy()
    
    if filter_status:
        filtered_df = filtered_df[filtered_df["Status"].isin(filter_status)]
    if filter_priority:
        filtered_df = filtered_df[filtered_df["Priority"].isin(filter_priority)]
    if filter_staff:
        filtered_df = filtered_df[filtered_df["Assigned Staff"].isin(filter_staff)]
    if search_text:
        filtered_df = filtered_df[filtered_df["Ticket ID"].str.contains(search_text, case=False, na=False)]
    if isinstance(date_range, tuple) and len(date_range) == 2 and "Created Date" in filtered_df.columns:
        try:
            created_dates = pd.to_datetime(filtered_df["Created Date"]).dt.date
            filtered_df = filtered_df[
                (created_dates >= date_range[0]) &
                (created_dates <= date_range[1])
            ]
        except:
            pass  # Skip date filtering if conversion fails
    if min_resolution_time > 0 or max_resolution_time < float('inf'):
        filtered_df = filtered_df[
            (filtered_df["Total Resolution Time (hours)"] >= min_resolution_time) &
            (filtered_df["Total Resolution Time (hours)"] <= max_resolution_time)
        ]
    
    st.markdown(f"**Found {len(filtered_df)} ticket(s)**")
    
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Export option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Results (CSV)",
            data=csv,
            file_name=f"tickets_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No tickets match the selected filters.")

