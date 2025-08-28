"""
Lumen Workshop Strategic Initiative Dashboard
Apple Design Language - Clean, Minimal, Functional
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import hashlib
import base64
import json
import io
import sqlite3
from pathlib import Path
import os
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Lumen Strategic Dashboard",
    page_icon="⊙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database configuration
DB_PATH = "lumen_dashboard.db"

# Apple-inspired CSS styling
def load_css():
    st.markdown("""
    <style>
    /* Import SF Pro Display font (Apple's system font fallback) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles - Apple Design Language */
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', 'Helvetica Neue', sans-serif;
    }
    
    .main {
        padding: 0;
        background: #ffffff;
        min-height: 100vh;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Header - Apple Style */
    .dashboard-header {
        background: linear-gradient(180deg, #000000 0%, #1d1d1f 100%);
        color: #ffffff;
        padding: 2rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-bottom: 1px solid #424245;
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        background: linear-gradient(180deg, #ffffff 0%, #86868b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        color: #86868b;
        font-size: 1.125rem;
        font-weight: 400;
    }
    
    /* Card Styles - Apple Style */
    .metric-card {
        background: #ffffff;
        border: 1px solid #d2d2d7;
        padding: 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        transform: translateY(-2px);
    }
    
    /* Matrix Container - Clean Design */
    .matrix-wrapper {
        background: #ffffff;
        border: 1px solid #d2d2d7;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.04);
        position: relative;
        margin: 1rem 0;
    }
    
    /* Buttons - Apple Style */
    .stButton > button {
        background: #000000;
        color: #ffffff;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        font-size: 0.9375rem;
        letter-spacing: -0.01em;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
    }
    
    .stButton > button:hover {
        background: #1d1d1f;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.16);
        transform: translateY(-1px);
    }
    
    /* Secondary Button Style */
    .secondary-button {
        background: #f5f5f7 !important;
        color: #000000 !important;
        border: 1px solid #d2d2d7 !important;
    }
    
    .secondary-button:hover {
        background: #e8e8ed !important;
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background: #ffffff;
        padding: 1.25rem;
        border: 1px solid #d2d2d7;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transform: translateY(-1px);
    }
    
    div[data-testid="metric-container"] label {
        color: #86868b;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        color: #1d1d1f;
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Sidebar Styling - Dark Mode */
    section[data-testid="stSidebar"] {
        background: #1d1d1f;
        border-right: 1px solid #424245;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #ffffff;
        font-weight: 400;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.12);
    }
    
    /* Tab Styling - Apple Style */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 0;
        padding: 0;
        border-bottom: 1px solid #d2d2d7;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #86868b;
        border: none;
        padding: 1rem 1.5rem;
        font-weight: 500;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        border-bottom: 2px solid transparent;
        letter-spacing: -0.01em;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #1d1d1f;
    }
    
    .stTabs [aria-selected="true"] {
        color: #000000;
        border-bottom: 2px solid #000000;
        background: transparent;
    }
    
    /* Forms - Apple Style */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 0.5rem;
        border: 1px solid #d2d2d7;
        padding: 0.75rem;
        font-size: 0.9375rem;
        transition: all 0.2s ease;
        background: #ffffff;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #0071e3;
        box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
        outline: none;
    }
    
    /* Sliders - Apple Style */
    .stSlider > div > div > div {
        background: #d2d2d7;
    }
    
    .stSlider > div > div > div > div {
        background: #000000;
    }
    
    /* Expander - Apple Style */
    .streamlit-expanderHeader {
        background: #f5f5f7;
        border: 1px solid #d2d2d7;
        border-radius: 0.5rem;
        padding: 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #e8e8ed;
    }
    
    /* Activity Feed - Clean Design */
    .activity-item {
        background: #ffffff;
        border: 1px solid #d2d2d7;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid;
        transition: all 0.2s ease;
    }
    
    .activity-item:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        transform: translateX(2px);
    }
    
    .activity-item.create {
        border-left-color: #34c759;
    }
    
    .activity-item.update {
        border-left-color: #007aff;
    }
    
    .activity-item.delete {
        border-left-color: #ff3b30;
    }
    
    .activity-item.move {
        border-left-color: #5856d6;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 0.5rem;
        border: 1px solid #d2d2d7;
    }
    
    /* Selectbox */
    div[data-baseweb="select"] {
        border-radius: 0.5rem;
    }
    
    /* Remove all remaining rounded corners */
    * {
        border-radius: 0.5rem !important;
    }
    
    /* Data tables */
    .dataframe {
        border: 1px solid #d2d2d7 !important;
        font-size: 0.875rem;
    }
    
    .dataframe thead tr th {
        background: #f5f5f7 !important;
        color: #1d1d1f !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
    }
    
    /* Success/Error/Warning/Info Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 0.5rem;
    }
    
    /* Plotly Chart Styling */
    .js-plotly-plot {
        border: 1px solid #d2d2d7;
        border-radius: 0.5rem;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# Create Interactive Plotly Matrix with Draggable Points
def create_interactive_matrix():
    """Create an interactive matrix using Plotly with individually draggable points"""
    
    df = get_initiatives_from_db()
    
    fig = go.Figure()
    
    # Add quadrant backgrounds with Apple-style colors
    shapes = [
        # Quick Wins (top-left) - Green tint
        dict(type="rect", x0=0, y0=66.66, x1=50, y1=100,
             fillcolor="rgba(52, 199, 89, 0.05)", line=dict(width=0)),
        # Strategic (top-right) - Blue tint
        dict(type="rect", x0=50, y0=66.66, x1=100, y1=100,
             fillcolor="rgba(0, 122, 255, 0.05)", line=dict(width=0)),
        # Low Priority (bottom-left) - Gray tint
        dict(type="rect", x0=0, y0=0, x1=50, y1=33.33,
             fillcolor="rgba(142, 142, 147, 0.05)", line=dict(width=0)),
        # Consider (bottom-right) - Orange tint
        dict(type="rect", x0=50, y0=0, x1=100, y1=33.33,
             fillcolor="rgba(255, 149, 0, 0.05)", line=dict(width=0))
    ]
    
    # Add grid lines - thin and subtle
    shapes.extend([
        dict(type="line", x0=0, y0=33.33, x1=100, y1=33.33,
             line=dict(color="#d2d2d7", width=1)),
        dict(type="line", x0=0, y0=66.66, x1=100, y1=66.66,
             line=dict(color="#d2d2d7", width=1)),
        dict(type="line", x0=50, y0=0, x1=50, y1=100,
             line=dict(color="#d2d2d7", width=1))
    ])
    
    if not df.empty:
        # Apple-style color mapping
        color_map = {
            "pink": "#ff3b30",    # Red
            "yellow": "#ffcc00",   # Yellow
            "green": "#34c759",    # Green
            "blue": "#007aff"      # Blue
        }
        
        # Create editable scatter plot
        fig.add_trace(go.Scatter(
            x=df['x'].tolist(),
            y=df['y'].tolist(),
            mode='markers+text',
            marker=dict(
                size=50,
                color=[color_map.get(c, '#8e8e93') for c in df['color'].tolist()],
                line=dict(width=2, color='white'),
                opacity=0.95
            ),
            text=[t[:15] + '...' if len(t) > 15 else t for t in df['title'].tolist()],
            textposition="middle center",
            textfont=dict(size=10, color='white', family='-apple-system, BlinkMacSystemFont', weight=500),
            hovertemplate=[
                f"<b>{row['title']}</b><br>"
                f"{row['details']}<br>"
                f"<br>Category: {row['category']}"
                f"<br>Value: {row['value']}"
                f"<br>Effort: {row['effort']}"
                f"<br>Last updated: {row['updated_by']}"
                "<extra></extra>"
                for _, row in df.iterrows()
            ],
            customdata=df[['id', 'title', 'details', 'category', 'color']].values.tolist(),
            showlegend=False
        ))
    
    # Update layout with Apple design language
    fig.update_layout(
        xaxis=dict(
            title="<b>Effort →</b>",
            range=[-5, 105],
            tickmode='array',
            tickvals=[0, 50, 100],
            ticktext=['Low', 'Medium', 'High'],
            showgrid=False,
            zeroline=False,
            tickfont=dict(family='-apple-system', size=12, color='#86868b')
        ),
        yaxis=dict(
            title="<b>Value →</b>",
            range=[-5, 105],
            tickmode='array',
            tickvals=[0, 33.33, 66.66, 100],
            ticktext=['Low', 'Medium', 'Medium', 'High'],
            showgrid=False,
            zeroline=False,
            tickfont=dict(family='-apple-system', size=12, color='#86868b')
        ),
        shapes=shapes,
        annotations=[
            dict(text="<b>QUICK WINS</b>", x=25, y=85, showarrow=False, 
                 font=dict(size=12, color="#34c759", family='-apple-system')),
            dict(text="<b>STRATEGIC</b>", x=75, y=85, showarrow=False, 
                 font=dict(size=12, color="#007aff", family='-apple-system')),
            dict(text="<b>LOW PRIORITY</b>", x=25, y=15, showarrow=False, 
                 font=dict(size=12, color="#8e8e93", family='-apple-system')),
            dict(text="<b>CONSIDER</b>", x=75, y=15, showarrow=False, 
                 font=dict(size=12, color="#ff9500", family='-apple-system'))
        ],
        height=700,
        hovermode='closest',
        dragmode='select',  # Allow selecting points
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=60, r=20, t=20, b=60),
        font=dict(family='-apple-system, BlinkMacSystemFont')
    )
    
    # Enable editable mode for dragging points
    config = {
        'editable': True,
        'edits': {
            'shapePosition': True,
            'annotationPosition': False
        },
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
        'modeBarButtonsToAdd': []
    }
    
    return fig, config

