"""
Lumen Workshop Strategic Initiative Dashboard
With True Drag-and-Drop Using Streamlit-Elements
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import base64
import json
from streamlit_elements import elements, mui, html, sync, event, dashboard

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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
    }
    
    .main {
        padding: 0;
        background: #ffffff;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .dashboard-header {
        background: #000000;
        color: #ffffff;
        padding: 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-bottom: 1px solid #424245;
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        color: #86868b;
        font-size: 1.125rem;
    }
    
    .stButton > button {
        background: #000000;
        color: #ffffff;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1d1d1f;
        transform: translateY(-1px);
    }
    
    div[data-testid="metric-container"] {
        background: #ffffff;
        padding: 1.25rem;
        border: 1px solid #d2d2d7;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    </style>
    """, unsafe_allow_html=True)

# Database functions
def init_database():
    """Initialize the database with tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
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
    
    conn.commit()
    conn.close()

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

def update_position(id, x, y, user="user"):
    """Update position of an initiative"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Convert position to value/effort
    value = "High" if y > 66 else "Medium" if y > 33 else "Low"
    effort = "High" if x > 66 else "Medium" if x > 33 else "Low"
    
    c.execute('''
        UPDATE initiatives 
        SET x = ?, y = ?, value = ?, effort = ?, 
            updated_at = CURRENT_TIMESTAMP, updated_by = ?
        WHERE id = ?
    ''', (x, y, value, effort, user, id))
    
    conn.commit()
    conn.close()

