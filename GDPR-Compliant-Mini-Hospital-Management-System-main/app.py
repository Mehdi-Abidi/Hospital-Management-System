# This library is for future compatibility
from __future__ import annotations 

from datetime import datetime, timedelta
from typing import List

import pandas as pd
import streamlit as st
# database operations
from database import (
    delete_patient,
    fetch_log_counts_by_day,
    fetch_logs,
    fetch_patients,
    get_user_by_username,
    init_db,
    insert_patient,
    log_action,
    patient_count,
    refresh_anonymized_fields,
    update_patient,
)
# password hashing and verification
from security import verify_password 
# Application start time for uptime calculation
APP_START = datetime.utcnow() 
# Data retention period in days
RETENTION_DAYS = 365 

#  Application theme and session management 
def apply_dark_theme():
    """Apply custom dark slate theme with glassmorphism CSS"""
    st.markdown("""
    <style>
        /* Import Shield Icon Font */
        @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
        
        /* Global Dark Black Theme */
        .stApp {
            background: #000000;
            background-image: 
                radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.2) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(88, 28, 135, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(30, 58, 138, 0.2) 0px, transparent 50%),
                radial-gradient(at 0% 100%, rgba(88, 28, 135, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main content area */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #f1f5f9 !important;
            font-weight: 600 !important;
            text-shadow: 0 2px 10px rgba(59, 130, 246, 0.3);
        }
        
        h1 {
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2 {
            font-size: 2rem !important;
            margin-top: 2rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        /* Sidebar styling with glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-right: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: #cbd5e1;
        }
        
        /* Sidebar title */
        [data-testid="stSidebar"] h1 {
            color: #f1f5f9 !important;
            font-size: 1.5rem !important;
            padding: 1rem 0;
        }
        
        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(10, 10, 10, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 
                0 8px 32px 0 rgba(0, 0, 0, 0.5),
                inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        }
        
        /* Buttons with glassmorphism */
        .stButton > button {
            background: rgba(59, 130, 246, 0.2);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: #bfdbfe;
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 0.5rem;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
        }
        
        .stButton > button:hover {
            background: rgba(59, 130, 246, 0.3);
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
            transform: translateY(-2px);
        }
        
        /* Form buttons */
        .stFormSubmitButton > button {
            background: rgba(16, 185, 129, 0.2);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: #a7f3d0;
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 0.5rem;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .stFormSubmitButton > button:hover {
            background: rgba(16, 185, 129, 0.3);
            border-color: rgba(16, 185, 129, 0.5);
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
        }
        
        /* Text inputs with glassmorphism */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background: rgba(10, 10, 10, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: #e2e8f0;
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 0.5rem;
            padding: 0.75rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            background: rgba(10, 10, 10, 0.8);
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        /* Select boxes with glassmorphism */
        .stSelectbox > div > div > select {
            background: rgba(10, 10, 10, 0.6);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: #e2e8f0;
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 0.5rem;
        }
        
        /* Radio buttons with glassmorphism */
        .stRadio > div {
            background: rgba(10, 10, 10, 0.5);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            padding: 1rem;
            border-radius: 0.75rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        /* Checkbox */
        .stCheckbox {
            color: #cbd5e1;
        }
        
        /* Metrics with glassmorphism */
        [data-testid="stMetricValue"] {
            color: #60a5fa !important;
            font-size: 2rem !important;
            font-weight: 600 !important;
            text-shadow: 0 2px 10px rgba(59, 130, 246, 0.5);
        }
        
        [data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.875rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        [data-testid="stMetric"] {
            background: rgba(10, 10, 10, 0.6);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            box-shadow: 
                0 8px 32px 0 rgba(0, 0, 0, 0.5),
                inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
        }
        
        /* Info/Success/Warning/Error boxes with glassmorphism */
        .stAlert {
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 0.75rem;
            border-left: 4px solid;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }
        
        .stSuccess {
            background: rgba(16, 185, 129, 0.1);
            border-left-color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: #a7f3d0;
        }
        
        .stInfo {
            background: rgba(59, 130, 246, 0.1);
            border-left-color: #3b82f6;
            border: 1px solid rgba(59, 130, 246, 0.2);
            color: #bfdbfe;
        }
        
        .stWarning {
            background: rgba(245, 158, 11, 0.1);
            border-left-color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.2);
            color: #fde68a;
        }
        
        .stError {
            background: rgba(239, 68, 68, 0.1);
            border-left-color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #fecaca;
        }
        
        /* Dataframes with glassmorphism */
        .stDataFrame {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 0.75rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            overflow: hidden;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        /* Expanders with glassmorphism */
        .streamlit-expanderHeader {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: #e2e8f0 !important;
            border-radius: 0.5rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            font-weight: 500;
        }
        
        .streamlit-expanderContent {
            background: rgba(30, 41, 59, 0.2);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-top: none;
            border-radius: 0 0 0.5rem 0.5rem;
        }
        
        /* Divider */
        hr {
            border-color: rgba(148, 163, 184, 0.2);
            margin: 2rem 0;
        }
        
        /* Caption text */
        .caption {
            color: #64748b !important;
            font-size: 0.875rem;
        }
        
        /* Download button with glassmorphism */
        .stDownloadButton > button {
            background: rgba(139, 92, 246, 0.2);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            color: #c4b5fd;
            border: 1px solid rgba(139, 92, 246, 0.3);
            border-radius: 0.5rem;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
        }
        
        .stDownloadButton > button:hover {
            background: rgba(139, 92, 246, 0.3);
            border-color: rgba(139, 92, 246, 0.5);
            box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
        }
        
        /* Charts with glassmorphism */
        .stBarChart, .stLineChart, .stAreaChart {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 0.75rem;
            padding: 1rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
        }
        
        /* Form styling with glassmorphism */
        .stForm {
            background: rgba(30, 41, 59, 0.3);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-radius: 0.75rem;
            padding: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        /* Column styling */
        [data-testid="column"] {
            padding: 0.5rem;
        }
        
        /* Custom header with glassmorphism and glowing shield */
        .dashboard-header {
            text-align: center;
            padding: 3rem 2rem;
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 1rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(148, 163, 184, 0.1);
            box-shadow: 
                0 8px 32px 0 rgba(0, 0, 0, 0.37),
                inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
            position: relative;
        }
        
        .shield-icon-container {
            position: relative;
            display: inline-block;
            margin-bottom: 1.5rem;
        }
        
        .shield-icon {
            font-size: 4rem;
            color: #60a5fa;
            filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.8))
                    drop-shadow(0 0 40px rgba(59, 130, 246, 0.5));
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.8))
                        drop-shadow(0 0 40px rgba(59, 130, 246, 0.5));
            }
            to {
                filter: drop-shadow(0 0 30px rgba(59, 130, 246, 1))
                        drop-shadow(0 0 60px rgba(59, 130, 246, 0.7));
            }
        }
        
        .shield-glow-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 120px;
            height: 120px;
            border: 2px solid rgba(59, 130, 246, 0.3);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% {
                transform: translate(-50%, -50%) scale(1);
                opacity: 1;
            }
            50% {
                transform: translate(-50%, -50%) scale(1.2);
                opacity: 0.5;
            }
        }
        
        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 20px rgba(59, 130, 246, 0.5);
        }
        
        .dashboard-subtitle {
            font-size: 1.1rem;
            color: #94a3b8;
            line-height: 1.6;
        }
        
        /* Table styling */
        table {
            color: #e2e8f0 !important;
        }
        
        thead tr th {
            background: rgba(51, 65, 85, 0.6) !important;
            backdrop-filter: blur(8px);
            color: #f1f5f9 !important;
            border-color: rgba(148, 163, 184, 0.2) !important;
            text-transform: uppercase;
            font-size: 0.875rem;
            letter-spacing: 0.05em;
        }
        
        tbody tr {
            background: rgba(30, 41, 59, 0.3) !important;
            border-color: rgba(148, 163, 184, 0.1) !important;
            transition: all 0.2s ease;
        }
        
        tbody tr:hover {
            background: rgba(51, 65, 85, 0.5) !important;
        }
        
        /* Section headers with icons */
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
        }
        
        .section-icon {
            font-size: 1.5rem;
            color: #60a5fa;
            filter: drop-shadow(0 2px 8px rgba(59, 130, 246, 0.5));
        }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state variables
def init_session() -> None:
    # Authentication state
    if "auth" not in st.session_state:
        st.session_state.auth = {"logged_in": False, "user": None}
    # GDPR consent state
    if "consent" not in st.session_state:
        st.session_state.consent = False
    # Last data sync timestamp
    if "last_sync" not in st.session_state:
        st.session_state.last_sync = None

# Render login form with GDPR consent
def render_login() -> None:
    # Custom header with glowing shield icon
    st.markdown("""
    <div class="dashboard-header">
        <div class="shield-icon-container">
            <div class="shield-glow-ring"></div>
            <i class="fas fa-shield-halved shield-icon"></i>
        </div>
        <div class="dashboard-title">Privacy-Centric Hospital Dashboard</div>
        <div class="dashboard-subtitle">Built to demonstrate GDPR, CIA triad controls, and privacy engineering</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(
        """
        **GDPR Privacy Notice**
        
        This demo processes synthetic patient data. Access is logged and restricted per role.
        By continuing you consent to lawful, fair, and transparent processing.
        """
    )
    # GDPR consent checkbox
    st.session_state.consent = st.checkbox(
        "I acknowledge the GDPR privacy notice and acceptable use policy.",
        value=st.session_state.get("consent", False),
    )
    # Login form
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign in", disabled=not st.session_state.consent)
        # Handle login submission
        if submitted:
            try:
                user = get_user_by_username(username.strip())
            except Exception as exc:
                st.error(f"Unable to reach the identity service: {exc}")
                return
            if not user or not verify_password(password, user["password"]):
                log_action(None, "unauthorized", "login_failed", f"username={username}")
                st.error("Invalid credentials or access denied.")
                return
            # Successful login
            st.session_state.auth = {"logged_in": True, "user": user}
            log_action(user["user_id"], user["role"], "login", "Successful authentication")
            st.success("Login successful. Redirecting...")
            st.rerun()

# Logout function with logging
def logout() -> None:
    # Log the logout action
    auth = st.session_state.get("auth")
    if auth and auth.get("logged_in"):
        # Log the logout action
        user = auth.get("user")
        log_action(user.get("user_id"), user.get("role"), "logout", "User initiated logout")
    st.session_state.auth = {"logged_in": False, "user": None}
    st.rerun()

@st.cache_data(ttl=60) # Cache patient data for 60 seconds

# Cached fetch of patient records
def cached_patients(include_sensitive: bool) -> List[dict]:
    records = fetch_patients(include_sensitive=include_sensitive)
    return records

# Render operational overview with metrics and visualizations
def render_overview(role: str) -> List[dict]:
    st.markdown('<div class="section-header"><i class="fas fa-chart-line section-icon"></i><h2 style="margin:0;">Operational Overview</h2></div>', unsafe_allow_html=True)
    # Fetch patient data based on role
    include_sensitive = role == "admin"
    try:
        patients = cached_patients(include_sensitive)
        st.session_state.last_sync = datetime.utcnow()
    except Exception as exc:
        st.error(f"Unable to load patients: {exc}")
        return []

    total_patients = patient_count()
    
    # Metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:# Display total registered patients
        st.metric("Registered Patients", total_patients)
    with col2:# Display last data sync time
        st.metric(
            "Data Last Synced",
            (st.session_state.last_sync or datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S"),
        )
    with col3:# Display system uptime
        st.metric(
            "System Uptime",
            str(datetime.utcnow() - APP_START).split(".")[0],
        )

    if role == "admin":# Admin-specific controls and data access
        st.success("Admin access: raw + anonymized datasets available.")
        col1, col2 = st.columns(2)
        if col1.button("Refresh Anonymized Fields"):# Button to refresh anonymized data
            try:
                refresh_anonymized_fields()# Clear cache and log action
                cached_patients.clear()# Clear cached patient data

                log_action(current_user_id(), role, "reanonymize", "Full refresh triggered")
                st.success("Anonymized fields updated.")
                st.rerun()
            except Exception as exc:
                st.error(f"Unable to refresh anonymized data: {exc}")
        
        with col2:# Provide patient data download option
            df = pd.DataFrame(patients)
            csv = df.to_csv(index=False).encode("utf-8")
            downloaded = st.download_button(
                "Download Patient Backup (CSV)",
                csv,
                file_name="patient_backup.csv",
                mime="text/csv",
            )
            if downloaded:
                log_action(current_user_id(), role, "export", "Downloaded patient backup")

    display_retention_summary(patients)# Show data retention summary
    display_activity_viz(role)# Show activity visualizations
    return patients


def display_retention_summary(patients: List[dict]) -> None:# Show data retention summary
    if not patients:
        return
    # Identify stale records beyond retention period
    retention_limit = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    # Filter patients added before retention limit
    stale = [p for p in patients if datetime.fromisoformat(p["date_added"]) < retention_limit]
    # Display in expandable section
    with st.expander(f"Data Retention Monitor ({len(stale)} records require review)"):
        st.write(
            f"Records expire after {RETENTION_DAYS} days. {len(stale)} record(s) require review."
        )
        if stale:
            st.table(
                # Display stale records in a table
                pd.DataFrame(
                    [
                        {
                            "Patient": p.get("anonymized_name", p.get("name", "")),
                            "Added": p["date_added"],
                        }
                        for p in stale
                    ]
                )
            )

# Enhanced activity visualization with multiple charts
def display_activity_viz(role: str) -> None:# Show activity visualizations
    """Enhanced activity visualization with multiple charts"""
    if role != "admin":
        st.info("Activity visualization limited to admin role.")
        return
    
    st.markdown('<div class="section-header"><i class="fas fa-chart-bar section-icon"></i><h2 style="margin:0;">System Analytics & Activity Insights</h2></div>', unsafe_allow_html=True)
    
    try:
        # Fetch all logs for comprehensive analysis
        all_logs = fetch_logs(limit=1000)
        
        if not all_logs:
            st.warning("No activity logs available yet.")
            return
        
        logs_df = pd.DataFrame(all_logs)
        logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'])
        
        # Get daily activity stats
        log_stats = fetch_log_counts_by_day()
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📉 Daily Trend", 
            "🔐 Action Types", 
            "👥 User Roles", 
            "🕐 Hourly Pattern",
            "📋 Activity Summary"
        ])
        # Daily activity trend
        with tab1:
            st.markdown("### Daily Activity Trend")
            if log_stats:
                df_daily = pd.DataFrame(log_stats)
                df_daily["day"] = pd.to_datetime(df_daily["day"])
                st.area_chart(df_daily.set_index("day")["total"], use_container_width=True)
                
                # Quick stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Actions", df_daily["total"].sum())
                with col2:
                    st.metric("Peak Day", df_daily["total"].max())
                with col3:
                    avg_daily = df_daily["total"].mean()
                    st.metric("Avg Daily", f"{avg_daily:.1f}")
            else:
                st.info("Insufficient data for daily trends.")
        
        with tab2:
            st.markdown("### Action Type Distribution")
            
            # Count actions by type
            action_counts = logs_df['action'].value_counts().reset_index()
            action_counts.columns = ['Action', 'Count']
            
            # Display as bar chart
            st.bar_chart(action_counts.set_index('Action'), use_container_width=True)
            
            # Display detailed table
            st.markdown("#### Detailed Breakdown")
            
            # Add percentage column
            action_counts['Percentage'] = (action_counts['Count'] / action_counts['Count'].sum() * 100).round(2)
            action_counts['Percentage'] = action_counts['Percentage'].astype(str) + '%'
            
            st.dataframe(action_counts, use_container_width=True, hide_index=True)
            
            # Most common action
            most_common = action_counts.iloc[0]
            st.info(f"🏆 Most common action: **{most_common['Action']}** ({most_common['Count']} times)")
        
        with tab3:
            st.markdown("### Activity by User Role")
            
            # Count actions by role
            role_counts = logs_df['role'].value_counts().reset_index()
            role_counts.columns = ['Role', 'Actions']
            
            # Display as bar chart
            st.bar_chart(role_counts.set_index('Role'), use_container_width=True)
            
            # Role activity breakdown
            st.markdown("#### Role Activity Details")
            
            # Calculate percentages
            role_counts['Percentage'] = (role_counts['Actions'] / role_counts['Actions'].sum() * 100).round(2)
            role_counts['Percentage'] = role_counts['Percentage'].astype(str) + '%'
            
            # Display table
            st.dataframe(role_counts, use_container_width=True, hide_index=True)
            
            # Most active role
            most_active = role_counts.iloc[0]
            st.success(f"👤 Most active role: **{most_active['Role']}** ({most_active['Actions']} actions)")
            
            # Cross-tab: Role vs Action Type
            st.markdown("#### Role vs Action Cross-Analysis")
            role_action_pivot = pd.crosstab(logs_df['role'], logs_df['action'])
            st.dataframe(role_action_pivot, use_container_width=True)
        
        with tab4:
            st.markdown("### Hourly Activity Pattern")
            
            # Extract hour from timestamp
            logs_df['hour'] = logs_df['timestamp'].dt.hour
            hourly_counts = logs_df.groupby('hour').size().reset_index(name='count')
            
            # Ensure all 24 hours are represented
            all_hours = pd.DataFrame({'hour': range(24)})
            hourly_counts = all_hours.merge(hourly_counts, on='hour', how='left').fillna(0)
            hourly_counts['count'] = hourly_counts['count'].astype(int)
            
            # Display line chart
            st.line_chart(hourly_counts.set_index('hour')['count'], use_container_width=True)
            
            # Peak hours
            peak_hour = hourly_counts.loc[hourly_counts['count'].idxmax()]
            st.info(f"⏰ Peak activity hour: **{int(peak_hour['hour'])}:00** ({int(peak_hour['count'])} actions)")
            
            # Business hours vs off-hours
            business_hours = hourly_counts[(hourly_counts['hour'] >= 9) & (hourly_counts['hour'] <= 17)]
            off_hours = hourly_counts[(hourly_counts['hour'] < 9) | (hourly_counts['hour'] > 17)]
            # Compare activity during business hours and off-hours
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Business Hours (9-17)", int(business_hours['count'].sum()))
            with col2:
                st.metric("Off Hours", int(off_hours['count'].sum()))
        # Activity summary and insights
        with tab5:
            st.markdown("### Activity Summary & Insights")
            
            # Overall statistics
            col1, col2, col3, col4 = st.columns(4)
            # Total events
            with col1:
                st.metric("Total Events", len(logs_df))
            # Unique users
            with col2:
                unique_users = logs_df['user_id'].nunique()
                st.metric("Active Users", unique_users)
            # Unique action types
            with col3:
                unique_actions = logs_df['action'].nunique()
                st.metric("Action Types", unique_actions)
            # Active days
            with col4:
                # Calculate days with activity
                days_active = logs_df['timestamp'].dt.date.nunique()
                st.metric("Active Days", days_active)
            # Divider
            st.divider()
            
            # Recent activity timeline
            st.markdown("#### Recent Activity Timeline")
            recent_logs = logs_df.sort_values('timestamp', ascending=False).head(15)
            
            # Format for display
            display_logs = recent_logs[['timestamp', 'role', 'action', 'details']].copy()
            display_logs['timestamp'] = display_logs['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(display_logs, use_container_width=True, hide_index=True)
            
            # Security insights
            st.markdown("#### Security Insights")
            
            # Check for failed logins
            failed_logins = logs_df[logs_df['action'] == 'login_failed']
            unauthorized_attempts = logs_df[logs_df['role'] == 'unauthorized']
            # Display security-related metrics
            col1, col2 = st.columns(2)
            with col1:
                if len(failed_logins) > 0:
                    st.warning(f"⚠️ {len(failed_logins)} failed login attempts detected")
                else:
                    st.success("✅ No failed login attempts")
            
            with col2:
                if len(unauthorized_attempts) > 0:
                    st.warning(f"⚠️ {len(unauthorized_attempts)} unauthorized access attempts")
                else:
                    st.success("✅ No unauthorized access attempts")
            
            # Data modification tracking
            modifications = logs_df[logs_df['action'].isin(['add_patient', 'update_patient', 'delete_patient'])]
            st.info(f"📝 Total data modifications: **{len(modifications)}**")
            
    except Exception as exc:
        st.error(f"Unable to generate visualizations: {exc}")

# Render patient registry section with role-based access
def render_patients_section(role: str, patients: List[dict]) -> None:
    st.markdown('<div class="section-header"><i class="fas fa-hospital-user section-icon"></i><h2 style="margin:0;">Patient Registry</h2></div>', unsafe_allow_html=True)
    if not patients:
        st.warning("No patient data available.")
        return
    # View mode selection for admins
    view_mode = "Anonymized"# Default to anonymized view
    if role == "admin":# Allow admins to toggle view mode
        view_mode = st.radio("Select view", ["Anonymized", "Raw"], horizontal=True)
    # Display patient data based on view mode and role
    df = pd.DataFrame(patients)
    if view_mode == "Anonymized" or role != "admin":
        display_cols = [
            "patient_id",
            "anonymized_name",
            "anonymized_contact",
            "anonymized_diagnosis",
            "date_added",
        ]
    else:
        display_cols = [
            "patient_id",
            "name",
            "contact",
            "diagnosis",
            "date_added",
        ]
    # Highlight sensitive columns for admins
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    # Data modification section for admins and receptionists
    if role in {"admin", "receptionist"}:
        st.markdown('<div class="section-header"><i class="fas fa-edit section-icon"></i><h3 style="margin:0;">Intake / Update</h3></div>', unsafe_allow_html=True)
        with st.expander("Add New Patient", expanded=False):
            with st.form("add_patient"):
                name = st.text_input("Full Name", placeholder="John Doe")
                contact = st.text_input("Contact", help="E.g., +1-555-123-4567", placeholder="+1-555-123-4567")
                diagnosis = st.text_area("Diagnosis", placeholder="Enter diagnosis details...")
                submitted = st.form_submit_button("Add Patient")
                if submitted:
                    if not (name and contact and diagnosis):
                        st.error("All fields are required.")
                    else:
                        try:
                            # Insert new patient record
                            pid = insert_patient(name.strip(), contact.strip(), diagnosis.strip())
                            log_action(
                                current_user_id(),
                                role,
                                "add_patient",
                                f"patient_id={pid}",
                            )
                            cached_patients.clear()
                            st.success(f"Patient record {pid} created securely.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Unable to add patient: {exc}")
        # Update patient records
        with st.expander("Update Patient", expanded=False):
            if not patients:
                st.info("No patients to update.")
            else:
                # Select patient record to update
                options = {f"{p['anonymized_name']} (ID {p['patient_id']})": p["patient_id"] for p in patients}
                selection = st.selectbox("Select record", list(options.keys()))
                new_contact = st.text_input("New Contact", placeholder="Leave blank to keep current")
                new_diagnosis = st.text_input("New Diagnosis", placeholder="Leave blank to keep current")
                if st.button("Apply Update", type="primary"):
                    if not new_contact and not new_diagnosis:
                        st.warning("Provide at least one field to update.")
                    else:
                        try:
                            update_patient(
                                options[selection],
                                contact=new_contact or None,
                                diagnosis=new_diagnosis or None,
                            )
                            log_action(
                                current_user_id(),
                                role,
                                "update_patient",
                                f"patient_id={options[selection]}",
                            )
                            cached_patients.clear()
                            st.success("Record updated and re-masked.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Unable to update patient: {exc}")
        # Delete patient records
        with st.expander("Delete Patient (Irreversible)", expanded=False):
            if not patients:
                st.info("No patients to delete.")
            else:
                st.warning("⚠️ Deletion is permanent and cannot be undone. This action will be logged for audit purposes.")
                options = {f"{p['anonymized_name']} (ID {p['patient_id']})": p["patient_id"] for p in patients}
                selection = st.selectbox("Select record to delete", list(options.keys()), key="delete_select")
                
                # Confirmation checkbox
                confirm = st.checkbox("I confirm this record should be permanently deleted.")
                # Delete button
                if st.button("Delete Record", type="secondary", disabled=not confirm):
                    try:
                        patient_id = options[selection]
                        delete_patient(patient_id)
                        log_action(
                            current_user_id(),
                            role,
                            "delete_patient",
                            f"patient_id={patient_id}, anonymized_name={selection.split(' (ID')[0]}",
                        )
                        cached_patients.clear()
                        st.success(f"Patient record {patient_id} has been permanently deleted. Action logged for GDPR accountability.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Unable to delete patient: {exc}")
    # Info for doctors about data edits
    if role == "doctor":
        st.info("Doctors can request admin assistance for data edits to maintain integrity.")

# Render audit log section for administrators
def render_audit_section(role: str) -> None:
    if role != "admin":
        st.warning("Audit logs restricted to administrators.")
        return
    st.markdown('<div class="section-header"><i class="fas fa-clipboard-check section-icon"></i><h2 style="margin:0;">Integrity Audit Log</h2></div>', unsafe_allow_html=True)
    try:
        # Fetch audit logs
        logs = fetch_logs(limit=250)
    except Exception as exc:
        st.error(f"Unable to fetch logs: {exc}")
        return
    df = pd.DataFrame(logs)
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "Export Logs (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="audit_logs.csv",
        mime="text/csv",
    )
    log_action(current_user_id(), role, "view_logs", "Admin reviewed audit trail")