# Database functions (keep existing ones and add these)
def update_position(id, x, y, user="user"):
    """Update only the position of an initiative"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    value = get_value_from_position(y)
    effort = get_effort_from_position(x)
    
    c.execute('''
        UPDATE initiatives 
        SET x = ?, y = ?, value = ?, effort = ?, 
            updated_at = CURRENT_TIMESTAMP, updated_by = ?
        WHERE id = ?
    ''', (x, y, value, effort, user, id))
    
    # Log the action
    c.execute("SELECT title FROM initiatives WHERE id = ?", (id,))
    title = c.fetchone()[0]
    log_action(conn, "MOVE", id, title, user, f"Moved initiative to ({x:.1f}, {y:.1f})")
    
    conn.commit()
    conn.close()

# Keep all existing database functions from previous version
def init_database():
    """Initialize the database with tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create initiatives table
    c.execute('''
        CREATE TABLE IF NOT EXISTS initiatives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            details TEXT,
            color TEXT,
            category TEXT,
            x REAL,
            y REAL,
            value TEXT,
            effort TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            is_deleted BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create audit log table
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            initiative_id INTEGER,
            initiative_title TEXT,
            user TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create sessions table for authentication
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logout_time TIMESTAMP,
            ip_address TEXT
        )
    ''')
    
    # Check if we need to populate with default data
    c.execute("SELECT COUNT(*) FROM initiatives WHERE is_deleted = 0")
    count = c.fetchone()[0]
    
    if count == 0:
        # Insert default initiatives
        default_initiatives = load_default_initiatives()
        for init in default_initiatives:
            c.execute('''
                INSERT INTO initiatives (title, details, color, category, x, y, value, effort, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (init['title'], init['details'], init['color'], init['category'], 
                  init['x'], init['y'], init['value'], init['effort'], 'system'))
    
    conn.commit()
    conn.close()

def load_default_initiatives():
    """Load default initiative data"""
    return [
        {"title": "Prioritize CommMgmt Strategy", "details": "Establish clear communication management strategy and framework", 
         "color": "pink", "category": "Strategic/Process", "x": 10, "y": 15, "value": "High", "effort": "Low"},
        {"title": "Strategic Direction", "details": "Define clear strategic direction for technology investments", 
         "color": "blue", "category": "People/Organization", "x": 5, "y": 20, "value": "High", "effort": "Low"},
        {"title": "Cannot 'justify' tech invest", "details": "Need framework to justify and measure ROI on technology investments", 
         "color": "green", "category": "Technology/Platform", "x": 20, "y": 10, "value": "High", "effort": "Low"},
        {"title": "No prioritization marketing", "details": "Implement marketing prioritization framework", 
         "color": "green", "category": "Technology/Platform", "x": 15, "y": 25, "value": "High", "effort": "Low"},
        {"title": "Do I have right people in roles", "details": "Skills assessment and organizational alignment needed", 
         "color": "blue", "category": "People/Organization", "x": 25, "y": 18, "value": "High", "effort": "Low"},
        {"title": "Back to Shots - CJA", "details": "Return to basic CJA implementation", 
         "color": "yellow", "category": "Quick Implementation", "x": 8, "y": 30, "value": "High", "effort": "Low"},
        {"title": "Build hurdling warehouse", "details": "Create comprehensive data warehouse solution", 
         "color": "pink", "category": "Strategic/Process", "x": 45, "y": 8, "value": "High", "effort": "Medium"},
        {"title": "Align tools vs Campaign Member", "details": "Align technology tools with campaign member needs", 
         "color": "yellow", "category": "Quick Implementation", "x": 40, "y": 25, "value": "High", "effort": "Medium"},
        {"title": "Marketing Activity Data", "details": "Migrate marketing activity data to specific roles", 
         "color": "pink", "category": "Strategic/Process", "x": 50, "y": 15, "value": "High", "effort": "Medium"},
        {"title": "Campaign Orchestration", "details": "No scale view of complete campaign activity - need comprehensive tracking", 
         "color": "pink", "category": "Strategic/Process", "x": 65, "y": 10, "value": "High", "effort": "High"}
    ]

def get_initiatives_from_db():
    """Fetch all active initiatives from database"""
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, title, details, color, category, x, y, value, effort, 
               created_at, updated_at, created_by, updated_by
        FROM initiatives 
        WHERE is_deleted = 0
        ORDER BY id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def add_initiative_to_db(title, details, color, category, x, y, user="user"):
    """Add new initiative to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    value = get_value_from_position(y)
    effort = get_effort_from_position(x)
    
    c.execute('''
        INSERT INTO initiatives (title, details, color, category, x, y, value, effort, created_by, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, details, color, category, x, y, value, effort, user, user))
    
    initiative_id = c.lastrowid
    
    # Log the action
    log_action(conn, "CREATE", initiative_id, title, user, f"Created new initiative: {title}")
    
    conn.commit()
    conn.close()
    return initiative_id

