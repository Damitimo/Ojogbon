"""
AI Resume Generator - Streamlit Web Interface
"""
import streamlit as st
import os
from pathlib import Path
import json
from dotenv import load_dotenv
import sys
import uuid
import time
import shutil
from datetime import datetime
from resume_generator import ResumeGenerator
from profile_manager import UserProfile, ProfileManager, Education, Experience, Project
from export_handler import ResumeExporter

# Add the current directory to the path so we can import from the same directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create data directory if it doesn't exist
DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / 'resume_history.json'
BACKUP_DIR = DATA_DIR / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = DATA_DIR / 'settings.json'

# Page config
st.set_page_config(
    page_title="AI Resume Generator",
    page_icon="📄",
    layout="wide"
)

# Helper functions for API key persistence
CONFIG_FILE = Path(".api_config.json")

def load_api_key():
    """Load API key from config file or environment"""
    # First try environment variable
    env_key = os.getenv('ANTHROPIC_API_KEY', '')
    if env_key:
        return env_key
    
    # Then try config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('api_key', '')
        except:
            return ''
    return ''

def save_api_key(api_key):
    """Save API key to config file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'api_key': api_key}, f)
        return True
    except:
        return False

def load_settings():
    """Load application settings from file"""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}

def save_settings(settings):
    """Save application settings to file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_resume_history():
    """Load resume history from file"""
    try:
        if not HISTORY_FILE.exists():
            return []
            
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
            
        # Ensure each entry has required fields
        for item in history:
            if not isinstance(item, dict):
                continue
                
            item.setdefault('id', str(uuid.uuid4()))
            item.setdefault('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            item.setdefault('job_title', 'Untitled')
            item.setdefault('company', '')
            item.setdefault('job_description', '')
            item.setdefault('resume', {})
            
        return history
        
    except (json.JSONDecodeError, Exception) as e:
        st.error(f"Error loading resume history: {e}")
        return []

# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = None  # No default profile - users must create or load their own
if 'generated_resume' not in st.session_state:
    st.session_state.generated_resume = None
if 'resume_history' not in st.session_state:
    st.session_state.resume_history = load_resume_history()
if 'current_resume_index' not in st.session_state:
    st.session_state.current_resume_index = -1
if 'api_key' not in st.session_state:
    st.session_state.api_key = load_api_key()
    print(f"DEBUG: Loaded API key from config: {bool(st.session_state.api_key)}, length: {len(st.session_state.api_key) if st.session_state.api_key else 0}")
if 'form_counter' not in st.session_state:
    st.session_state.form_counter = 0
if 'current_profile_name' not in st.session_state:
    st.session_state.current_profile_name = None

# Initialize managers EARLY - before auto-loading
profile_manager = ProfileManager()
exporter = ResumeExporter()

# Profile loading - users must explicitly choose their profile
if 'profile_loaded' not in st.session_state:
    st.session_state.profile_loaded = False

# Ensure all history items have unique IDs
for i, item in enumerate(st.session_state.resume_history):
    if not isinstance(item, dict):
        continue
    if 'id' not in item:
        item['id'] = str(uuid.uuid4())
    # Ensure timestamp exists
    if 'timestamp' not in item:
        item['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if 'api_key_saved' not in st.session_state:
    st.session_state.api_key_saved = bool(load_api_key())
if 'editing_api_key' not in st.session_state:
    st.session_state.editing_api_key = not st.session_state.api_key_saved
if 'show_profile_editor' not in st.session_state:
    st.session_state.show_profile_editor = False
if 'editing_items' not in st.session_state:
    st.session_state.editing_items = {}

def auto_save_profile():
    """Automatically save the current profile to file"""
    if st.session_state.current_profile_name and st.session_state.profile:
        try:
            profile_manager.create_profile(
                st.session_state.current_profile_name, 
                st.session_state.profile, 
                replace=True
            )
            return True
        except Exception as e:
            st.error(f"Auto-save failed: {str(e)}")
            return False
    return False

def save_resume_history():
    """Save resume history to a file"""
    if 'resume_history' not in st.session_state:
        return
        
    try:
        # Create a clean copy of the history with all data
        history_to_save = []
        for item in st.session_state.resume_history:
            if not isinstance(item, dict):
                continue
                
            item_copy = item.copy()
            
            # Make sure we have required fields
            item_copy.setdefault('id', str(uuid.uuid4()))
            item_copy.setdefault('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            item_copy.setdefault('job_title', 'Untitled')
            item_copy.setdefault('company', '')
            item_copy.setdefault('job_description', '')
            
            history_to_save.append(item_copy)
        
        # Save to a temporary file first
        temp_file = f"{HISTORY_FILE}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(history_to_save, f, indent=2, default=str)
            
        # Atomically replace the old file
        if os.path.exists(temp_file):
            if HISTORY_FILE.exists():
                os.replace(temp_file, HISTORY_FILE)
            else:
                shutil.move(temp_file, HISTORY_FILE)
                
    except Exception as e:
        st.error(f"Error saving resume history: {e}")
        try:
            with open(HISTORY_FILE, 'w') as f:
                json.dump([], f)
        except:
            pass

def create_backup():
    """Create a backup of the history file"""
    try:
        if not HISTORY_FILE.exists():
            return
            
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = BACKUP_DIR / f"resume_history_{timestamp}.json"
        shutil.copy2(HISTORY_FILE, backup_file)
        
        # Keep only the last 5 backups
        backups = sorted(BACKUP_DIR.glob('resume_history_*.json'), key=os.path.getmtime)
        for old_backup in backups[:-5]:
            try:
                os.remove(old_backup)
            except:
                pass
    except Exception as e:
        print(f"Warning: Could not create backup: {e}")

def main():
    # More aggressive scroll preservation
    st.markdown("""
    <script>
    // Continuously save scroll position
    let scrollTimer;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(function() {
            sessionStorage.setItem('scrollPos', window.scrollY);
        }, 50);
    });
    
    // Save on any click
    document.addEventListener('click', function() {
        sessionStorage.setItem('scrollPos', window.scrollY);
    });
    
    // Restore scroll position immediately and repeatedly
    function restoreScroll() {
        const scrollPos = sessionStorage.getItem('scrollPos');
        if (scrollPos !== null && scrollPos !== '0') {
            window.scrollTo(0, parseInt(scrollPos));
        }
    }
    
    // Try multiple times to ensure it works
    restoreScroll();
    setTimeout(restoreScroll, 50);
    setTimeout(restoreScroll, 100);
    setTimeout(restoreScroll, 200);
    setTimeout(restoreScroll, 300);
    
    // Also try on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', restoreScroll);
    }
    </script>
    """, unsafe_allow_html=True)
    
    st.title("🤖 AI Resume Generator")
    st.markdown("**Just paste a job description → AI generates a complete resume automatically!**")
    
    # Profile Management Navbar with styling
    st.markdown("""
    <style>
    .navbar-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    /* Fix status container height to match buttons */
    div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] > div[data-testid="column"] > div[data-testid="stMarkdownContainer"] {
        display: flex;
        align-items: center;
    }
    /* Adjust alert/info box padding */
    .stAlert {
        padding: 0.5rem 0.75rem !important;
        margin: 0 !important;
    }
    .stAlert > div {
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    profiles = profile_manager.list_profiles()
    
    # Create navbar with profile dropdown and action buttons
    if st.session_state.show_profile_editor:
        # Show back button when editing profile
        navbar_col1, navbar_col2 = st.columns([1, 11])
        with navbar_col1:
            if st.button("⬅️ Back", key="navbar_back", use_container_width=True):
                st.session_state.show_profile_editor = False
                st.rerun()
        with navbar_col2:
            if st.session_state.current_profile_name:
                st.info(f"📝 **Editing Profile:** {st.session_state.current_profile_name}")
            else:
                st.info(f"📝 **Creating New Profile** - Remember to save after filling in your details")
    else:
        # Adjust columns based on whether profile is loaded (to show delete button)
        if st.session_state.current_profile_name:
            navbar_col1, navbar_col2, navbar_col3, navbar_col4, navbar_col5 = st.columns([3, 1, 1, 1, 5])
        else:
            navbar_col1, navbar_col2, navbar_col3, navbar_col4 = st.columns([3, 1, 1, 6])
        
        with navbar_col1:
            # Profile dropdown
            current_profile = st.session_state.current_profile_name if st.session_state.current_profile_name else None
            
            if profiles:
                profile_options = ['-- No Profile Loaded --'] + profiles
                default_index = 0
                if current_profile and current_profile in profiles:
                    default_index = profiles.index(current_profile) + 1
                
                selected_profile = st.selectbox(
                    "Profile",
                    options=profile_options,
                    index=default_index,
                    key="navbar_profile_selector",
                    label_visibility="collapsed"
                )
                
                # Load profile when selection changes
                if selected_profile != '-- No Profile Loaded --' and selected_profile != current_profile:
                    try:
                        st.session_state.profile = profile_manager.load_profile(selected_profile)
                        st.session_state.current_profile_name = selected_profile
                        st.session_state.profile_loaded = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading profile: {e}")
            else:
                st.selectbox(
                    "Profile",
                    options=['-- No Profiles Available --'],
                    key="navbar_profile_selector_empty",
                    disabled=True,
                    label_visibility="collapsed"
                )
        
        with navbar_col2:
            # Edit Profile button
            if st.button("✏️ Edit", key="navbar_edit", disabled=st.session_state.profile is None, use_container_width=True):
                st.session_state.show_profile_editor = True
                st.rerun()
        
        with navbar_col3:
            # New Profile button
            if st.button("➕ New Profile", key="navbar_new", use_container_width=True):
                st.session_state.profile = profile_manager.create_default_profile()
                st.session_state.current_profile_name = None
                st.session_state.profile_loaded = False
                st.session_state.show_profile_editor = True
                st.rerun()
        
        # Show delete button only if profile is loaded
        if st.session_state.current_profile_name:
            with navbar_col4:
                # Delete Profile button
                if st.button("🗑️ Delete", key="navbar_delete", use_container_width=True):
                    if st.session_state.get('confirm_delete_navbar'):
                        # Confirmed - delete the profile
                        if profile_manager.delete_profile(st.session_state.current_profile_name):
                            deleted_name = st.session_state.current_profile_name
                            st.session_state.profile = None
                            st.session_state.current_profile_name = None
                            st.session_state.profile_loaded = False
                            st.session_state.confirm_delete_navbar = False
                            st.success(f"✅ Deleted profile: {deleted_name}")
                            st.rerun()
                        else:
                            st.error("Failed to delete profile")
                    else:
                        # First click - ask for confirmation
                        st.session_state.confirm_delete_navbar = True
                        st.rerun()
            
            with navbar_col5:
                # Show current profile status or delete confirmation
                if st.session_state.get('confirm_delete_navbar'):
                    st.markdown(f"""
                    <div style="background-color: #FFF3CD; border: 1px solid #FFE69C; border-radius: 0.375rem; padding: 0.5rem 0.75rem; display: flex; align-items: center; height: 38px;">
                        <span style="color: #664D03;">⚠️ Click Delete again to confirm deletion of '{st.session_state.current_profile_name}'</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #D1E7DD; border: 1px solid #A3CFBB; border-radius: 0.375rem; padding: 0.5rem 0.75rem; display: flex; align-items: center; height: 38px;">
                        <span style="color: #0A3622;">👤 <strong>Loaded:</strong> {st.session_state.current_profile_name}</span>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            with navbar_col4:
                # Show warning when no profile is loaded
                st.markdown("""
                <div style="background-color: #FFF3CD; border: 1px solid #FFE69C; border-radius: 0.375rem; padding: 0.5rem 0.75rem; display: flex; align-items: center; height: 38px;">
                    <span style="color: #664D03;">⚠️ <strong>No profile loaded</strong> - Create or select a profile</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # Sidebar for API key and profile management
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key section with Save/Edit functionality
        if st.session_state.editing_api_key:
            api_key_input = st.text_input(
                "Claude API Key",
                value=st.session_state.api_key,
                type="password",
                help="Enter your Anthropic Claude API key. Get one at https://console.anthropic.com/settings/keys",
                key="api_key_input"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", key="save_api_key", use_container_width=True):
                    if api_key_input:
                        if save_api_key(api_key_input):
                            st.session_state.api_key = api_key_input
                            st.session_state.api_key_saved = True
                            st.session_state.editing_api_key = False
                            st.success("✅ API key saved!")
                            st.rerun()
                        else:
                            st.error("Failed to save API key")
                    else:
                        st.error("Please enter an API key")
            with col2:
                if st.button("❌ Cancel", key="cancel_api_key", use_container_width=True):
                    st.session_state.editing_api_key = False
                    st.rerun()
        else:
            # Show masked API key when saved
            if st.session_state.api_key:
                masked_key = st.session_state.api_key[:8] + "..." + st.session_state.api_key[-4:] if len(st.session_state.api_key) > 12 else "***"
                st.text_input(
                    "Claude API Key",
                    value=masked_key,
                    disabled=True,
                    help="API key is saved. Click Edit to change.",
                    key="api_key_display"
                )
                if st.button("✏️ Edit API Key", key="edit_api_key", use_container_width=True):
                    st.session_state.editing_api_key = True
                    st.rerun()
            else:
                st.text_input(
                    "Claude API Key",
                    value="",
                    disabled=True,
                    help="Click below to add your API key",
                    key="api_key_empty"
                )
                if st.button("➕ Add API Key", key="add_api_key", use_container_width=True):
                    st.session_state.editing_api_key = True
                    st.rerun()
        
        if not st.session_state.api_key or st.session_state.editing_api_key:
            st.warning("⚠️ Please enter and save your Claude API key to use the generator")
        
        st.divider()
        
        # History Section
        st.subheader("📜 Resume History")
        
        if st.session_state.resume_history:
            # Navigation buttons
            nav_cols = st.columns(2)
            with nav_cols[0]:
                prev_disabled = st.session_state.current_resume_index >= len(st.session_state.resume_history) - 1
                if st.button("⏪ Older", disabled=prev_disabled, use_container_width=True):
                    st.session_state.current_resume_index += 1
                    st.rerun()
            with nav_cols[1]:
                next_disabled = st.session_state.current_resume_index <= 0
                if st.button("Newer ⏩", disabled=next_disabled, use_container_width=True):
                    st.session_state.current_resume_index -= 1
                    st.rerun()
            
            # History list in scrollable container
            with st.container(height=400):
                st.write("Recent Resumes:")
                for idx, item in enumerate(st.session_state.resume_history):
                    is_current = idx == st.session_state.current_resume_index
                    job_title = item.get('job_title', 'Untitled')
                    company = f" at {item['company']}" if item.get('company') else ""
                    timestamp = item.get('timestamp', '')
                    
                    # Create a simple layout without nested columns for sidebar compatibility
                    # Main history item button
                    display_text = f"{job_title}{company}"
                    if len(display_text) > 25:  # Truncate long titles
                        display_text = display_text[:22] + "..."
                    
                    # Display title, edit, and delete in separate columns (no nesting)
                    col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
                    
                    with col1:
                        if st.button(
                            display_text,
                            key=f"history_{idx}",
                            type="primary" if is_current else "secondary",
                            use_container_width=True
                        ):
                            st.session_state.current_resume_index = idx
                            # Load both resume and JD
                            if 'job_description' in item and item['job_description']:
                                st.session_state["history_jd"] = item['job_description']
                            if 'resume' in item and item['resume']:
                                st.session_state.generated_resume = item['resume']
                            st.rerun()
                        
                        # Show timestamp below the button
                        if timestamp:
                            st.caption(f"Saved: {timestamp}")
                    
                    with col2:
                        # Edit button
                        if st.button("✏️", key=f"edit_history_{idx}", help="Edit history item name", use_container_width=True):
                            st.session_state[f"editing_history_{idx}"] = True
                    
                    with col3:
                        # Delete button
                        if st.button("🗑️", key=f"delete_history_{idx}", help="Delete history item", use_container_width=True):
                            # Remove the item from history
                            del st.session_state.resume_history[idx]
                            # Adjust current index if necessary
                            if st.session_state.current_resume_index >= len(st.session_state.resume_history):
                                st.session_state.current_resume_index = max(0, len(st.session_state.resume_history) - 1)
                            # Save updated history
                            save_resume_history()
                            st.rerun()
                    
                    # Handle editing mode for this history item
                    if st.session_state.get(f"editing_history_{idx}", False):
                        with st.expander(f"Edit History Item #{idx + 1}", expanded=True):
                            new_title = st.text_input(
                                "Job Title", 
                                value=job_title, 
                                key=f"edit_title_{idx}"
                            )
                            new_company = st.text_input(
                                "Company", 
                                value=item.get('company', ''), 
                                key=f"edit_company_{idx}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.button("💾 Save", key=f"save_edit_{idx}"):
                                    # Update the history item
                                    st.session_state.resume_history[idx]['job_title'] = new_title or 'Untitled'
                                    st.session_state.resume_history[idx]['company'] = new_company or ''
                                    # Save to file
                                    save_resume_history()
                                    # Clear editing state
                                    del st.session_state[f"editing_history_{idx}"]
                                    st.success("✅ History item updated!")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_edit_{idx}"):
                                    del st.session_state[f"editing_history_{idx}"]
                                    st.rerun()
        else:
            st.info("No resume history yet. Generate a resume to see it here.")
    
    # Main content area
    if st.session_state.show_profile_editor:
        # Show profile editor
        create_profile_tab()
    elif st.session_state.profile is None and not st.session_state.show_profile_editor:
        # Welcome screen for new users
        st.header("👋 Welcome to AI Resume Generator!")
        st.markdown("### Get Started")
        st.info("""
        **To use this application:**
        1. 👆 Use the **navigation bar above** to **create a new profile** or **load an existing profile**
        2. Fill in your professional information (education, experience, skills, etc.)
        3. Save your profile with a name
        4. Generate tailored resumes for any job description!
        
        Each user should create their own profile - this allows multiple people to use the software with their own information.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Create Your Profile", type="primary", use_container_width=True):
                st.session_state.profile = profile_manager.create_default_profile()
                st.session_state.current_profile_name = None
                st.session_state.profile_loaded = False
                st.session_state.show_profile_editor = True
                st.rerun()
        
        with col2:
            profiles = profile_manager.list_profiles()
            if profiles:
                if st.button("📂 Load Existing Profile", use_container_width=True):
                    st.info("👆 Use the dropdown in the navbar above to select and load a profile")
    else:
        # Two-column layout: Generate (left) and Results (right)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            generate_resume_section()
        
        with col2:
            if st.session_state.generated_resume:
                view_export_section()
            else:
                st.info("👈 Paste a job description and click Generate to see your tailored resume here")


def create_profile_tab():
    """Tab for creating/editing user profile"""
    st.header("Create Your Master Profile")
    st.markdown("Fill in all your information. The AI will select and tailor relevant parts for each job.")
    
    if st.session_state.profile is None:
        st.info("👈 Create a new profile or load an existing one from the sidebar")
        return
    
    profile = st.session_state.profile
    
    # Personal Information
    with st.expander("👤 Personal Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            profile.personal_info['name'] = st.text_input("Full Name*", value=profile.personal_info.get('name', ''))
            profile.personal_info['email'] = st.text_input("Email*", value=profile.personal_info.get('email', ''))
            profile.personal_info['phone'] = st.text_input("Phone", value=profile.personal_info.get('phone', ''))
            profile.personal_info['location'] = st.text_input("Location", value=profile.personal_info.get('location', ''))
        
        with col2:
            profile.personal_info['linkedin'] = st.text_input("LinkedIn URL", value=profile.personal_info.get('linkedin', ''))
            profile.personal_info['github'] = st.text_input("GitHub URL", value=profile.personal_info.get('github', ''))
            profile.personal_info['portfolio'] = st.text_input("Portfolio URL", value=profile.personal_info.get('portfolio', ''))
    
    # Summary (optional - will be generated)
    with st.expander("📋 Professional Summary (Optional)", expanded=False):
        st.info("💡 You can write a general summary here, but the AI will generate tailored summaries for each job.")
        profile.summary = st.text_area(
            "Professional Summary",
            value=profile.summary,
            height=100,
            placeholder="Optional: Write a general professional summary about yourself..."
        )

    # My Story section for personal narrative
    with st.expander("📝 My Story (Optional - used for cover letters)", expanded=False):
        st.info("💡 Share your personal story, motivations, and key career themes here. The AI will use this narrative when generating cover letters or responses about why you want to work somewhere.")
        profile.my_story = st.text_area(
            "Your Story",
            value=getattr(profile, 'my_story', ''),
            height=200,
            placeholder="Explain your career journey, motivations, and personal values...\n• Why do you do the work you do?\n• What impact do you want to make?\n• Key turning points or experiences."
        )
    
    # Education
    with st.expander("🎓 Education", expanded=True):
        st.markdown('<div id="education-section"></div>', unsafe_allow_html=True)
        st.subheader("Education History")
        
        # Display existing education
        for idx, edu in enumerate(profile.education):
            edit_key = f"edit_edu_{idx}"
            
            if st.session_state.editing_items.get(edit_key):
                # Edit mode
                with st.form(f"edit_edu_form_{idx}"):
                    st.markdown(f"**Edit Education #{idx + 1}**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        degree = st.text_input("Degree*", value=edu.degree)
                        institution = st.text_input("Institution*", value=edu.institution)
                        location = st.text_input("Location", value=edu.location or "")
                    
                    with col2:
                        start_date = st.text_input("Start Date*", value=edu.start_date)
                        end_date = st.text_input("End Date*", value=edu.end_date)
                        gpa = st.text_input("GPA", value=edu.gpa or "")
                    
                    achievements = st.text_area(
                        "Key Achievements (optional - 3 bullets max)",
                        value='\n'.join(edu.achievements) if edu.achievements else "",
                        height=120,
                        placeholder="• Achievement 1\n• Achievement 2\n• Achievement 3"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if degree and institution and start_date and end_date:
                                # Process achievements - handle both bullet and non-bullet input
                                achievement_list = []
                                for line in achievements.split('\n'):
                                    line = line.strip()
                                    if line:
                                        # Remove existing bullet if present, then add it back
                                        if line.startswith('•'):
                                            line = line[1:].strip()
                                        achievement_list.append('• ' + line)
                                
                                profile.education[idx] = Education(
                                    degree=degree,
                                    institution=institution,
                                    location=location,
                                    start_date=start_date,
                                    end_date=end_date,
                                    gpa=gpa if gpa else None,
                                    achievements=achievement_list[:3]  # Limit to 3 achievements
                                )
                                st.session_state.editing_items.pop(edit_key, None)
                                auto_save_profile()
                                st.success("✅ Updated and profile saved!")
                                st.rerun()  # Rerun to show updated view mode
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.editing_items.pop(edit_key, None)
                            st.rerun()  # Rerun to show view mode
            else:
                # View mode
                st.markdown(f"**Education #{idx + 1}**")
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"{edu.degree} - {edu.institution}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_btn_edu_{idx}", use_container_width=True):
                        st.session_state.editing_items[edit_key] = True
                        st.rerun()  # Keep rerun for edit button to show form
                
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_edu_{idx}", use_container_width=True):
                        profile.education.pop(idx)
                        st.rerun()
        
        # Add new education
        st.markdown("---")
        if st.button("➕ Add Education", key="add_education_btn", type="primary"):
            st.session_state.editing_items["add_new_education"] = True
            st.rerun()
        
        if st.session_state.editing_items.get("add_new_education"):
            with st.form(f"add_education_{st.session_state.form_counter}"):
                st.markdown("**Add New Education**")
                col1, col2 = st.columns(2)
                
                with col1:
                    degree = st.text_input("Degree*", placeholder="e.g., Bachelor of Science in Computer Science")
                    institution = st.text_input("Institution*", placeholder="e.g., University of California")
                    location = st.text_input("Location", placeholder="e.g., Berkeley, CA")
                
                with col2:
                    start_date = st.text_input("Start Date*", placeholder="e.g., Sep 2020")
                    end_date = st.text_input("End Date*", placeholder="e.g., May 2024")
                    gpa = st.text_input("GPA (optional)", placeholder="e.g., 3.8/4.0")
                
                achievements = st.text_area(
                    "Key Achievements (optional - 3 bullets max)",
                    height=120,
                    placeholder="• Achievement 1\n• Achievement 2\n• Achievement 3"
                )
                
                st.markdown("---")  # Add separator
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save", type="primary", use_container_width=True):
                        if degree and institution and start_date and end_date:
                            # Process achievements - handle both bullet and non-bullet input
                            achievement_list = []
                            for line in achievements.split('\n'):
                                line = line.strip()
                                if line:
                                    # Remove existing bullet if present, then add it back
                                    if line.startswith('•'):
                                        line = line[1:].strip()
                                    achievement_list.append('• ' + line)
                            
                            new_edu = Education(
                                degree=degree,
                                institution=institution,
                                location=location,
                                start_date=start_date,
                                end_date=end_date,
                                gpa=gpa if gpa else None,
                                achievements=achievement_list[:3]  # Limit to 3 achievements
                            )
                            profile.education.append(new_edu)
                            st.session_state.form_counter += 1
                            st.session_state.editing_items.pop("add_new_education", None)
                            auto_save_profile()
                            st.success("✅ Education added and profile saved!")
                            st.rerun()
                        else:
                            st.error("Please fill in all required fields")
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.editing_items.pop("add_new_education", None)
                        st.rerun()
    
    # Work Experience
    with st.expander("💼 Work Experience", expanded=True):
        st.markdown('<div id="experience-section"></div>', unsafe_allow_html=True)
        st.subheader("Work Experience")
        
        # Display existing experiences
        st.info(f"📊 Showing {len(profile.experience)} work experience(s)")
        for idx, exp in enumerate(profile.experience):
            edit_key = f"edit_exp_{idx}"
            
            if st.session_state.editing_items.get(edit_key):
                # Edit mode
                with st.form(f"edit_exp_form_{idx}"):
                    st.markdown(f"**Edit Experience #{idx + 1}**")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        title = st.text_input("Job Title*", value=exp.title)
                        company = st.text_input("Company*", value=exp.company)
                        location = st.text_input("Location", value=exp.location or "")
                    
                    with col2:
                        start_date = st.text_input("Start Date*", value=exp.start_date)
                        end_date = st.text_input("End Date*", value=exp.end_date)
                    
                    description = st.text_area(
                        "Responsibilities",
                        value='\n'.join(exp.description) if exp.description else "",
                        height=150
                    )
                    
                    skills_used = st.text_input(
                        "Skills Used",
                        value=', '.join(exp.skills_used) if exp.skills_used else ""
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if title and company and start_date and end_date:
                                desc_list = [line.strip() for line in description.split('\n') if line.strip()] if description else []
                                skills_list = [s.strip() for s in skills_used.split(',') if s.strip()] if skills_used else []
                                
                                profile.experience[idx] = Experience(
                                    title=title,
                                    company=company,
                                    location=location,
                                    start_date=start_date,
                                    end_date=end_date,
                                    description=desc_list,
                                    skills_used=skills_list
                                )
                                st.session_state.editing_items.pop(edit_key, None)
                                auto_save_profile()
                                st.success("✅ Updated and profile saved!")
                                st.rerun()  # Rerun to show updated view mode
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.editing_items.pop(edit_key, None)
                            st.rerun()  # Rerun to show view mode
            else:
                # View mode
                st.markdown(f"**Experience #{idx + 1}**")
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"{exp.title} at {exp.company}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_btn_exp_{idx}", use_container_width=True):
                        st.session_state.editing_items[edit_key] = True
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_exp_{idx}", use_container_width=True):
                        profile.experience.pop(idx)
                        st.rerun()
        
        # Add new experience
        st.markdown("---")
        if st.button("➕ Add Experience", key="add_experience_btn", type="primary"):
            st.session_state.editing_items["add_new_experience"] = True
            st.rerun()
        
        if st.session_state.editing_items.get("add_new_experience"):
            with st.form(f"add_experience_{st.session_state.form_counter}"):
                st.markdown("**Add New Experience**")
                st.info("💡 Tip: Leave responsibilities and skills blank - AI will generate them based on the job description")
                col1, col2 = st.columns(2)
                
                with col1:
                    title = st.text_input("Job Title*", placeholder="e.g., Software Engineer")
                    company = st.text_input("Company*", placeholder="e.g., Google")
                    location = st.text_input("Location", placeholder="e.g., Mountain View, CA")
                
                with col2:
                    start_date = st.text_input("Start Date*", placeholder="e.g., Jan 2022")
                    end_date = st.text_input("End Date*", placeholder="e.g., Present")
                
                description = st.text_area(
                    "Responsibilities (optional - AI will generate from JD)",
                    height=150,
                    placeholder="Leave blank for AI to generate, or enter your own:\n• Led development of...\n• Implemented features...\n• Collaborated with..."
                )
                
                skills_used = st.text_input(
                    "Skills Used (optional - AI will generate from JD)",
                    placeholder="e.g., Python, React, AWS, Docker - or leave blank"
                )
                
                st.markdown("---")  # Add separator
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save", type="primary", use_container_width=True):
                        if title and company and start_date and end_date:
                            desc_list = [line.strip() for line in description.split('\n') if line.strip()] if description else ["Relevant experience to be tailored based on job description"]
                            skills_list = [s.strip() for s in skills_used.split(',') if s.strip()] if skills_used else []
                            
                            new_exp = Experience(
                                title=title,
                                company=company,
                                location=location,
                                start_date=start_date,
                                end_date=end_date,
                                description=desc_list,
                                skills_used=skills_list
                            )
                            profile.experience.append(new_exp)
                            st.session_state.form_counter += 1
                            st.session_state.editing_items.pop("add_new_experience", None)
                            auto_save_profile()
                            st.success("✅ Experience added and profile saved!")
                            st.rerun()
                        else:
                            st.error("Please fill in job title, company, and dates")
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.editing_items.pop("add_new_experience", None)
                        st.rerun()
    
    # Projects
    with st.expander("🚀 Projects", expanded=True):
        st.markdown('<div id="projects-section"></div>', unsafe_allow_html=True)
        st.subheader("Projects")
        
        # Display existing projects
        for idx, proj in enumerate(profile.projects):
            edit_key = f"edit_proj_{idx}"
            
            if st.session_state.editing_items.get(edit_key):
                # Edit mode
                with st.form(f"edit_proj_form_{idx}"):
                    st.markdown(f"**Edit Project #{idx + 1}**")
                    
                    name = st.text_input("Project Name*", value=proj.name)
                    description = st.text_area(
                        "Description",
                        value=proj.description or "",
                        height=100
                    )
                    technologies = st.text_input(
                        "Technologies Used",
                        value=', '.join(proj.technologies) if proj.technologies else ""
                    )
                    achievements = st.text_area(
                        "Key Achievements",
                        value='\n'.join(proj.achievements) if proj.achievements else "",
                        height=100
                    )
                    url = st.text_input("Project URL", value=proj.url or "")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("💾 Save", use_container_width=True):
                            if name:
                                tech_list = [t.strip() for t in technologies.split(',') if t.strip()] if technologies else []
                                achievement_list = [line.strip() for line in achievements.split('\n') if line.strip()] if achievements else []
                                
                                profile.projects[idx] = Project(
                                    name=name,
                                    description=description if description else "Project details to be generated",
                                    technologies=tech_list,
                                    achievements=achievement_list,
                                    url=url if url else None
                                )
                                st.session_state.editing_items.pop(edit_key, None)
                                auto_save_profile()
                                st.success("✅ Updated and profile saved!")
                                st.rerun()  # Rerun to show updated view mode
                    with col_cancel:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.editing_items.pop(edit_key, None)
                            st.rerun()  # Rerun to show view mode
            else:
                # View mode
                st.markdown(f"**Project #{idx + 1}**")
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"{proj.name}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_btn_proj_{idx}", use_container_width=True):
                        st.session_state.editing_items[edit_key] = True
                        st.rerun()
                
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_proj_{idx}", use_container_width=True):
                        profile.projects.pop(idx)
                        st.rerun()
        
        # Add new project
        st.markdown("---")
        if st.button("➕ Add Project", key="add_project_btn", type="primary"):
            st.session_state.editing_items["add_new_project"] = True
            st.rerun()
        
        if st.session_state.editing_items.get("add_new_project"):
            with st.form(f"add_project_{st.session_state.form_counter}"):
                st.markdown("**Add New Project**")
                st.info("💡 Tip: AI will generate project details based on the job description")
                
                name = st.text_input("Project Name*", placeholder="e.g., E-commerce Platform")
                description = st.text_area(
                    "Description (optional - AI will generate)",
                    height=100,
                    placeholder="AI will generate based on job description, or enter your own..."
                )
                technologies = st.text_input(
                    "Technologies Used (optional - AI will generate)",
                    placeholder="e.g., React, Node.js, MongoDB - or leave blank"
                )
                achievements = st.text_area(
                    "Key Achievements (optional - AI will generate)",
                    height=100,
                    placeholder="• AI will generate achievements\n• Or enter your own"
                )
                url = st.text_input("Project URL (optional)", placeholder="e.g., https://github.com/...")
                
                st.markdown("---")  # Add separator
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("💾 Save", type="primary", use_container_width=True):
                        if name:
                            tech_list = [t.strip() for t in technologies.split(',') if t.strip()] if technologies else []
                            achievement_list = [line.strip() for line in achievements.split('\n') if line.strip()] if achievements else []
                            
                            new_proj = Project(
                                name=name,
                                description=description if description else "Project details to be generated",
                                technologies=tech_list,
                                achievements=achievement_list,
                                url=url if url else None
                            )
                            profile.projects.append(new_proj)
                            st.session_state.form_counter += 1
                            st.session_state.editing_items.pop("add_new_project", None)
                            auto_save_profile()
                            st.success("✅ Project added and profile saved!")
                            st.rerun()
                        else:
                            st.error("Please enter a project name")
                with col_cancel:
                    if st.form_submit_button("❌ Cancel", use_container_width=True):
                        st.session_state.editing_items.pop("add_new_project", None)
                        st.rerun()
    
    # Skills
    with st.expander("🛠️ Skills", expanded=True):
        st.subheader("Skills")
        
        col1, col2 = st.columns(2)
        
        with col1:
            technical_skills = st.text_area(
                "Technical Skills (one per line or comma-separated)",
                value='\n'.join(profile.skills.get('technical', [])),
                height=150,
                placeholder="Python\nJavaScript\nReact\nAWS"
            )
            
            languages = st.text_input(
                "Programming Languages",
                value=', '.join(profile.skills.get('languages', [])),
                placeholder="Python, Java, C++"
            )
        
        with col2:
            tools = st.text_input(
                "Tools & Frameworks",
                value=', '.join(profile.skills.get('tools', [])),
                placeholder="Git, Docker, Kubernetes"
            )
            
            soft_skills = st.text_input(
                "Soft Skills",
                value=', '.join(profile.skills.get('soft_skills', [])),
                placeholder="Leadership, Communication, Problem-solving"
            )
        
        # Update skills
        profile.skills['technical'] = [s.strip() for s in technical_skills.replace(',', '\n').split('\n') if s.strip()]
        profile.skills['languages'] = [s.strip() for s in languages.split(',') if s.strip()]
        profile.skills['tools'] = [s.strip() for s in tools.split(',') if s.strip()]
        profile.skills['soft_skills'] = [s.strip() for s in soft_skills.split(',') if s.strip()]
    
    # Certifications & Awards
    with st.expander("🏆 Certifications & Awards", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            certifications = st.text_area(
                "Certifications (one per line)",
                value='\n'.join(profile.certifications),
                height=150,
                placeholder="AWS Certified Solutions Architect\nGoogle Cloud Professional"
            )
            profile.certifications = [c.strip() for c in certifications.split('\n') if c.strip()]
        
        with col2:
            awards = st.text_area(
                "Awards & Achievements (one per line)",
                value='\n'.join(profile.awards),
                height=150,
                placeholder="Dean's List\nHackathon Winner"
            )
            profile.awards = [a.strip() for a in awards.split('\n') if a.strip()]
    
    # Save Profile to File
    st.divider()
    st.markdown("### 💾 Save Profile to File")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        profile_name = st.text_input(
            "Profile Name",
            value=st.session_state.current_profile_name or "my_profile",
            placeholder="Enter a name for this profile file",
            help=f"Current profile: {st.session_state.current_profile_name or 'None'} • Use letters, numbers, and spaces only."
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("💾 Save to File", type="primary"):
            if profile_name:
                # Clean the profile name for checking
                clean_name = profile_name.strip()
                clean_name = ' '.join(clean_name.split())  # Normalize whitespace
                clean_name = clean_name.replace('.', '')
                
                # Check if profile exists
                profile_path = Path("profiles") / f"{clean_name}.json"
                
                if profile_path.exists():
                    st.warning(f"⚠️ Profile '{clean_name}' already exists!")
                    col_replace, col_version = st.columns(2)
                    
                    with col_replace:
                        if st.button("🔄 Replace Existing", type="secondary"):
                            profile_path, final_name = profile_manager.create_profile(profile_name, profile, replace=True)
                            st.session_state.profile = profile
                            st.session_state.current_profile_name = final_name
                            st.success(f"✅ Profile '{final_name}' saved to file!")
                            st.rerun()
                    
                    with col_version:
                        if st.button("📝 Save as New Version", type="primary"):
                            profile_path, final_name = profile_manager.create_profile(profile_name, profile, replace=False)
                            st.session_state.profile = profile
                            st.session_state.current_profile_name = final_name
                            st.success(f"✅ Profile '{final_name}' saved to file!")
                            st.rerun()
                else:
                    # Profile doesn't exist, save normally
                    profile_path, final_name = profile_manager.create_profile(profile_name, profile, replace=False)
                    st.session_state.profile = profile  # Update session state with current profile
                    st.session_state.current_profile_name = final_name
                    st.success(f"✅ Profile '{final_name}' saved to file!")
            else:
                st.error("Please enter a profile name")


def generate_resume_section():
    """Section for generating tailored resumes"""
    st.header("🎯 Generate Tailored Resume")
    
    if not st.session_state.api_key or not st.session_state.api_key_saved:
        st.warning("⚠️ Please enter and save your Claude API key in the sidebar")
        return
    
    profile = st.session_state.profile
    
    # Show profile status
    if profile is None:
        st.warning("⚠️ No profile loaded")
    else:
        st.success(f"✅ Profile loaded: {profile.personal_info.get('name', 'Unnamed Profile')}")
    
    st.markdown("**Paste the job description and the AI will tailor your resume to match it.**")
    st.info("💡 Your profile will be optimized for the target job while maintaining authenticity.")
    
    # Check if we're loading from history
    jd_value = st.session_state.get("history_jd") or st.session_state.get("jd_input", "")
    
    job_description = st.text_area(
        "Job Description",
        value=jd_value,
        height=400,
        placeholder="Paste the full job description here...\n\nThe AI will analyze:\n• Required skills\n• Responsibilities\n• Experience level\n• Company culture\n\nAnd tailor your resume accordingly."
    )
    
    # Clear history_jd after use
    if st.session_state.get("history_jd"):
        del st.session_state["history_jd"]
    
    # Extra Knowledge field for context-specific information
    with st.expander("🧠 Extra Knowledge (Optional)", expanded=False):
        st.info("💡 Add context-specific information that the AI should know when tailoring your resume.")
        extra_knowledge = st.text_area(
            "Additional Context",
            height=150,
            placeholder="Examples:\n• For pharmacist roles: In Nigeria we use NAFDAC instead of FDA\n• For international roles: I have work authorization for Country X\n• Industry-specific terminology: We call ' agile sprints' -> ' iteration cycles' at my company\n• Company-specific tools: We use internal tool 'X' instead of industry standard 'Y'",
            key="extra_knowledge"
        )
    
    style = "professional"  # Always use professional style
    
    # Experience Bullet Controls
    if profile and profile.experience:
        st.subheader("🎯 Experience Bullet Control")
        st.info("💡 Choose how many bullets the AI should generate for each experience section")
        
        # Initialize bullet counts in session state if not exists
        if 'experience_bullet_counts' not in st.session_state:
            st.session_state.experience_bullet_counts = {}
        
        # Display each experience with bullet counter
        experience_controls = []
        for i, exp in enumerate(profile.experience):
            company_map = ""
            if i == 0:
                company_map = " → RBC"
            elif i == 1:
                company_map = " → Gusto"
            
            col1, col2 = st.columns([0.7, 0.3])
            
            with col1:
                st.markdown(f"**Experience {i+1}:** {exp.title} at {exp.company}{company_map}")
            
            with col2:
                bullet_count = st.selectbox(
                    f"Bullets for Exp {i+1}",
                    options=[2, 3, 4, 5, 6],
                    index=3 if i not in st.session_state.experience_bullet_counts else 
                           max(0, st.session_state.experience_bullet_counts.get(i, 4) - 2),
                    key=f"bullet_count_{i}",
                    help=f"Number of bullets to generate for {exp.company}"
                )
                st.session_state.experience_bullet_counts[i] = bullet_count
    
    if st.button("🚀 Generate Resume", type="primary", use_container_width=True):
        # Check for both required inputs
        has_error = False

        if profile is None:
            st.error("❌ Please load or create a profile first")
            has_error = True
        
        if not job_description:
            st.error("❌ Please paste a job description")
            has_error = True
        
        if has_error:
            st.info("👈 Use the sidebar to create/load a profile and paste a job description above")
            return
        
        with st.spinner("🤖 AI is analyzing the job description and tailoring your resume..."):
            try:
                print(f"DEBUG: About to call ResumeGenerator with API key: {bool(st.session_state.api_key)}, length: {len(st.session_state.api_key) if st.session_state.api_key else 0}")
                generator = ResumeGenerator(api_key=st.session_state.api_key)
                tailored_resume = generator.generate_tailored_resume(
                    profile=profile,
                    job_description=job_description,
                    style=style,
                    extra_knowledge=extra_knowledge if extra_knowledge else None,
                    experience_bullet_counts=st.session_state.get('experience_bullet_counts', {})
                )
                
                st.session_state.generated_resume = tailored_resume
                st.session_state["jd_input"] = job_description  # Store for history loading
                # Extract company and job title from job description if possible
                company_name = ""
                job_title = ""
                
                if job_description:
                    import re
                    
                    # First, look for common patterns that clearly indicate company and title
                    # Common patterns for job postings
                    common_patterns = [
                        # Pattern: "[Company] is hiring a [Job Title]"
                        r'([A-Z][A-Za-z0-9&.\-\s]+?)\s+is\s+hiring\s+(?:a|an)?\s*([A-Z][A-Za-z\-\s]+?)(?:\s+to|\s+for|\s+who|\s+with|\s+in|\s+at|\s*\.|\s*$|\n)',
                        # Pattern: "[Job Title] at [Company]"
                        r'([A-Z][A-Za-z\-\s]+?)\s+at\s+([A-Z][A-Za-z0-9&.\-\s]+?)(?:\s*[,\n\.]|\s+we|\s+our|\s+is|\s+are|$)',
                        # Pattern: "[Company]: [Job Title]"
                        r'([A-Z][A-Za-z0-9&.\-\s]+?)\s*[:\-]\s*([A-Z][A-Za-z\-\s]+?)(?:\s*[,\n\.]|\s+we|\s+our|\s+is|\s+are|$)'
                    ]
                    
                    # Try common patterns first
                    for pattern in common_patterns:
                        match = re.search(pattern, job_description, re.IGNORECASE | re.MULTILINE)
                        if match and len(match.groups()) >= 2:
                            potential_company = match.group(1).strip()
                            potential_title = match.group(2).strip()
                            
                            # Clean up the company name
                            company_name = re.sub(r'[^\w\s-]', '', potential_company).strip()
                            company_name = ' '.join(company_name.split())  # Normalize whitespace
                            
                            # Clean up the job title
                            job_title = re.sub(r'[^\w\s-]', '', potential_title).strip()
                            job_title = ' '.join(job_title.split())  # Normalize whitespace
                            
                            # If we found both, we're done
                            if company_name and job_title:
                                break
                    
                    # If we didn't find both, try to find them separately
                    if not company_name or not job_title:
                        # Try to find company name in the first few lines
                        first_paragraph = job_description.split('\n')[0]
                        
                        # Look for company name in the first paragraph
                        company_matches = re.findall(r'\b([A-Z][A-Za-z0-9&.\-\s]+?)\s+(?:Inc|Ltd|LLC|Corp|Co\.|Company|Technologies|Labs)\b', first_paragraph)
                        if company_matches:
                            company_name = company_matches[0].strip()
                        else:
                            # Look for all-uppercase words that might be company names
                            all_caps = re.findall(r'\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b', first_paragraph)
                            if all_caps:
                                company_name = all_caps[0].strip()
                        
                        # Try to find job title if not found yet
                        if not job_title:
                            # Common title keywords
                            title_keywords = [
                                'intern', 'internship', 'product manager', 'software engineer', 
                                'developer', 'designer', 'analyst', 'associate', 'specialist'
                            ]
                            
                            # Look for title patterns in the first few lines
                            for line in job_description.split('\n')[:5]:
                                for keyword in title_keywords:
                                    if keyword in line.lower():
                                        # Try to extract the full title
                                        match = re.search(r'([A-Z][A-Za-z\-\s]+' + re.escape(keyword) + r'[A-Za-z\-\s]*)', line, re.IGNORECASE)
                                        if match:
                                            job_title = match.group(1).strip()
                                            break
                                if job_title:
                                    break
                    
                    # Clean up the results
                    if company_name:
                        company_name = re.sub(r'\b(?:the|a|an|in|at|for|with|and|or|but|to|of|on|by|as|is|are|was|were|be|being|been)\b', '', 
                                           company_name, flags=re.IGNORECASE).strip()
                        company_name = ' '.join(company_name.split())  # Normalize whitespace
                    
                    if job_title:
                        job_title = re.sub(r'[^\w\s-]', '', job_title).strip()
                        job_title = ' '.join(job_title.split())  # Normalize whitespace
                
                add_to_history(
                    resume_data=tailored_resume,
                    job_description=job_description,
                    company_name=company_name,
                    job_title=job_title
                )
                
                st.success("✅ Resume generated! Check the right panel →")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error generating resume: {str(e)}")
                st.info("Make sure your API key is valid and you have credits available in your Anthropic account.")

    st.divider()

    st.header("📝 Story-Based Responses")
    st.info("Leverage your ⭐ My Story to craft tailored narratives. Select what you need and the AI will build it from your story plus the job description above.")

    if not profile.my_story or not profile.my_story.strip():
        st.warning("Add content to 'My Story' in your profile to enable story-based generation.")
        return

    col_story_1, col_story_2 = st.columns(2)
    with col_story_1:
        include_why = st.checkbox("Why you want to work here", key="story_include_why")
        include_cover_letter = st.checkbox("Full cover letter", key="story_include_cover")

    with col_story_2:
        extra_story_context = st.text_area(
            "Optional extra context for story outputs",
            key="extra_story_context",
            height=120,
            placeholder="Provide nuances the AI should mention (e.g., team values you admire, specific initiatives you want to join, referral names). Leave blank if none."
        )

    st.caption("📌 At least one option must be selected to enable story generation.")

    if st.button("✨ Generate Story Content", type="primary", use_container_width=True):
        if not include_why and not include_cover_letter:
            st.error("Please select at least one story output to generate.")
            return

        if profile is None:
            st.error("❌ Please load or create a profile first")
            return

        if not job_description:
            st.error("❌ Please paste a job description above so the story can be tailored.")
            return

        with st.spinner("📖 Crafting personalised story content..."):
            try:
                generator = ResumeGenerator(api_key=st.session_state.api_key)
                story_outputs = generator.generate_story_content(
                    profile=profile,
                    job_description=job_description,
                    include_why=include_why,
                    include_cover_letter=include_cover_letter,
                    extra_knowledge=extra_story_context if extra_story_context else extra_knowledge if extra_knowledge else None
                )

                if include_why and story_outputs.get("why_you_want_to_work_here"):
                    st.subheader("Why You Want to Work Here")
                    st.write(story_outputs["why_you_want_to_work_here"])

                if include_cover_letter and story_outputs.get("cover_letter"):
                    st.subheader("Cover Letter")
                    st.write(story_outputs["cover_letter"])

                if include_why or include_cover_letter:
                    st.success("Story content generated! Scroll up to review or copy.")
            except Exception as e:
                st.error(f"❌ Error generating story content: {str(e)}")


def add_to_history(resume_data, job_description='', company_name='', job_title=''):
    """Add a generated resume and job description to the history
    
    Args:
        resume_data: The generated resume data
        job_description: The original job description text
        company_name: Optional company name
        job_title: Optional job title
    """
    if 'resume_history' not in st.session_state:
        st.session_state.resume_history = []
    
    # Create a simple entry with just what we need
    entry = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'job_description': job_description,
        'resume': resume_data,
        'job_title': job_title or 'Untitled',
        'company': company_name or ''
    }
    
    # Add to history (newest first)
    st.session_state.resume_history.insert(0, entry)
    st.session_state.current_resume_index = 0
    
    # Keep only last 20 entries
    st.session_state.resume_history = st.session_state.resume_history[:20]
    
    # Save to file
    save_resume_history()

def view_export_section():
    """Section for viewing and exporting resumes in right column"""
    st.header("📄 Generated Resume")
    
    # Get the current resume to display
    resume = None
    
    if st.session_state.get('resume_history') and st.session_state.current_resume_index >= 0:
        try:
            history_item = st.session_state.resume_history[st.session_state.current_resume_index]
            
            # Update the job description in the form if it exists
            if 'job_description' in history_item and history_item['job_description']:
                st.session_state["history_jd"] = history_item['job_description']
            
            # Get the resume data
            if 'resume' in history_item and history_item['resume']:
                resume = history_item['resume']
                
                # Update the generated resume in session state
                st.session_state.generated_resume = resume
                
                # Show the resume title and company if available
                title = history_item.get('job_title', 'Untitled')
                company = history_item.get('company', '')
                if company:
                    st.subheader(f"{title} at {company}")
                else:
                    st.subheader(title)
                    
                # Show timestamp if available
                timestamp = history_item.get('timestamp', '')
                if timestamp:
                    st.caption(f"Saved on {timestamp}")
            else:
                st.warning("No resume data found in history.")
                return
                
        except (KeyError, IndexError) as e:
            st.error("Error loading resume from history.")
            return
    
    # If no history or history loading failed, use the current generated resume if it exists
    if resume is None:
        resume = st.session_state.get('generated_resume', {})
        if not resume:
            return
    
    # Display the resume content
    if resume:
        # Personal Info
        personal = resume.get('personal_info', {})
        st.markdown(f"### {personal.get('name', 'Your Name')}")
        
        contact_info = []
        if personal.get('email'):
            contact_info.append(f"📧 {personal['email']}")
        if personal.get('phone'):
            contact_info.append(f"📱 {personal['phone']}")
        if personal.get('location'):
            contact_info.append(f"📍 {personal['location']}")
        
        if contact_info:
            st.markdown(" | ".join(contact_info))
        
        st.divider()
        
        # Summary
        if resume.get('summary'):
            st.subheader("Professional Summary")
            st.write(resume['summary'])
            st.divider()
            
        # Education - Moved to after Summary
        if resume.get('education'):
            st.subheader("Education")
            for edu in resume['education']:
                st.markdown(f"**{edu['degree']}**")
                st.markdown(f"{edu['institution']} | {edu.get('start_date', '')} - {edu.get('end_date', '').replace('Present', 'Present')}")
                if edu.get('location'):
                    st.markdown(f"📍 {edu['location']}")
                if edu.get('gpa'):
                    st.markdown(f"GPA: {edu['gpa']}")
                # Display achievements if any
                if edu.get('achievements') and len(edu['achievements']) > 0:
                    for achievement in edu['achievements']:
                        st.markdown(f"• {achievement}")
                st.write("")
            st.divider()
        
        # Experience
        if resume.get('experience'):
            st.subheader("Experience")
            for exp in resume['experience']:
                st.markdown(f"**{exp['title']}** - {exp['company']}")
                st.markdown(f"*{exp.get('start_date', '')} - {exp.get('end_date', '')}*")
                for bullet in exp.get('description', []):
                    st.markdown(f"• {bullet}")
                st.write("")
            st.divider()
        
        # Projects
        if resume.get('projects') and len(resume['projects']) > 0:
            st.subheader("Projects")
            for proj in resume['projects']:
                st.markdown(f"**{proj['name']}**")
                st.markdown(f"*{', '.join(proj['technologies'])}*")
                st.write(proj['description'])
                if proj.get('achievements'):
                    for achievement in proj['achievements']:
                        st.markdown(f"• {achievement}")
                st.write("")
            st.divider()
        
        # Skills
        if resume.get('skills'):
            st.subheader("Skills")
            skills = resume['skills']
            
            if skills.get('technical'):
                st.markdown(f"**Technical:** {', '.join(skills['technical'][:9])}")
            if skills.get('languages'):
                st.markdown(f"**Languages:** {', '.join(skills['languages'][:9])}")
            if skills.get('tools'):
                st.markdown(f"**Tools:** {', '.join(skills['tools'][:9])}")
        
        # Export options
        st.divider()
        
        st.subheader("📥 Export Options")
        
        # Export toggles
        col1, col2 = st.columns(2)
        with col1:
            include_summary = st.checkbox("Include Summary", value=False, key="export_include_summary")
        with col2:
            include_projects = st.checkbox("Include Projects", value=False, key="export_include_projects")
        
        # Filter resume data based on export options
        export_resume = resume.copy()
        if not include_summary and 'summary' in export_resume:
            del export_resume['summary']
        if not include_projects and 'projects' in export_resume:
            del export_resume['projects']
        
        # Export buttons
        st.subheader("Export Format")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 PDF", use_container_width=True, type="primary"):
                with st.spinner("Generating..."):
                    try:
                        pdf_path = exporter.export_to_pdf(export_resume)
                        with open(pdf_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=f.read(),
                                file_name=pdf_path.name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                        st.success("✅ Ready!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("📝 DOCX", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        docx_path = exporter.export_to_docx(export_resume)
                        with open(docx_path, 'rb') as f:
                            st.download_button(
                                label="⬇️ Download DOCX",
                                data=f.read(),
                                file_name=docx_path.name,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                        st.success("✅ Ready!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col3:
            if st.button("📋 TXT", use_container_width=True):
                with st.spinner("Generating..."):
                    try:
                        txt_path = exporter.export_to_txt(export_resume)
                        with open(txt_path, 'r', encoding='utf-8') as f:
                            st.download_button(
                                label="⬇️ Download TXT",
                                data=f.read(),
                                file_name=txt_path.name,
                                mime="text/plain",
                                use_container_width=True
                            )
                        st.success("✅ Ready!")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
