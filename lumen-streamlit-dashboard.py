"""
Lumen Workshop Strategic Initiative Dashboard
Streamlit Application with Database Persistence
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

# Page configuration
st.set_page_config(
    page_title="Lumen Workshop Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database configuration
DB_PATH = "lumen_dashboard.db"

# Custom CSS for styling
def load_css():
    st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    .quadrant-label {
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 5px;
        display: inline-block;
    }
    .quick-wins {
        background: #d4edda;
        color: #155724;
    }
    .strategic {
        background: #cce5ff;
        color: #004085;
    }
    .consider {
        background: #fff3cd;
        color: #856404;
    }
    .low-priority {
        background: #f8d7da;
        color: #721c24;
    }
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .initiative-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .audit-log {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# Database functions
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
         "color": "pink", "category": "Strategic/Process", "x": 65, "y": 10, "value": "High", "effort": "High"},
        {"title": "Campaign Tracking", "details": "Implement comprehensive campaign tracking system", 
         "color": "pink", "category": "Strategic/Process", "x": 70, "y": 20, "value": "High", "effort": "High"},
        {"title": "Governance Standards", "details": "Governance around things: AEMI, content alignment from other tech", 
         "color": "pink", "category": "Strategic/Process", "x": 80, "y": 15, "value": "High", "effort": "High"},
        {"title": "Supposed to differentiate", "details": "Supposed to differentiate on experience - foundational follow", 
         "color": "pink", "category": "Strategic/Process", "x": 75, "y": 25, "value": "High", "effort": "High"},
        {"title": "AI/O Implementation", "details": "AI/O or some sort of experience orchestration", 
         "color": "green", "category": "Technology/Platform", "x": 85, "y": 18, "value": "High", "effort": "High"},
        {"title": "Lead/Person Source", "details": "Implement lead/person source data warehouse", 
         "color": "pink", "category": "Strategic/Process", "x": 68, "y": 30, "value": "High", "effort": "High"},
        {"title": "AEM Developer Team", "details": "Build AEM Developer team with appropriate roles and skills", 
         "color": "pink", "category": "Strategic/Process", "x": 85, "y": 35, "value": "Medium", "effort": "High"},
        {"title": "Contact Remediation Process", "details": "Implement contact remediation processes", 
         "color": "yellow", "category": "Quick Implementation", "x": 10, "y": 45, "value": "Medium", "effort": "Low"},
        {"title": "Different template for journey", "details": "Create different templates for voter journey campaigns", 
         "color": "green", "category": "Technology/Platform", "x": 15, "y": 50, "value": "Medium", "effort": "Low"},
        {"title": "What-if Chat", "details": "Implement what-if chat functionality", 
         "color": "green", "category": "Technology/Platform", "x": 8, "y": 55, "value": "Medium", "effort": "Low"},
        {"title": "Scalable Email Execution", "details": "Build scalable email execution framework", 
         "color": "yellow", "category": "Quick Implementation", "x": 35, "y": 48, "value": "Medium", "effort": "Medium"},
        {"title": "Missing big talent on AEM", "details": "Critical talent gap in AEM expertise", 
         "color": "green", "category": "Technology/Platform", "x": 40, "y": 53, "value": "Medium", "effort": "Medium"},
        {"title": "CDP Implementation", "details": "Customer Data Platform implementation - foundational need", 
         "color": "pink", "category": "Strategic/Process", "x": 45, "y": 45, "value": "Medium", "effort": "Medium"},
        {"title": "Multiple redundant items", "details": "Multiple items in Tech Stack Page 26 do the same thing", 
         "color": "pink", "category": "Strategic/Process", "x": 50, "y": 58, "value": "Medium", "effort": "Medium"},
        {"title": "SDR Process", "details": "SDR process and campaign tracking implementation", 
         "color": "green", "category": "Technology/Platform", "x": 70, "y": 45, "value": "Medium", "effort": "High"},
        {"title": "Misconception about CDP", "details": "Misconception that CDP will fix all audience/segmentation issues", 
         "color": "pink", "category": "Strategic/Process", "x": 75, "y": 50, "value": "Medium", "effort": "High"},
        {"title": "Leverage Chat KPIs", "details": "Leverage existing chat KPIs for insights", 
         "color": "yellow", "category": "Quick Implementation", "x": 12, "y": 75, "value": "Low", "effort": "Low"},
        {"title": "Technical Chat Platform", "details": "Define technical chat platform and strategy", 
         "color": "pink", "category": "Strategic/Process", "x": 18, "y": 80, "value": "Low", "effort": "Low"},
        {"title": "DC to BC Admin", "details": "Administrative transition requirements", 
         "color": "pink", "category": "Strategic/Process", "x": 45, "y": 78, "value": "Low", "effort": "Medium"}
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

# Initialize session state
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'auth_attempts' not in st.session_state:
        st.session_state.auth_attempts = 0
    if 'locked_until' not in st.session_state:
        st.session_state.locked_until = None
    if 'username' not in st.session_state:
        st.session_state.username = "user"

def hash_password(password):
    """Hash password with salt for authentication"""
    salt = 'L3m3nW0rk$h0p2025!'
    return hashlib.sha256((password + salt).encode()).hexdigest()

def check_authentication(password):
    """Check if the provided password is correct"""
    # Using base64 encoded password for obfuscation
    correct_password = base64.b64decode('THVtZW5EYXNoMjAyNSE=').decode()
    return password == correct_password

def show_login():
    """Display login form"""
    load_css()
    
    st.markdown("<h1>🔐 Lumen Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>Strategic Initiative Matrix</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### Enter Credentials")
            
            # Check if account is locked
            if st.session_state.locked_until:
                if datetime.now() < st.session_state.locked_until:
                    remaining = (st.session_state.locked_until - datetime.now()).seconds
                    st.error(f"Account locked. Try again in {remaining} seconds.")
                    st.stop()
                else:
                    st.session_state.locked_until = None
                    st.session_state.auth_attempts = 0
            
            username = st.text_input("Username (optional)", value="user", key="username_input")
            password = st.text_input("Password", type="password", key="password_input")
            submit = st.form_submit_button("Access Dashboard", use_container_width=True)
            
            if submit:
                if check_authentication(password):
                    st.session_state.authenticated = True
                    st.session_state.auth_attempts = 0
                    st.session_state.username = username if username else "user"
                    
                    # Log successful login
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO sessions (user) VALUES (?)
                    ''', (st.session_state.username,))
                    conn.commit()
                    conn.close()
                    
                    st.rerun()
                else:
                    st.session_state.auth_attempts += 1
                    
                    if st.session_state.auth_attempts >= 5:
                        st.session_state.locked_until = datetime.now() + timedelta(minutes=5)
                        st.error("Too many failed attempts. Account locked for 5 minutes.")
                    elif st.session_state.auth_attempts >= 3:
                        remaining = 5 - st.session_state.auth_attempts
                        st.warning(f"Warning: {remaining} attempts remaining")
                        st.error("Incorrect password. Please try again.")
                    else:
                        st.error("Incorrect password. Please try again.")

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

def get_color_hex(color_name):
    """Convert color name to hex value"""
    colors = {
        "pink": "#ff69b4",
        "yellow": "#ffd700",
        "green": "#90ee90",
        "blue": "#87ceeb",
        "orange": "#ffa500",
        "red": "#ff6b6b"
    }
    return colors.get(color_name, "#cccccc")

def create_matrix_plot():
    """Create the interactive 2x2 matrix using Plotly"""
    fig = go.Figure()
    
    # Add quadrant backgrounds
    shapes = [
        # Quick Wins (top-left)
        dict(type="rect", x0=0, y0=66.66, x1=50, y1=100,
             fillcolor="rgba(212, 237, 218, 0.2)", line=dict(width=0)),
        # Strategic Investments (top-right)
        dict(type="rect", x0=50, y0=66.66, x1=100, y1=100,
             fillcolor="rgba(204, 229, 255, 0.2)", line=dict(width=0)),
        # Low Priority (bottom-left)
        dict(type="rect", x0=0, y0=0, x1=50, y1=33.33,
             fillcolor="rgba(248, 215, 218, 0.2)", line=dict(width=0)),
        # Consider Carefully (bottom-right)
        dict(type="rect", x0=50, y0=0, x1=100, y1=33.33,
             fillcolor="rgba(255, 243, 205, 0.2)", line=dict(width=0))
    ]
    
    # Add grid lines
    shapes.extend([
        dict(type="line", x0=0, y0=33.33, x1=100, y1=33.33,
             line=dict(color="gray", width=1, dash="dash")),
        dict(type="line", x0=0, y0=66.66, x1=100, y1=66.66,
             line=dict(color="gray", width=1, dash="dash")),
        dict(type="line", x0=50, y0=0, x1=50, y1=100,
             line=dict(color="gray", width=1, dash="dash"))
    ])
    
    # Get initiatives from database
    df = get_initiatives_from_db()
    
    if not df.empty:
        # Group initiatives by color for plotting
        color_groups = df.groupby('color')
        
        for color, group in color_groups:
            hover_text = []
            for _, row in group.iterrows():
                text = f"<b>{row['title']}</b><br>{row['details']}<br>"
                text += f"Value: {row['value']}<br>Effort: {row['effort']}<br>"
                text += f"Created: {row['created_at']}<br>By: {row['created_by']}"
                hover_text.append(text)
            
            fig.add_trace(go.Scatter(
                x=group['x'],
                y=group['y'],
                mode='markers+text',
                marker=dict(
                    size=15,
                    color=get_color_hex(color),
                    line=dict(width=2, color='white')
                ),
                text=group['title'],
                textposition="top center",
                textfont=dict(size=9),
                hovertext=hover_text,
                hoverinfo='text',
                name=color.capitalize()
            ))
    
    # Update layout
    fig.update_layout(
        title="Strategic Initiative Matrix",
        xaxis=dict(
            title="Effort (Months) →",
            range=[0, 100],
            tickmode='array',
            tickvals=[0, 50, 100],
            ticktext=['0', '6', '12'],
            showgrid=False
        ),
        yaxis=dict(
            title="Value →",
            range=[0, 100],
            tickmode='array',
            tickvals=[0, 33.33, 66.66, 100],
            ticktext=['Low', 'Medium', 'Medium', 'High'],
            showgrid=False
        ),
        shapes=shapes,
        annotations=[
            dict(text="Quick Wins", x=25, y=83, showarrow=False, font=dict(size=12, color="green")),
            dict(text="Strategic Investments", x=75, y=83, showarrow=False, font=dict(size=12, color="blue")),
            dict(text="Low Priority", x=25, y=17, showarrow=False, font=dict(size=12, color="red")),
            dict(text="Consider Carefully", x=75, y=17, showarrow=False, font=dict(size=12, color="orange"))
        ],
        height=600,
        hovermode='closest',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.01
        )
    )
    
    return fig

def show_dashboard():
    """Display the main dashboard"""
    load_css()
    
    st.markdown("<h1>🎯 Lumen Workshop Strategic Initiative Matrix</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #7f8c8d;'>Logged in as: <b>{st.session_state.username}</b></p>", unsafe_allow_html=True)
    
    # Sidebar for controls
    with st.sidebar:
        st.markdown("## 🎛️ Controls")
        st.markdown(f"**User:** {st.session_state.username}")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        
        # Add new initiative
        with st.expander("➕ Add New Initiative"):
            with st.form("add_initiative"):
                title = st.text_input("Title*")
                details = st.text_area("Details")
                category = st.selectbox("Category*", [
                    "Strategic/Process",
                    "Quick Implementation", 
                    "Technology/Platform",
                    "People/Organization"
                ])
                color = st.selectbox("Color*", ["pink", "yellow", "green", "blue", "red", "orange"])
                col1, col2 = st.columns(2)
                with col1:
                    x_pos = st.slider("Effort (X)", 0, 100, 50)
                with col2:
                    y_pos = st.slider("Value (Y)", 0, 100, 50)
                
                if st.form_submit_button("Add Initiative"):
                    if title:
                        add_initiative_to_db(title, details, color, category, x_pos, y_pos, st.session_state.username)
                        st.success("Initiative added successfully!")
                        st.rerun()
        
        # Export/Import
        st.markdown("---")
        st.markdown("## 📊 Data Management")
        
        # Export to CSV
        if st.button("📥 Export to CSV", use_container_width=True):
            df = get_initiatives_from_db()
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"lumen_initiatives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Database management
        st.markdown("---")
        st.markdown("## 🗄️ Database Management")
        
        # Show database stats
        df = get_initiatives_from_db()
        st.info(f"Total Initiatives: {len(df)}")
        
        # Reset database
        if st.button("🔄 Reset Database", use_container_width=True):
            confirm = st.checkbox("I confirm database reset")
            if confirm:
                if st.button("Confirm Reset"):
                    reset_database()
                    st.success("Database reset to original data")
                    st.rerun()
        
        # Show recent activity
        st.markdown("---")
        st.markdown("## 📜 Recent Activity")
        audit_df = get_audit_log(10)
        if not audit_df.empty:
            for _, row in audit_df.iterrows():
                action_emoji = {"CREATE": "➕", "UPDATE": "✏️", "DELETE": "🗑️", "RESET": "🔄"}.get(row['action'], "📝")
                st.markdown(f"""
                <div class='audit-log'>
                    {action_emoji} <b>{row['user']}</b> - {row['details']}<br>
                    <small>{row['timestamp']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Matrix View", "📋 Table View", "📊 Analytics", "📜 Audit Log"])
    
    with tab1:
        # Display the matrix
        fig = create_matrix_plot()
        st.plotly_chart(fig, use_container_width=True)
        
        # Edit initiatives section
        st.markdown("### ✏️ Edit Initiatives")
        df = get_initiatives_from_db()
        
        if not df.empty:
            col1, col2 = st.columns([1, 3])
            with col1:
                initiative_titles = ["Select an initiative..."] + df['title'].tolist()
                selected_title = st.selectbox("Choose Initiative", initiative_titles)
            
            if selected_title != "Select an initiative...":
                selected = df[df['title'] == selected_title].iloc[0]
                
                with col2:
                    with st.form(f"edit_{selected['id']}"):
                        col3, col4 = st.columns(2)
                        with col3:
                            new_x = st.slider("Effort", 0, 100, int(selected['x']))
                            new_y = st.slider("Value", 0, 100, int(selected['y']))
                        with col4:
                            new_title = st.text_input("Title", selected['title'])
                            new_details = st.text_area("Details", selected['details'])
                        
                        st.markdown(f"**Last updated:** {selected['updated_at']} by {selected['updated_by']}")
                        
                        col5, col6, col7 = st.columns(3)
                        with col5:
                            if st.form_submit_button("💾 Update"):
                                update_initiative_in_db(selected['id'], new_title, new_details, new_x, new_y, st.session_state.username)
                                st.success("Updated successfully!")
                                st.rerun()
                        with col6:
                            if st.form_submit_button("🗑️ Delete"):
                                delete_initiative_from_db(selected['id'], selected['title'], st.session_state.username)
                                st.success("Deleted successfully!")
                                st.rerun()
    
    with tab2:
        # Display initiatives in a table
        df = get_initiatives_from_db()
        
        if not df.empty:
            # Add quadrant column
            df['Quadrant'] = df.apply(lambda row: get_quadrant(row['x'], row['y']), axis=1)
            
            # Display columns
            display_cols = ['title', 'category', 'value', 'effort', 'Quadrant', 'details', 'updated_by', 'updated_at']
            df_display = df[display_cols]
            
            # Apply color coding
            def color_quadrant(val):
                colors = {
                    'Quick Wins': 'background-color: #d4edda',
                    'Strategic Investments': 'background-color: #cce5ff',
                    'Consider Carefully': 'background-color: #fff3cd',
                    'Low Priority': 'background-color: #f8d7da'
                }
                return colors.get(val, '')
            
            styled_df = df_display.style.applymap(color_quadrant, subset=['Quadrant'])
            st.dataframe(styled_df, use_container_width=True, height=600)
            
            # Summary stats
            st.markdown("### 📊 Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                quick_wins = len(df[df['Quadrant'] == 'Quick Wins'])
                st.metric("Quick Wins", quick_wins)
            with col2:
                strategic = len(df[df['Quadrant'] == 'Strategic Investments'])
                st.metric("Strategic", strategic)
            with col3:
                consider = len(df[df['Quadrant'] == 'Consider Carefully'])
                st.metric("Consider", consider)
            with col4:
                low_priority = len(df[df['Quadrant'] == 'Low Priority'])
                st.metric("Low Priority", low_priority)
    
    with tab3:
        # Analytics and insights
        st.markdown("### 📊 Portfolio Analytics")
        
        df = get_initiatives_from_db()
        
        if not df.empty:
            df['Quadrant'] = df.apply(lambda row: get_quadrant(row['x'], row['y']), axis=1)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Quadrant distribution pie chart
                quadrant_counts = df['Quadrant'].value_counts()
                fig_pie = px.pie(
                    values=quadrant_counts.values,
                    names=quadrant_counts.index,
                    title="Distribution by Quadrant",
                    color_discrete_map={
                        'Quick Wins': '#d4edda',
                        'Strategic Investments': '#cce5ff',
                        'Consider Carefully': '#fff3cd',
                        'Low Priority': '#f8d7da'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # Category distribution bar chart
                category_counts = df['category'].value_counts()
                fig_bar = px.bar(
                    x=category_counts.values,
                    y=category_counts.index,
                    orientation='h',
                    title="Distribution by Category",
                    labels={'x': 'Count', 'y': 'Category'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Value vs Effort heatmap
            st.markdown("### 🔥 Value/Effort Heatmap")
            pivot_table = pd.crosstab(df['value'], df['effort'])
            fig_heatmap = px.imshow(
                pivot_table,
                labels=dict(x="Effort", y="Value", color="Count"),
                title="Initiative Distribution Heatmap",
                color_continuous_scale="YlOrRd"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # User contributions
            st.markdown("### 👥 User Contributions")
            user_stats = df.groupby('updated_by').size().reset_index(name='Updates')
            fig_user = px.bar(user_stats, x='updated_by', y='Updates', title="Updates by User")
            st.plotly_chart(fig_user, use_container_width=True)
            
            # Recommendations
            st.markdown("### 💡 Strategic Recommendations")
            
            quick_wins_df = df[df['Quadrant'] == 'Quick Wins']
            if not quick_wins_df.empty:
                st.success(f"**Quick Wins Available:** {len(quick_wins_df)} initiatives can be implemented immediately with low effort and high value.")
                with st.expander("View Quick Wins"):
                    for _, initiative in quick_wins_df.iterrows():
                        st.write(f"• **{initiative['title']}** - {initiative['details']}")
            
            strategic_df = df[df['Quadrant'] == 'Strategic Investments']
            if not strategic_df.empty:
                st.info(f"**Strategic Investments:** {len(strategic_df)} initiatives require significant effort but offer high value.")
            
            low_priority_df = df[df['Quadrant'] == 'Low Priority']
            if not low_priority_df.empty:
                st.warning(f"**Review Low Priority:** {len(low_priority_df)} initiatives may need reassessment or removal from the roadmap.")
    
    with tab4:
        # Full audit log
        st.markdown("### 📜 Complete Audit Trail")
        
        audit_df = get_audit_log(100)
        
        if not audit_df.empty:
            # Add filters
            col1, col2, col3 = st.columns(3)
            with col1:
                action_filter = st.multiselect("Filter by Action", options=audit_df['action'].unique())
            with col2:
                user_filter = st.multiselect("Filter by User", options=audit_df['user'].unique())
            
            # Apply filters
            filtered_df = audit_df
            if action_filter:
                filtered_df = filtered_df[filtered_df['action'].isin(action_filter)]
            if user_filter:
                filtered_df = filtered_df[filtered_df['user'].isin(user_filter)]
            
            # Display filtered results
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            # Activity timeline
            st.markdown("### 📈 Activity Timeline")
            if not filtered_df.empty:
                filtered_df['date'] = pd.to_datetime(filtered_df['timestamp']).dt.date
                activity_by_date = filtered_df.groupby('date').size().reset_index(name='Actions')
                fig_timeline = px.line(activity_by_date, x='date', y='Actions', 
                                       title="Activity Over Time", markers=True)
                st.plotly_chart(fig_timeline, use_container_width=True)

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