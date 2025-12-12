import streamlit as st
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_app.utilities.data_generators import DatasetGenerator
from my_app.repositories.dataset_repository import DatasetRepository
from my_app.services.dataset_service import DatasetService
from my_app.AI.ai_assistant import datascience_ai_chat
from my_app.models.dataset import Dataset
from app.data.db import connect_database
from datetime import datetime, date

# Get API key from environment variable
DATA_SCIENCE_API_KEY = os.getenv("DATA_SCIENCE_API_KEY", "")

st.set_page_config(page_title="Data Science", page_icon="📊", layout="wide")

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
        if key == "datascience":
            st.info(f"**{label}** (Current Page)")
        else:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                st.switch_page(page)
    
    st.markdown("---")
    
    # Current Section Display
    with st.container():
        st.markdown("### 📊 Data Science")
        st.markdown("**Data Governance Center**")
    
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
if st.session_state.user_role != "Data Scientist":
    st.error(f"⚠️ Access Denied: This page is only accessible to Data Scientist users. Your role is: {st.session_state.user_role}")
    if st.button("Go to login page"):
        st.switch_page("Home.py")
    st.stop()

# ========== HEADER ==========
st.title("📊 Data Science Dashboard")
st.success(f"Welcome, **{st.session_state.username}**! Data Governance & Discovery Analytics.")

# ========== TABS ==========
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🤖 AI Assistant", "✏️ Manage Datasets", "🔍 Filter & Search"])

# Generate data using OOP structure
# Try to load from database first, fallback to generated data if empty
repository = DatasetRepository(use_database=True)
if len(repository.get_all()) == 0:
    # No data in database, generate sample data
    generator = DatasetGenerator(seed=42)
    datasets = generator.generate()
    repository = DatasetRepository(datasets, use_database=False)
service = DatasetService(repository)
df_datasets = service.to_dataframe()