def update_initiative_in_db(id, title, details, x, y, user="user"):
    """Update existing initiative in database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    value = get_value_from_position(y)
    effort = get_effort_from_position(x)
    
    c.execute('''
        UPDATE initiatives 
        SET title = ?, details = ?, x = ?, y = ?, value = ?, effort = ?, 
            updated_at = CURRENT_TIMESTAMP, updated_by = ?
        WHERE id = ?
    ''', (title, details, x, y, value, effort, user, id))
    
    # Log the action
    log_action(conn, "UPDATE", id, title, user, f"Updated initiative: {title}")
    
    conn.commit()
    conn.close()

def delete_initiative_from_db(id, title, user="user"):
    """Soft delete initiative from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        UPDATE initiatives 
        SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP, updated_by = ?
        WHERE id = ?
    ''', (user, id))
    
    # Log the action
    log_action(conn, "DELETE", id, title, user, f"Deleted initiative: {title}")
    
    conn.commit()
    conn.close()

def log_action(conn, action, initiative_id, initiative_title, user, details):
    """Log action to audit table"""
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_log (action, initiative_id, initiative_title, user, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (action, initiative_id, initiative_title, user, details))

def get_audit_log(limit=50):
    """Fetch recent audit log entries"""
    conn = sqlite3.connect(DB_PATH)
    query = f"""
        SELECT action, initiative_title, user, details, timestamp
        FROM audit_log
        ORDER BY timestamp DESC
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def reset_database():
    """Reset database to default state"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Soft delete all current initiatives
    c.execute("UPDATE initiatives SET is_deleted = 1 WHERE is_deleted = 0")
    
    # Insert default initiatives
    default_initiatives = load_default_initiatives()
    for init in default_initiatives:
        c.execute('''
            INSERT INTO initiatives (title, details, color, category, x, y, value, effort, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (init['title'], init['details'], init['color'], init['category'], 
              init['x'], init['y'], init['value'], init['effort'], 'system'))
    
    # Log the reset
    c.execute('''
        INSERT INTO audit_log (action, user, details)
        VALUES (?, ?, ?)
    ''', ('RESET', 'system', 'Database reset to default state'))
    
    conn.commit()
    conn.close()