# Helper to get current user ID
def current_user_id() -> int:
    return st.session_state.auth.get("user", {}).get("user_id")

# Main application function
def main() -> None:
    st.set_page_config(
        page_title="GDPR Hospital Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon="🛡️"
    )
    
    # Apply dark theme
    apply_dark_theme()
    
    # Initialize database and session
    init_db()
    init_session()
    if not st.session_state.auth["logged_in"]:# Render login if not authenticated
        render_login()
        return

    user = st.session_state.auth["user"]
    role = user["role"]
    # Sidebar navigation
    st.sidebar.markdown('<div class="section-header"><i class="fas fa-bars section-icon"></i><h1 style="margin:0; font-size:1.5rem;">Navigation</h1></div>', unsafe_allow_html=True)
    st.sidebar.success(f"Signed in as **{user['username']}** ({role})")
    if st.sidebar.button("Log out"):
        logout()

    nav_options = ["Overview", "Patients"]
    if role == "admin":
        nav_options.append("Audit")
    section = st.sidebar.radio("Workspace", nav_options)

    st.sidebar.divider()
    # Sidebar uptime and last sync info
    st.sidebar.caption(
        f"System uptime: {str(datetime.utcnow() - APP_START).split('.')[0]}\n\n"
        f"Last sync: {(st.session_state.last_sync or datetime.utcnow()).strftime('%H:%M:%S UTC')}"
    )

    patients = []
    # Render selected section
    if section == "Overview":
        patients = render_overview(role)
    elif section == "Patients":
        include_sensitive = role == "admin"
        patients = cached_patients(include_sensitive)
        render_patients_section(role, patients)
    elif section == "Audit":
        render_audit_section(role)

    st.divider()
    # Footer with GDPR and uptime info
    st.caption(
        " | ".join(
            [
                "GDPR controls demo",
                f"System uptime: {str(datetime.utcnow() - APP_START).split('.')[0]}",
                f"Last sync: {(st.session_state.last_sync or datetime.utcnow()).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                "Availability ensured via graceful error handling and export backups",
            ]
        )
    )

# Run the application
if __name__ == "__main__":
    main()