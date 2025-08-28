"""
Lumen Workshop Strategic Initiative Dashboard
Professional Streamlit Application with Database Persistence
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
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database configuration
DB_PATH = "lumen_dashboard.db"

# Professional CSS styling
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        padding: 0;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .dashboard-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .dashboard-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    /* Card Styles */
    .initiative-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: move;
        position: relative;
        border-left: 4px solid;
        margin: 0.5rem;
    }
    
    .initiative-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
    }
    
    .initiative-card.pink {
        border-left-color: #ff69b4;
        background: linear-gradient(135deg, #fff 0%, #fff0f8 100%);
    }
    
    .initiative-card.yellow {
        border-left-color: #ffd700;
        background: linear-gradient(135deg, #fff 0%, #fffef0 100%);
    }
    
    .initiative-card.green {
        border-left-color: #48c774;
        background: linear-gradient(135deg, #fff 0%, #f0fff4 100%);
    }
    
    .initiative-card.blue {
        border-left-color: #3273dc;
        background: linear-gradient(135deg, #fff 0%, #f0f7ff 100%);
    }
    
    /* Matrix Container */
    .matrix-wrapper {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        position: relative;
        margin: 1rem 0;
    }
    
    .matrix-container {
        position: relative;
        width: 100%;
        height: 700px;
        background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
        border-radius: 16px;
        overflow: hidden;
        border: 2px solid #e1e4e8;
    }
    
    /* Quadrant Labels */
    .quadrant-overlay {
        position: absolute;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 5;
    }
    
    .quadrant-label {
        position: absolute;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.875rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .quadrant-label.quick-wins {
        color: #10b981;
        border: 2px solid #10b98133;
        background: rgba(16, 185, 129, 0.05);
    }
    
    .quadrant-label.strategic {
        color: #3b82f6;
        border: 2px solid #3b82f633;
        background: rgba(59, 130, 246, 0.05);
    }
    
    .quadrant-label.consider {
        color: #f59e0b;
        border: 2px solid #f59e0b33;
        background: rgba(245, 158, 11, 0.05);
    }
    
    .quadrant-label.low-priority {
        color: #ef4444;
        border: 2px solid #ef444433;
        background: rgba(239, 68, 68, 0.05);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        color: white;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 2rem;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #64748b;
        border-bottom: 2px solid transparent;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        color: #667eea;
        border-bottom: 2px solid #667eea;
        background: transparent;
    }
    
    /* Forms */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 10px;
        border: 2px solid #e1e4e8;
        padding: 0.75rem;
        font-size: 0.95rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        border: 2px solid #e1e4e8;
        padding: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #667eea;
        background: #fafbff;
    }
    
    /* Activity Feed */
    .activity-item {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .activity-item:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .activity-item.create {
        border-left-color: #10b981;
    }
    
    .activity-item.update {
        border-left-color: #3b82f6;
    }
    
    .activity-item.delete {
        border-left-color: #ef4444;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #1a1a2e;
        color: white;
        text-align: center;
        border-radius: 8px;
        padding: 0.5rem;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.875rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    
    /* Animations */
    @keyframes slideIn {
        from {
            transform: translateY(20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    .animate-slide-in {
        animation: slideIn 0.5s ease;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-header h1 {
            font-size: 1.5rem;
        }
        
        .matrix-container {
            height: 500px;
        }
        
        .stButton > button {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }
    }
    
    /* Add New Card Button */
    .add-card-btn {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
        font-size: 2rem;
        cursor: pointer;
        transition: all 0.3s ease;
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .add-card-btn:hover {
        transform: scale(1.1) rotate(90deg);
        box-shadow: 0 6px 30px rgba(16, 185, 129, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# Interactive Matrix Component with Drag and Drop
def create_interactive_matrix():
    """Create an interactive matrix with drag-and-drop and click-to-edit capabilities"""
    
    df = get_initiatives_from_db()
    
    # Convert dataframe to JSON for JavaScript
    initiatives_json = df.to_json(orient='records') if not df.empty else '[]'
    
    # HTML and JavaScript for interactive matrix
    matrix_html = f"""
    <div class="matrix-wrapper">
        <div class="matrix-container" id="matrixContainer">
            <div class="quadrant-overlay">
                <div class="quadrant-label quick-wins" style="top: 20px; left: 20px;">Quick Wins</div>
                <div class="quadrant-label strategic" style="top: 20px; right: 20px;">Strategic</div>
                <div class="quadrant-label low-priority" style="bottom: 20px; left: 20px;">Low Priority</div>
                <div class="quadrant-label consider" style="bottom: 20px; right: 20px;">Consider</div>
            </div>
            
            <!-- Grid lines -->
            <svg style="position: absolute; width: 100%; height: 100%; pointer-events: none;">
                <line x1="0" y1="33.33%" x2="100%" y2="33.33%" stroke="#e1e4e8" stroke-width="2" stroke-dasharray="5,5"/>
                <line x1="0" y1="66.66%" x2="100%" y2="66.66%" stroke="#e1e4e8" stroke-width="2" stroke-dasharray="5,5"/>
                <line x1="50%" y1="0" x2="50%" y2="100%" stroke="#e1e4e8" stroke-width="2" stroke-dasharray="5,5"/>
            </svg>
            
            <!-- Axis labels -->
            <div style="position: absolute; bottom: -30px; left: 50%; transform: translateX(-50%); font-weight: 600; color: #64748b;">
                Effort →
            </div>
            <div style="position: absolute; left: -30px; top: 50%; transform: rotate(-90deg) translateX(-50%); font-weight: 600; color: #64748b;">
                Value →
            </div>
            
            <div id="cardsContainer"></div>
        </div>
        
        <!-- Floating Add Button -->
        <button class="add-card-btn" onclick="addNewCard()">+</button>
    </div>
    
    <!-- Edit Modal -->
    <div id="editModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 2000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 2rem; border-radius: 20px; width: 500px; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
            <h3 style="margin-top: 0; color: #1a1a2e;">Edit Initiative</h3>
            <input type="hidden" id="editId">
            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Title</label>
                <input type="text" id="editTitle" style="width: 100%; padding: 0.75rem; border-radius: 10px; border: 2px solid #e1e4e8;">
            </div>
            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Details</label>
                <textarea id="editDetails" style="width: 100%; padding: 0.75rem; border-radius: 10px; border: 2px solid #e1e4e8; min-height: 100px;"></textarea>
            </div>
            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Category</label>
                <select id="editCategory" style="width: 100%; padding: 0.75rem; border-radius: 10px; border: 2px solid #e1e4e8;">
                    <option value="Strategic/Process">Strategic/Process</option>
                    <option value="Quick Implementation">Quick Implementation</option>
                    <option value="Technology/Platform">Technology/Platform</option>
                    <option value="People/Organization">People/Organization</option>
                </select>
            </div>
            <div style="margin-bottom: 1rem;">
                <label style="display: block; margin-bottom: 0.5rem; font-weight: 500;">Color</label>
                <select id="editColor" style="width: 100%; padding: 0.75rem; border-radius: 10px; border: 2px solid #e1e4e8;">
                    <option value="pink">Pink</option>
                    <option value="yellow">Yellow</option>
                    <option value="green">Green</option>
                    <option value="blue">Blue</option>
                </select>
            </div>
            <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                <button onclick="closeEditModal()" style="padding: 0.75rem 1.5rem; border-radius: 10px; border: 2px solid #e1e4e8; background: white; cursor: pointer;">Cancel</button>
                <button onclick="saveEdit()" style="padding: 0.75rem 1.5rem; border-radius: 10px; border: none; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; cursor: pointer;">Save</button>
                <button onclick="deleteCard()" style="padding: 0.75rem 1.5rem; border-radius: 10px; border: none; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; cursor: pointer;">Delete</button>
            </div>
        </div>
    </div>
    
    <script>
        let initiatives = {initiatives_json};
        let draggedElement = null;
        let isCreatingNew = false;
        
        function createCard(initiative) {{
            const card = document.createElement('div');
            card.className = 'initiative-card ' + initiative.color;
            card.id = 'card-' + initiative.id;
            card.style.position = 'absolute';
            card.style.left = initiative.x + '%';
            card.style.top = initiative.y + '%';
            card.style.width = '150px';
            card.style.cursor = 'move';
            card.style.transform = 'translate(-50%, -50%)';
            card.innerHTML = `
                <div style="font-weight: 600; margin-bottom: 0.5rem; font-size: 0.875rem;">${{initiative.title}}</div>
                <div style="font-size: 0.75rem; color: #64748b;">${{initiative.category}}</div>
            `;
            
            // Make draggable
            card.draggable = true;
            card.addEventListener('dragstart', (e) => {{
                draggedElement = card;
                card.style.opacity = '0.5';
            }});
            
            card.addEventListener('dragend', (e) => {{
                card.style.opacity = '1';
                
                // Calculate new position
                const container = document.getElementById('matrixContainer');
                const rect = container.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                
                // Constrain to bounds
                const newX = Math.max(5, Math.min(95, x));
                const newY = Math.max(5, Math.min(95, y));
                
                card.style.left = newX + '%';
                card.style.top = newY + '%';
                
                // Update position in database
                updatePosition(initiative.id, newX, newY);
            }});
            
            // Click to edit
            card.addEventListener('click', (e) => {{
                if (!isCreatingNew) {{
                    openEditModal(initiative);
                }}
            }});
            
            return card;
        }}
        
        function renderCards() {{
            const container = document.getElementById('cardsContainer');
            container.innerHTML = '';
            initiatives.forEach(init => {{
                container.appendChild(createCard(init));
            }});
        }}
        
        function addNewCard() {{
            isCreatingNew = true;
            const container = document.getElementById('matrixContainer');
            
            // Create temporary card
            const tempCard = document.createElement('div');
            tempCard.className = 'initiative-card green';
            tempCard.style.position = 'absolute';
            tempCard.style.left = '50%';
            tempCard.style.top = '50%';
            tempCard.style.width = '150px';
            tempCard.style.transform = 'translate(-50%, -50%)';
            tempCard.style.opacity = '0.7';
            tempCard.innerHTML = '<div style="text-align: center;">Click to place</div>';
            
            container.appendChild(tempCard);
            
            // Follow mouse
            const moveCard = (e) => {{
                const rect = container.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                tempCard.style.left = Math.max(5, Math.min(95, x)) + '%';
                tempCard.style.top = Math.max(5, Math.min(95, y)) + '%';
            }};
            
            container.addEventListener('mousemove', moveCard);
            
            // Click to place
            container.addEventListener('click', function placeCard(e) {{
                const rect = container.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;
                
                container.removeEventListener('mousemove', moveCard);
                container.removeEventListener('click', placeCard);
                tempCard.remove();
                
                // Open modal for new card
                const newInit = {{
                    id: 'new',
                    title: 'New Initiative',
                    details: '',
                    category: 'Strategic/Process',
                    color: 'green',
                    x: Math.max(5, Math.min(95, x)),
                    y: Math.max(5, Math.min(95, y))
                }};
                
                openEditModal(newInit);
                isCreatingNew = false;
            }});
        }}
        
        function openEditModal(initiative) {{
            document.getElementById('editModal').style.display = 'block';
            document.getElementById('editId').value = initiative.id;
            document.getElementById('editTitle').value = initiative.title;
            document.getElementById('editDetails').value = initiative.details || '';
            document.getElementById('editCategory').value = initiative.category;
            document.getElementById('editColor').value = initiative.color;
        }}
        
        function closeEditModal() {{
            document.getElementById('editModal').style.display = 'none';
        }}
        
        function saveEdit() {{
            const id = document.getElementById('editId').value;
            const title = document.getElementById('editTitle').value;
            const details = document.getElementById('editDetails').value;
            const category = document.getElementById('editCategory').value;
            const color = document.getElementById('editColor').value;
            
            // Send update to Streamlit
            if (id === 'new') {{
                const newInit = initiatives.find(i => i.id === 'new');
                window.parent.postMessage({{
                    type: 'create',
                    data: {{
                        title: title,
                        details: details,
                        category: category,
                        color: color,
                        x: newInit.x,
                        y: newInit.y
                    }}
                }}, '*');
            }} else {{
                window.parent.postMessage({{
                    type: 'update',
                    data: {{
                        id: id,
                        title: title,
                        details: details,
                        category: category,
                        color: color
                    }}
                }}, '*');
            }}
            
            closeEditModal();
        }}
        
        function deleteCard() {{
            const id = document.getElementById('editId').value;
            if (id !== 'new') {{
                window.parent.postMessage({{
                    type: 'delete',
                    data: {{ id: id }}
                }}, '*');
            }}
            closeEditModal();
        }}
        
        function updatePosition(id, x, y) {{
            window.parent.postMessage({{
                type: 'move',
                data: {{ id: id, x: x, y: y }}
            }}, '*');
        }}
        
        // Enable drag and drop on container
        document.getElementById('matrixContainer').addEventListener('dragover', (e) => {{
            e.preventDefault();
        }});
        
        // Initial render
        renderCards();
    </script>
    """
    
    return matrix_html

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
        st.markdown("*Drag cards to reposition · Click to edit · Use + button to add new initiatives*")
        
        # Display the interactive matrix
        matrix_html = create_interactive_matrix()
        components.html(matrix_html, height=800, scrolling=False)
        
        # Quick stats row
        df = get_initiatives_from_db()
        if not df.empty:
            df['Quadrant'] = df.apply(lambda row: get_quadrant(row['x'], row['y']), axis=1)
            
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