# Authentication functions
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'auth_attempts' not in st.session_state:
        st.session_state.auth_attempts = 0
    if 'locked_until' not in st.session_state:
        st.session_state.locked_until = None
    if 'username' not in st.session_state:
        st.session_state.username = "user"

def check_authentication(password):
    """Check if the provided password is correct"""
    correct_password = base64.b64decode('THVtZW5EYXNoMjAyNSE=').decode()
    return password == correct_password

def get_value_from_position(y):
    """Convert Y position to value category"""
    if y < 33:
        return "High"
    elif y < 66:
        return "Medium"
    return "Low"

def get_effort_from_position(x):
    """Convert X position to effort category"""
    if x < 33:
        return "Low"
    elif x < 66:
        return "Medium"
    return "High"

def get_quadrant(x, y):
    """Determine quadrant based on position"""
    if y < 33 and x < 50:
        return "Quick Wins"
    elif y < 33 and x >= 50:
        return "Strategic Investments"
    elif y >= 66:
        return "Low Priority"
    return "Consider Carefully"

def show_login():
    """Display modern login form"""
    load_css()
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 3rem; border-radius: 20px; box-shadow: 0 20px 60px rgba(0,0,0,0.1); margin-top: 5rem;'>
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1 style='color: #1a1a2e; margin-bottom: 0.5rem;'>Welcome to Lumen</h1>
                <p style='color: #64748b;'>Strategic Initiative Dashboard</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", value="user", key="username_input")
            password = st.text_input("Password", type="password", key="password_input")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if check_authentication(password):
                    st.session_state.authenticated = True
                    st.session_state.username = username if username else "user"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