def add_initiative_to_db(title, details, color, category, x, y, user="user"):
    """Add new initiative to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    value = "High" if y > 66 else "Medium" if y > 33 else "Low"
    effort = "High" if x > 66 else "Medium" if x > 33 else "Low"
    
    c.execute('''
        INSERT INTO initiatives (title, details, color, category, x, y, value, effort, created_by, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, details, color, category, x, y, value, effort, user, user))
    
    conn.commit()
    conn.close()

def delete_initiative_from_db(id, user="user"):
    """Soft delete initiative from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        UPDATE initiatives 
        SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP, updated_by = ?
        WHERE id = ?
    ''', (user, id))
    
    conn.commit()
    conn.close()

# Authentication
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = "user"
    if 'selected_initiative' not in st.session_state:
        st.session_state.selected_initiative = None
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False

def check_authentication(password):
    """Check if the provided password is correct"""
    correct_password = base64.b64decode('THVtZW5EYXNoMjAyNSE=').decode()
    return password == correct_password

def show_login():
    """Display login form"""
    load_css()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 3rem; border: 1px solid #d2d2d7; margin-top: 5rem;'>
            <h1 style='color: #1d1d1f; text-align: center;'>Lumen Dashboard</h1>
            <p style='color: #86868b; text-align: center;'>Strategic Initiative Planning</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", value="user")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Sign In", use_container_width=True):
                if check_authentication(password):
                    st.session_state.authenticated = True
                    st.session_state.username = username if username else "user"
                    st.rerun()
                else:
                    st.error("Invalid credentials")

def create_draggable_matrix():
    """Create a draggable matrix using streamlit-elements"""

    df = get_initiatives_from_db()

    # Build initial layout from stored positions
    layout = []
    for _, row in df.iterrows():
        grid_x = int((row["x"] / 100) * 12)
        grid_y = int(((100 - row["y"]) / 100) * 12)
        layout.append(dashboard.Item(str(row["id"]), grid_x, grid_y, 1, 1))

    def handle_layout_change(updated_layout):
        """Update positions in database after drag"""
        for item in updated_layout:
            item_id = int(item["i"])
            x = (item["x"] / 12) * 100
            y = 100 - (item["y"] / 12) * 100
            update_position(item_id, x, y, st.session_state.username)
        st.rerun()

    def handle_click(item_id):
        """Handle when an item is clicked"""
        st.session_state.selected_initiative = item_id
        st.rerun()

    # Create the elements container
    with elements("matrix"):
        with mui.Box(
            sx={
                "width": 800,
                "height": 600,
                "position": "relative",
                "background": "linear-gradient(to right, #f5f5f7 50%, #ffffff 50%)",
                "border": "1px solid #d2d2d7",
                "borderRadius": "8px",
                "overflow": "hidden"
            }
        ):
            # Add quadrant labels
            mui.Typography(
                "QUICK WINS",
                sx={
                    "position": "absolute",
                    "top": 20,
                    "left": 20,
                    "color": "#34c759",
                    "fontWeight": 600,
                    "fontSize": "12px"
                }
            )

            mui.Typography(
                "STRATEGIC",
                sx={
                    "position": "absolute",
                    "top": 20,
                    "right": 20,
                    "color": "#007aff",
                    "fontWeight": 600,
                    "fontSize": "12px"
                }
            )

            mui.Typography(
                "LOW PRIORITY",
                sx={
                    "position": "absolute",
                    "bottom": 20,
                    "left": 20,
                    "color": "#8e8e93",
                    "fontWeight": 600,
                    "fontSize": "12px"
                }
            )

            mui.Typography(
                "CONSIDER",
                sx={
                    "position": "absolute",
                    "bottom": 20,
                    "right": 20,
                    "color": "#ff9500",
                    "fontWeight": 600,
                    "fontSize": "12px"
                }
            )

            # Grid lines
            mui.Box(
                sx={
                    "position": "absolute",
                    "top": "33.33%",
                    "left": 0,
                    "right": 0,
                    "height": "1px",
                    "background": "#d2d2d7"
                }
            )

            mui.Box(
                sx={
                    "position": "absolute",
                    "top": "66.66%",
                    "left": 0,
                    "right": 0,
                    "height": "1px",
                    "background": "#d2d2d7"
                }
            )

            mui.Box(
                sx={
                    "position": "absolute",
                    "top": 0,
                    "bottom": 0,
                    "left": "50%",
                    "width": "1px",
                    "background": "#d2d2d7"
                }
            )

            # Draggable items using dashboard.Grid
            with dashboard.Grid(
                layout,
                rowHeight=50,
                cols=12,
                width=800,
                margin=[0, 0],
                containerPadding=[0, 0],
                draggableHandle=".drag-handle",
                onLayoutChange=handle_layout_change,
            ):
                for _, row in df.iterrows():
                    colors = {
                        "pink": "#ff3b30",
                        "yellow": "#ffcc00",
                        "green": "#34c759",
                        "blue": "#007aff",
                    }

                    with mui.Paper(
                        key=str(row["id"]),
                        className="drag-handle",
                        elevation=3,
                        onClick=lambda e, item_id=row["id"]: handle_click(item_id),
                        sx={
                            "padding": "12px",
                            "borderRadius": "8px",
                            "background": colors.get(row["color"], "#8e8e93"),
                            "color": "white",
                            "cursor": "move",
                            "minWidth": "120px",
                            "maxWidth": "150px",
                            "textAlign": "center",
                            "&:hover": {"transform": "scale(1.05)", "boxShadow": 4},
                        },
                    ):
                        mui.Typography(
                            row["title"][:20] + "..." if len(row["title"]) > 20 else row["title"],
                            sx={"fontSize": "12px", "fontWeight": 500},
                        )

def show_dashboard():
    """Display the dashboard with draggable matrix"""
    load_css()
    
    st.markdown(f"""
    <div class="dashboard-header">
        <h1>Lumen Strategic Dashboard</h1>
        <p>{st.session_state.username} · Strategic Initiative Planning</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⊙ Interactive Matrix", "◉ Analytics", "☰ Data View"])
    
    with tab1:
        st.markdown("### Interactive Strategy Matrix")
        st.info("🎯 Drag and drop cards to reposition · Click cards to edit details")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Display the draggable matrix
            create_draggable_matrix()
        
        with col2:
            st.markdown("### Actions")
            
            # Edit selected initiative
            if st.session_state.selected_initiative:
                df = get_initiatives_from_db()
                selected = df[df['id'] == st.session_state.selected_initiative]
                
                if not selected.empty:
                    selected = selected.iloc[0]
                    st.markdown(f"**Editing:** {selected['title']}")
                    
                    with st.form(key="edit_form"):
                        new_title = st.text_input("Title", value=selected['title'])
                        new_details = st.text_area("Details", value=selected.get('details', ''))
                        new_category = st.selectbox(
                            "Category",
                            ["Strategic/Process", "Quick Implementation", 
                             "Technology/Platform", "People/Organization"]
                        )
                        new_color = st.selectbox(
                            "Color",
                            ["pink", "yellow", "green", "blue"]
                        )
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update", use_container_width=True):
                                # Update initiative
                                conn = sqlite3.connect(DB_PATH)
                                c = conn.cursor()
                                c.execute('''
                                    UPDATE initiatives 
                                    SET title = ?, details = ?, category = ?, color = ?, 
                                        updated_at = CURRENT_TIMESTAMP, updated_by = ?
                                    WHERE id = ?
                                ''', (new_title, new_details, new_category, new_color, 
                                      st.session_state.username, st.session_state.selected_initiative))
                                conn.commit()
                                conn.close()
                                st.success("Updated!")
                                st.session_state.selected_initiative = None
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("Delete", use_container_width=True):
                                delete_initiative_from_db(st.session_state.selected_initiative, 
                                                        st.session_state.username)
                                st.success("Deleted!")
                                st.session_state.selected_initiative = None
                                st.rerun()
            
            # Add new initiative
            if st.button("➕ Add New", use_container_width=True):
                st.session_state.show_add_form = True
            
            if st.session_state.show_add_form:
                with st.form(key="add_form"):
                    title = st.text_input("Title*")
                    details = st.text_area("Details")
                    category = st.selectbox(
                        "Category",
                        ["Strategic/Process", "Quick Implementation", 
                         "Technology/Platform", "People/Organization"]
                    )
                    color = st.selectbox("Color", ["pink", "yellow", "green", "blue"])
                    
                    if st.form_submit_button("Add", use_container_width=True):
                        if title:
                            add_initiative_to_db(title, details, color, category, 50, 50, 
                                               st.session_state.username)
                            st.session_state.show_add_form = False
                            st.success("Added! Drag to position.")
                            st.rerun()
                        else:
                            st.error("Title required!")
        
        # Stats
        df = get_initiatives_from_db()
        if not df.empty:
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                quick_wins = len(df[(df['x'] < 50) & (df['y'] > 66)])
                st.metric("Quick Wins", quick_wins)
            with col2:
                strategic = len(df[(df['x'] >= 50) & (df['y'] > 66)])
                st.metric("Strategic", strategic)
            with col3:
                low_priority = len(df[df['y'] <= 33])
                st.metric("Low Priority", low_priority)
            with col4:
                st.metric("Total", len(df))
    
    with tab2:
        st.markdown("### Analytics")
        # Add your analytics here
        
    with tab3:
        st.markdown("### Data Table")
        df = get_initiatives_from_db()
        if not df.empty:
            st.dataframe(df[['title', 'category', 'value', 'effort', 'updated_by', 'updated_at']], 
                        use_container_width=True)

def main():
    """Main application entry point"""
    init_database()
    init_session_state()
    
    if not st.session_state.authenticated:
        show_login()
    else:
        show_dashboard()

if __name__ == "__main__":
    main()