# ========== DASHBOARD TAB ==========
with tab1:
    # ========== PROBLEM STATEMENT ==========
    st.markdown("---")
    st.markdown("### 🚨 Core Problem: Data Governance & Discovery")
    st.warning("**Critical Issue**: The team must manage a growing catalog of large datasets uploaded by various departments (IT, Cyber), requiring quality checks and resource management.")

    # ========== KEY METRICS ==========
    st.markdown("---")
    st.markdown("### 📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    total_datasets = len(df_datasets)
    total_size_gb = df_datasets["Size (GB)"].sum()
    total_storage_cost = df_datasets["Storage Cost ($/month)"].sum()
    pending_quality_checks = len(df_datasets[df_datasets["Quality Status"] == "Pending"])

    with col1:
        st.metric("Total Datasets", total_datasets, delta=None)
    with col2:
        st.metric("Total Storage", f"{total_size_gb:.0f} GB", delta=f"{total_size_gb:.0f} GB")
    with col3:
        st.metric("Monthly Storage Cost", f"${total_storage_cost:.2f}", delta=f"${total_storage_cost:.2f}", delta_color="inverse")
    with col4:
        st.metric("Pending Quality Checks", pending_quality_checks, delta=f"{pending_quality_checks}", delta_color="inverse")

    # ========== RESOURCE CONSUMPTION ANALYSIS ==========
    st.markdown("---")
    st.markdown("### 📈 High-Value Insight: Resource Consumption Analysis")

    # Resource consumption by department
    st.markdown("#### 🔍 Dataset Resource Consumption by Department")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Storage Size by Department")
        dept_size = df_datasets.groupby("Department")["Size (GB)"].sum().sort_values(ascending=False)
        dept_size_df = pd.DataFrame({
            "Department": dept_size.index,
            "Total Size (GB)": dept_size.values
        })
        st.bar_chart(dept_size_df.set_index("Department"), height=300)
        
        # Show detailed breakdown
        st.dataframe(dept_size_df, use_container_width=True)

    with col2:
        st.markdown("##### Row Count by Department")
        dept_rows = df_datasets.groupby("Department")["Rows (Millions)"].sum().sort_values(ascending=False)
        dept_rows_df = pd.DataFrame({
            "Department": dept_rows.index,
            "Total Rows (Millions)": dept_rows.values
        })
        st.bar_chart(dept_rows_df.set_index("Department"), height=300)
        
        # Show detailed breakdown
        st.dataframe(dept_rows_df, use_container_width=True)

    # Top resource consumers
    st.markdown("#### Top 5 Resource-Consuming Datasets")
    top_consumers = df_datasets.nlargest(5, "Size (GB)")[["Dataset Name", "Department", "Size (GB)", "Rows (Millions)", "Storage Cost ($/month)"]]
    st.dataframe(top_consumers, use_container_width=True)

    # Size vs Rows correlation
    st.markdown("#### Dataset Size vs Row Count Analysis")
    size_rows_df = df_datasets[["Dataset Name", "Size (GB)", "Rows (Millions)"]].set_index("Dataset Name")
    st.scatter_chart(size_rows_df, x="Size (GB)", y="Rows (Millions)", height=400)

    # ========== DATA SOURCE DEPENDENCY ANALYSIS ==========
    st.markdown("---")
    st.markdown("### 🔗 Data Source Dependency Analysis")

    col1, col2 = st.columns(2)

    # Get dependency analysis from service
    dependency_analysis = service.get_dependency_analysis()
    
    with col1:
        st.markdown("#### Dataset Dependencies")
        # Datasets with most dependencies (most critical)
        high_dependency_list = dependency_analysis["high_dependency_datasets"]
        high_dependency_df = pd.DataFrame([ds.to_dict() for ds in high_dependency_list])
        st.dataframe(high_dependency_df[["Dataset Name", "Department", "Dependencies", "Size (GB)"]], use_container_width=True)
        
        st.info("**Critical Datasets**: These datasets have the most dependencies and should be prioritized for quality checks and monitoring.")

    with col2:
        st.markdown("#### Dependency Distribution")
        dependency_dist = df_datasets["Dependencies"].value_counts().sort_index()
        dep_df = pd.DataFrame({
            "Dependencies": dependency_dist.index,
            "Count": dependency_dist.values
        })
        st.bar_chart(dep_df.set_index("Dependencies"), height=300)
        
        # Show statistics
        avg_dependencies = df_datasets["Dependencies"].mean()
        max_dependencies = df_datasets["Dependencies"].max()
        st.metric("Average Dependencies", f"{avg_dependencies:.1f}")
        st.metric("Max Dependencies", max_dependencies)

    # Dependency network summary
    st.markdown("#### Dependency Risk Assessment")
    risk_levels = dependency_analysis["risk_levels"]
    risk_summary_df = pd.DataFrame({
        "Risk Level": list(risk_levels.keys()),
        "Dataset Count": list(risk_levels.values())
    })
    st.dataframe(risk_summary_df, use_container_width=True)

    # ========== QUALITY CHECKS STATUS ==========
    st.markdown("---")
    st.markdown("### ✅ Quality Checks Status")

    quality_summary = df_datasets.groupby(["Department", "Quality Status"]).size().reset_index(name="Count")
    quality_pivot = quality_summary.pivot(index="Department", columns="Quality Status", values="Count").fillna(0)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Quality Status by Department")
        st.bar_chart(quality_pivot, height=300)
        st.dataframe(quality_pivot, use_container_width=True)

    with col2:
        st.markdown("#### Overall Quality Status")
        overall_quality = df_datasets["Quality Status"].value_counts()
        quality_df = pd.DataFrame({
            "Status": overall_quality.index,
            "Count": overall_quality.values
        })
        st.bar_chart(quality_df.set_index("Status"), height=300)
        
        # Show failed datasets
        failed_datasets = df_datasets[df_datasets["Quality Status"] == "Failed"][["Dataset Name", "Department", "Size (GB)"]]
        if len(failed_datasets) > 0:
            st.warning(f"**{len(failed_datasets)} datasets failed quality checks**")
            st.dataframe(failed_datasets, use_container_width=True)

    # ========== ARCHIVING RECOMMENDATIONS ==========
    st.markdown("---")
    st.markdown("### 💾 Data Governance & Archiving Policy Recommendations")

    # Get archiving recommendations from service
    archiving_recs = service.get_archiving_recommendations(limit=5)

    st.markdown("#### Top 5 Archiving Candidates")
    st.info("**Archiving Criteria**: Low access frequency, old last accessed date, low dependencies, and large storage size.")
    
    if archiving_recs["candidates"]:
        archive_candidates_df = pd.DataFrame([ds.to_dict() for ds in archiving_recs["candidates"]])
        st.dataframe(archive_candidates_df[["Dataset Name", "Department", "Size (GB)", "Days Since Access", 
                                             "Access Frequency (30d)", "Dependencies", "Archive Score"]], use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Potential Storage Freed", f"{archiving_recs['potential_savings_gb']:.0f} GB")
    with col2:
        st.metric("Monthly Cost Savings", f"${archiving_recs['potential_cost_savings_monthly']:.2f}")
    with col3:
        st.metric("Annual Cost Savings", f"${archiving_recs['potential_cost_savings_annual']:.2f}")

    # Archiving recommendations by department
    st.markdown("#### Archiving Recommendations by Department")
    dept_archive = df_datasets.groupby("Department").agg({
        "Archive Score": "mean",
        "Size (GB)": "sum",
        "Dataset Name": "count"
    }).round(2)
    dept_archive.columns = ["Avg Archive Score", "Total Size (GB)", "Dataset Count"]
    dept_archive = dept_archive.sort_values("Avg Archive Score", ascending=False)
    st.dataframe(dept_archive, use_container_width=True)

    # ========== ACCESS PATTERNS ==========
    st.markdown("---")
    st.markdown("### 📊 Dataset Access Patterns")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Access Frequency Distribution")
        access_freq = df_datasets["Access Frequency (30d)"].value_counts().sort_index()
        access_df = pd.DataFrame({
            "Access Frequency": access_freq.index,
            "Dataset Count": access_freq.values
        })
        st.bar_chart(access_df.set_index("Access Frequency"), height=300)
        
        # Identify rarely accessed datasets using repository
        rarely_accessed = repository.get_rarely_accessed(threshold=5)
        st.warning(f"**{len(rarely_accessed)} datasets accessed less than 5 times in last 30 days**")

    with col2:
        st.markdown("#### Days Since Last Access")
        days_since = df_datasets["Days Since Access"].value_counts().sort_index()
        days_df = pd.DataFrame({
            "Days Since Access": days_since.index,
            "Dataset Count": days_since.values
        })
        st.bar_chart(days_df.set_index("Days Since Access"), height=300)
        
        # Identify stale datasets using repository
        stale_datasets = repository.get_stale_datasets(days_threshold=90)
        st.warning(f"**{len(stale_datasets)} datasets not accessed in over 90 days**")

    # ========== DETAILED DATASET CATALOG ==========
    st.markdown("---")
    with st.expander("📄 View Complete Dataset Catalog"):
        st.dataframe(
            df_datasets.sort_values("Size (GB)", ascending=False),
            use_container_width=True,
            height=400
        )

    # ========== RECOMMENDATIONS ==========
    st.markdown("---")
    st.markdown("### 💡 Data Governance Recommendations")
    archiving_recs = service.get_archiving_recommendations(limit=5)
    st.markdown(f"""
    1. **Immediate Archiving**: Archive the top 5 candidates to free up **{archiving_recs['potential_savings_gb']:.0f} GB** of storage and save **${archiving_recs['potential_cost_savings_monthly']:.2f}/month**
    2. **Quality Check Priority**: Focus quality checks on datasets with high dependencies to ensure data integrity
    3. **Department Coordination**: IT and Cyber departments contribute the most storage - coordinate with them for data lifecycle management
    4. **Access Monitoring**: Implement automated monitoring for datasets not accessed in 90+ days for archiving consideration
    5. **Dependency Mapping**: Create a dependency graph to identify critical datasets that require enhanced monitoring and backup
    6. **Storage Optimization**: Review large datasets (>200GB) for compression or partitioning opportunities
    7. **Data Retention Policy**: Establish clear retention policies based on access patterns and business requirements
    """)

# ========== AI ASSISTANT TAB ==========
with tab2:
    st.markdown("---")
    if DATA_SCIENCE_API_KEY and DATA_SCIENCE_API_KEY != "":
        datascience_ai_chat(DATA_SCIENCE_API_KEY, df_datasets)
    else:
        st.error("⚠️ API Key Not Configured")
        st.warning("Please add your OpenAI API key to `.env` file in the project root.")
        st.info("""
        **Instructions:**
        1. Copy `.env.example` to `.env` in the project root directory
        2. Open `.env` file and replace `your-data-science-api-key-here` with your actual API key
        3. Get your API key from: https://platform.openai.com/api-keys
        4. Restart the application
        5. **Important**: The `.env` file is already in `.gitignore` and will not be committed to GitHub
        """)

# ========== MANAGE DATASETS TAB ==========
with tab3:
    st.markdown("---")
    st.markdown("### ✏️ Manage Datasets")
    
    # Sub-tabs for different operations
    manage_tab1, manage_tab2, manage_tab3 = st.tabs(["➕ Add New", "✏️ Update", "🗑️ Delete"])
    
    with manage_tab1:
        st.markdown("#### Add New Dataset")
        with st.form("add_dataset_form"):
            col1, col2 = st.columns(2)
            with col1:
                dataset_name = st.text_input("Dataset Name")
                department = st.selectbox("Department", ["IT", "Cyber", "Finance", "HR", "Operations", "Other"])
                size_gb = st.number_input("Size (GB)", min_value=0.0, value=0.0, step=0.1)
                rows_millions = st.number_input("Rows (Millions)", min_value=0.0, value=0.0, step=0.1)
            with col2:
                upload_date = st.date_input("Upload Date", value=datetime.now().date())
                last_accessed = st.date_input("Last Accessed", value=datetime.now().date())
                quality_status = st.selectbox("Quality Status", ["Passed", "Failed", "Pending"])
                dependencies = st.number_input("Dependencies", min_value=0, value=0, step=1)
            
            access_frequency = st.number_input("Access Frequency (30 days)", min_value=0, value=0, step=1)
            
            submitted = st.form_submit_button("Add Dataset", use_container_width=True)
            
            if submitted:
                try:
                    days_since = (datetime.now().date() - last_accessed).days
                    storage_cost = round(size_gb * 0.023, 2)
                    
                    dataset = Dataset(
                        name=dataset_name,
                        department=department,
                        size_gb=size_gb,
                        rows_millions=rows_millions,
                        upload_date=upload_date,
                        last_accessed=last_accessed,
                        days_since_access=days_since,
                        quality_status=quality_status,
                        dependencies=dependencies,
                        access_frequency_30d=access_frequency,
                        storage_cost_per_month=storage_cost
                    )
                    dataset.calculate_archive_score()
                    
                    # Insert into database
                    conn = connect_database()
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO datasets_metadata 
                        (dataset_name, category, source, last_updated, record_count, file_size_mb)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        dataset_name,
                        department,
                        department,
                        str(last_accessed),
                        int(rows_millions * 1_000_000),
                        size_gb * 1024
                    ))
                    conn.commit()
                    dataset_id = cursor.lastrowid
                    conn.close()
                    
                    # Add to repository
                    repository.add(dataset)
                    
                    st.success(f"✅ Dataset '{dataset_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding dataset: {str(e)}")
    
    with manage_tab2:
        st.markdown("#### Update Dataset")
        
        all_datasets = repository.get_all()
        if len(all_datasets) > 0:
            df_all = repository.to_dataframe()
            df_all['Index'] = range(len(df_all))
            
            selected_idx = st.selectbox("Select Dataset to Update", 
                options=range(len(df_all)),
                format_func=lambda x: f"{df_all.iloc[x]['Dataset Name']} - {df_all.iloc[x]['Department']}")
            
            selected_dataset = all_datasets[selected_idx]
            
            with st.form("update_dataset_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Dataset Name", value=selected_dataset.name)
                    new_department = st.selectbox("Department",
                        ["IT", "Cyber", "Finance", "HR", "Operations", "Other"],
                        index=["IT", "Cyber", "Finance", "HR", "Operations", "Other"].index(selected_dataset.department) if selected_dataset.department in ["IT", "Cyber", "Finance", "HR", "Operations", "Other"] else 0)
                    new_size = st.number_input("Size (GB)", min_value=0.0, value=selected_dataset.size_gb, step=0.1)
                    new_rows = st.number_input("Rows (Millions)", min_value=0.0, value=selected_dataset.rows_millions, step=0.1)
                with col2:
                    new_quality = st.selectbox("Quality Status",
                        ["Passed", "Failed", "Pending"],
                        index=["Passed", "Failed", "Pending"].index(selected_dataset.quality_status))
                    new_dependencies = st.number_input("Dependencies", min_value=0, value=selected_dataset.dependencies, step=1)
                    new_access_freq = st.number_input("Access Frequency (30 days)", min_value=0, value=selected_dataset.access_frequency_30d, step=1)
                    new_last_accessed = st.date_input("Last Accessed", value=selected_dataset.last_accessed)
                
                submitted = st.form_submit_button("Update Dataset", use_container_width=True)
                
                if submitted:
                    try:
                        # Update in database
                        conn = connect_database()
                        cursor = conn.cursor()
                        cursor.execute("""
                            UPDATE datasets_metadata 
                            SET dataset_name = ?, category = ?, source = ?, last_updated = ?, 
                                record_count = ?, file_size_mb = ?
                            WHERE dataset_name = ?
                        """, (
                            new_name,
                            new_department,
                            new_department,
                            str(new_last_accessed),
                            int(new_rows * 1_000_000),
                            new_size * 1024,
                            selected_dataset.name
                        ))
                        conn.commit()
                        conn.close()
                        
                        # Update in repository
                        selected_dataset.name = new_name
                        selected_dataset.department = new_department
                        selected_dataset.size_gb = new_size
                        selected_dataset.rows_millions = new_rows
                        selected_dataset.quality_status = new_quality
                        selected_dataset.dependencies = new_dependencies
                        selected_dataset.access_frequency_30d = new_access_freq
                        selected_dataset.last_accessed = new_last_accessed
                        selected_dataset.days_since_access = (datetime.now().date() - new_last_accessed).days
                        selected_dataset.storage_cost_per_month = round(new_size * 0.023, 2)
                        selected_dataset.calculate_archive_score()
                        
                        st.success("✅ Dataset updated successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error updating dataset: {str(e)}")
        else:
            st.info("No datasets available to update.")
    
    with manage_tab3:
        st.markdown("#### Delete Dataset")
        
        all_datasets = repository.get_all()
        if len(all_datasets) > 0:
            df_all = repository.to_dataframe()
            df_all['Index'] = range(len(df_all))
            
            selected_idx = st.selectbox("Select Dataset to Delete", 
                options=range(len(df_all)),
                format_func=lambda x: f"{df_all.iloc[x]['Dataset Name']} - {df_all.iloc[x]['Department']}")
            
            selected_dataset = all_datasets[selected_idx]
            
            st.warning(f"⚠️ You are about to delete: **{selected_dataset.name}** ({selected_dataset.department})")
            
            if st.button("🗑️ Delete Dataset", use_container_width=True, type="primary"):
                try:
                    # Delete from database
                    conn = connect_database()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM datasets_metadata WHERE dataset_name = ?", (selected_dataset.name,))
                    conn.commit()
                    conn.close()
                    
                    # Remove from repository
                    repository._datasets.remove(selected_dataset)
                    
                    st.success("✅ Dataset deleted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error deleting dataset: {str(e)}")
        else:
            st.info("No datasets available to delete.")