def show_dashboard():
    """Display the modern dashboard"""
    load_css()
    
    # Custom header
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>Lumen Strategic Dashboard</h1>
        <p>Welcome, {st.session_state.username} · Strategic Initiative Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Strategy Matrix", "📊 Analytics", "📋 Data View", "📜 Activity Log"])
    
    with tab1:
        # Interactive Matrix
        st.markdown("### Interactive Strategy Matrix")
        
        # Create two columns for matrix and controls
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Display the Plotly matrix
            fig = create_interactive_matrix()
            st.plotly_chart(fig, use_container_width=True, key="matrix_plot")
        
        with col2:
            st.markdown("### Quick Actions")
            
            # Add new initiative
            if st.button("➕ Add Initiative", use_container_width=True):
                st.session_state.show_add_form = True
            
            # Edit selected initiative
            st.markdown("### Edit Initiative")
            df = get_initiatives_from_db()
            if not df.empty:
                selected_title = st.selectbox(
                    "Select to edit:",
                    ["Choose..."] + df['title'].tolist(),
                    key="edit_select"
                )
                
                if selected_title != "Choose...":
                    selected = df[df['title'] == selected_title].iloc[0]
                    
                    with st.form(key=f"edit_form_{selected['id']}"):
                        new_title = st.text_input("Title", value=selected['title'])
                        new_details = st.text_area("Details", value=selected.get('details', ''))
                        new_x = st.slider("Effort", 0, 100, int(selected['x']))
                        new_y = st.slider("Value", 0, 100, int(selected['y']))
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save", use_container_width=True):
                                update_initiative_in_db(
                                    selected['id'], new_title, new_details, 
                                    new_x, new_y, st.session_state.username
                                )
                                st.success("Updated!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("🗑️ Delete", use_container_width=True):
                                delete_initiative_from_db(
                                    selected['id'], selected['title'], 
                                    st.session_state.username
                                )
                                st.success("Deleted!")
                                st.rerun()
        
        # Add new initiative form (popup-style)
        if hasattr(st.session_state, 'show_add_form') and st.session_state.show_add_form:
            with st.container():
                st.markdown("---")
                st.markdown("### 🆕 Add New Initiative")
                
                with st.form(key="add_new_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        title = st.text_input("Title*", key="new_title")
                        category = st.selectbox(
                            "Category*",
                            ["Strategic/Process", "Quick Implementation", 
                             "Technology/Platform", "People/Organization"],
                            key="new_category"
                        )
                        x_pos = st.slider("Effort (0=Low, 100=High)", 0, 100, 50, key="new_x")
                    
                    with col2:
                        details = st.text_area("Details", key="new_details")
                        color = st.selectbox(
                            "Color*",
                            ["pink", "yellow", "green", "blue"],
                            key="new_color"
                        )
                        y_pos = st.slider("Value (0=Low, 100=High)", 0, 100, 50, key="new_y")
                    
                    col1, col2, col3 = st.columns(3)
                    with col2:
                        submitted = st.form_submit_button("Add Initiative", use_container_width=True)
                        
                    if submitted:
                        if title:
                            add_initiative_to_db(
                                title, details, color, category, 
                                x_pos, y_pos, st.session_state.username
                            )
                            st.session_state.show_add_form = False
                            st.success("Initiative added successfully!")
                            st.rerun()
                        else:
                            st.error("Title is required!")
                
                if st.button("Cancel", use_container_width=True):
                    st.session_state.show_add_form = False
                    st.rerun()
        
        # Quick stats row
        df = get_initiatives_from_db()
        if not df.empty:
            df['Quadrant'] = df.apply(lambda row: get_quadrant(row['x'], row['y']), axis=1)
            
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                quick_wins = len(df[df['Quadrant'] == 'Quick Wins'])
                st.metric("🎯 Quick Wins", quick_wins, delta=None, delta_color="normal")
            with col2:
                strategic = len(df[df['Quadrant'] == 'Strategic Investments'])
                st.metric("🚀 Strategic", strategic)
            with col3:
                consider = len(df[df['Quadrant'] == 'Consider Carefully'])
                st.metric("🤔 Consider", consider)
            with col4:
                total = len(df)
                st.metric("📊 Total", total)
    
    with tab2:
        # Analytics Dashboard
        st.markdown("### Strategic Analytics")
        
        df = get_initiatives_from_db()
        if not df.empty:
            df['Quadrant'] = df.apply(lambda row: get_quadrant(row['x'], row['y']), axis=1)
            
            # Two column layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Quadrant distribution
                quadrant_counts = df['Quadrant'].value_counts()
                fig_pie = px.pie(
                    values=quadrant_counts.values,
                    names=quadrant_counts.index,
                    title="Portfolio Distribution",
                    color_discrete_map={
                        'Quick Wins': '#10b981',
                        'Strategic Investments': '#3b82f6',
                        'Consider Carefully': '#f59e0b',
                        'Low Priority': '#ef4444'
                    }
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(
                    showlegend=False,
                    height=400,
                    font=dict(size=14)
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Category distribution
                category_counts = df['category'].value_counts()
                fig_bar = px.bar(
                    x=category_counts.values,
                    y=category_counts.index,
                    orientation='h',
                    title="Category Breakdown",
                    color=category_counts.index,
                    color_discrete_map={
                        'Strategic/Process': '#ff69b4',
                        'Quick Implementation': '#ffd700',
                        'Technology/Platform': '#48c774',
                        'People/Organization': '#3273dc'
                    }
                )
                fig_bar.update_layout(
                    showlegend=False,
                    height=400,
                    xaxis_title="Count",
                    yaxis_title=""
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Heatmap
            st.markdown("### Value/Effort Distribution")
            pivot_table = pd.crosstab(df['value'], df['effort'])
            fig_heatmap = px.imshow(
                pivot_table,
                labels=dict(x="Effort", y="Value", color="Count"),
                color_continuous_scale="Viridis",
                aspect="auto"
            )
            fig_heatmap.update_layout(height=350)
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with tab3:
        # Data table view
        st.markdown("### Initiative Data Table")
        
        df = get_initiatives_from_db()
        if not df.empty:
            df['Quadrant'] = df.apply(lambda row: get_quadrant(row['x'], row['y']), axis=1)
            
            # Format the dataframe
            display_cols = ['title', 'category', 'value', 'effort', 'Quadrant', 'updated_by', 'updated_at']
            df_display = df[display_cols].copy()
            
            # Display with custom styling
            st.dataframe(
                df_display,
                use_container_width=True,
                height=500,
                column_config={
                    "title": st.column_config.TextColumn("Initiative", width="medium"),
                    "category": st.column_config.TextColumn("Category", width="small"),
                    "value": st.column_config.TextColumn("Value", width="small"),
                    "effort": st.column_config.TextColumn("Effort", width="small"),
                    "Quadrant": st.column_config.TextColumn("Quadrant", width="small"),
                    "updated_by": st.column_config.TextColumn("Updated By", width="small"),
                    "updated_at": st.column_config.DatetimeColumn("Last Updated", format="MM/DD/YY HH:mm")
                }
            )
            
            # Export button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export as CSV",
                data=csv,
                file_name=f"lumen_initiatives_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with tab4:
        # Activity log
        st.markdown("### Recent Activity")
        
        audit_df = get_audit_log(50)
        if not audit_df.empty:
            # Create activity cards
            for _, row in audit_df.head(20).iterrows():
                action_icon = {
                    "CREATE": "➕",
                    "UPDATE": "✏️",
                    "DELETE": "🗑️",
                    "MOVE": "↔️",
                    "RESET": "🔄"
                }.get(row['action'], "📝")
                
                action_class = row['action'].lower()
                
                st.markdown(f"""
                <div class="activity-item {action_class}" style="margin: 0.5rem 0;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.5rem; margin-right: 1rem;">{action_icon}</span>
                        <div style="flex: 1;">
                            <strong>{row['user']}</strong> {row['details']}<br>
                            <small style="color: #64748b;">{row['timestamp']}</small>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Sidebar controls
    with st.sidebar:
        st.markdown("### ⚙️ Controls")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        # Database management
        with st.expander("🗄️ Database"):
            df = get_initiatives_from_db()
            st.info(f"Total Initiatives: {len(df)}")
            
            if st.button("Reset to Default", use_container_width=True):
                if st.checkbox("Confirm reset"):
                    reset_database()
                    st.success("Database reset")
                    st.rerun()

def main():
    """Main application entry point"""
    # Initialize database
    init_database()
    
    # Initialize session state
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()