# ========== FILTER & SEARCH TAB ==========
with tab4:
    st.markdown("---")
    st.markdown("### 🔍 Filter & Search Datasets")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_department = st.multiselect("Filter by Department",
            df_datasets["Department"].unique().tolist() if not df_datasets.empty else [],
            default=[])
        filter_quality = st.multiselect("Filter by Quality Status",
            ["Passed", "Failed", "Pending"],
            default=[])
    
    with col2:
        min_size = st.number_input("Min Size (GB)", min_value=0.0, value=0.0, step=1.0)
        max_size = st.number_input("Max Size (GB)", min_value=0.0, value=float(df_datasets["Size (GB)"].max()) if not df_datasets.empty else 1000.0, step=1.0)
        search_text = st.text_input("🔍 Search (Dataset Name)", "")
    
    with col3:
        min_dependencies = st.number_input("Min Dependencies", min_value=0, value=0, step=1)
        max_dependencies = st.number_input("Max Dependencies", min_value=0, value=int(df_datasets["Dependencies"].max()) if not df_datasets.empty else 10, step=1)
        min_access_freq = st.number_input("Min Access Frequency (30d)", min_value=0, value=0, step=1)
    
    # Apply filters
    filtered_df = df_datasets.copy()
    
    if filter_department:
        filtered_df = filtered_df[filtered_df["Department"].isin(filter_department)]
    if filter_quality:
        filtered_df = filtered_df[filtered_df["Quality Status"].isin(filter_quality)]
    if search_text:
        filtered_df = filtered_df[filtered_df["Dataset Name"].str.contains(search_text, case=False, na=False)]
    if min_size > 0 or max_size < float('inf'):
        filtered_df = filtered_df[
            (filtered_df["Size (GB)"] >= min_size) &
            (filtered_df["Size (GB)"] <= max_size)
        ]
    if min_dependencies > 0 or max_dependencies < float('inf'):
        filtered_df = filtered_df[
            (filtered_df["Dependencies"] >= min_dependencies) &
            (filtered_df["Dependencies"] <= max_dependencies)
        ]
    if min_access_freq > 0:
        filtered_df = filtered_df[filtered_df["Access Frequency (30d)"] >= min_access_freq]
    
    st.markdown(f"**Found {len(filtered_df)} dataset(s)**")
    
    if len(filtered_df) > 0:
        st.dataframe(filtered_df, use_container_width=True, height=400)
        
        # Export option
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Results (CSV)",
            data=csv,
            file_name=f"datasets_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No datasets match the selected filters.")

# ========== LOGOUT ==========
st.divider()
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    st.info("You have been logged out.")
    st.switch_page("Home.py")
