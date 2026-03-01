import streamlit as st
import backend
import time
import re # For password validation

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="BookTok",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (STYLING) ---
st.markdown("""
<style>
    /* Fonts */
    .title-font { font-size: 60px !important; font-weight: 800; color: #FF4B4B; text-align: center; font-family: 'Helvetica', sans-serif; }
    .quote-font { font-size: 22px; color: #888; text-align: center; font-style: italic; margin-bottom: 30px; }
    
    /* Cover Art Placeholder */
    .no-cover {
        width: 100%;
        height: 200px;
        background-color: #e0e0e0;
        color: #555;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        padding: 5px;
    }
    
    /* Buttons */
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    
    /* Grid Alignment */
    div[data-testid="column"] { text-align: center; }
    img { border-radius: 5px; transition: transform .2s; }
    img:hover { transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = 'intro'
if 'auth_mode' not in st.session_state: st.session_state.auth_mode = 'login' # login vs signup
if 'selected_book' not in st.session_state: st.session_state.selected_book = None # For detailed view

# --- HELPER FUNCTIONS ---
def validate_password(password):
    """
    Rules: At least 8 chars, 1 Upper, 1 Lower, 1 Number, 1 Special Char
    """
    if len(password) < 8: return False
    if not re.search(r"[A-Z]", password): return False
    if not re.search(r"[a-z]", password): return False
    if not re.search(r"\d", password): return False
    if not re.search(r"[ !@#$%^&*()_+\-=$$$${};':\"\\|,.<>\/?]", password): return False
    return True

def display_cover(image_url, title):
    """Renders image or a nice placeholder"""
    if image_url:
        st.image(image_url, use_container_width=True)
    else:
        st.markdown(f'<div class="no-cover">{title}<br>(No Cover)</div>', unsafe_allow_html=True)

# --- 1. INTRO PAGE ---
def intro_page():
    placeholder = st.empty()
    with placeholder.container():
        st.write("#")
        st.write("#")
        st.markdown('<p class="title-font">BookTok 📚</p>', unsafe_allow_html=True)
        st.markdown('<p class="quote-font">Welcome to your world of Fantasy...</p>', unsafe_allow_html=True)
        time.sleep(3) # Wait 3 seconds
        
    st.session_state.page = 'login'
    st.rerun()

# --- 2. LOGIN / SIGNUP PAGE ---
def login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<p class="title-font" style="font-size:40px!important;">BookTok 📚</p>', unsafe_allow_html=True)
        st.markdown('<p class="quote-font">Welcome to your world of Fantasy</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.session_state.auth_mode == 'login':
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Log In"):
                if backend.check_login(username, password):
                    st.session_state.user = username
                    st.session_state.page = 'home'
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
            
            st.write("")
            if st.button("Not a member? Sign Up"):
                st.session_state.auth_mode = 'signup'
                st.rerun()
                
        else: # Signup Mode
            st.subheader("Create Account")
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password", help="Min 8 chars, 1 Upper, 1 Lower, 1 Number, 1 Special")
            
            if st.button("Sign Up"):
                if validate_password(new_pass):
                    if backend.create_user(new_user, new_pass):
                        st.success("Account created! Please log in.")
                        st.session_state.auth_mode = 'login'
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Username taken.")
                else:
                    st.error("Password too weak! Needs 8 chars, Upper, Lower, Number, and Symbol.")
            
            st.write("")
            if st.button("Already a member? Log In"):
                st.session_state.auth_mode = 'login'
                st.rerun()

# --- 3. MAIN APP LAYOUT ---
def main_app():
    # --- SIDEBAR ---
    with st.sidebar:
        st.header(f"👤 {st.session_state.user}")
        st.markdown("---")
        if st.button("🏠 Home"):
            st.session_state.selected_book = None
            st.session_state.page = 'home'
            st.rerun()
        
        st.write("### My Library")
        if st.button("📖 To Be Read"): pass # Placeholder for future logic
        if st.button("✅ Read"): pass
        if st.button("➕ Add Reading List"): st.info("Coming soon!")
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = 'login'
            st.rerun()

    # --- DETAILED BOOK VIEW ---
    if st.session_state.selected_book:
        book = st.session_state.selected_book
        
        if st.button("← Back to Search"):
            st.session_state.selected_book = None
            st.rerun()
            
        st.markdown(f"## {book['title']}")
        
        c1, c2 = st.columns([1, 2])
        
        # Left Side: Cover
        with c1:
            display_cover(book['image_url'], book['title'])
            st.write("")
            b1, b2 = st.columns(2)
            with b1:
                if st.button("➕ TBR"):
                    backend.add_book_to_library(st.session_state.user, book, 'tbr')
                    st.toast("Added to TBR!")
            with b2:
                if st.button("✅ Read"):
                    backend.add_book_to_library(st.session_state.user, book, 'read')
                    st.toast("Marked as Read!")

        # Right Side: Details
        with c2:
            st.write(f"**Author:** {book['authors']}")
            st.write(f"**Released:** {book['published_date']}")
            st.write(f"**Rating:** ⭐ {book['rating']} ({book['rating_count']} votes)")
            st.write(f"**Genres:** {book['categories']}")
            st.markdown("### Description")
            st.write(book['description'])
        
        st.markdown("---")
        st.subheader(f"More books like '{book['title']}'")
        # Reuse search logic to find similar books based on author or genre
        sim_query = book['authors'].split(',')[0] # Search by first author
        recs = backend.search_google_books(sim_query)
        display_book_grid(recs[:5]) # Show 5 recommendations

    # --- HOME / SEARCH VIEW ---
    else:
        st.markdown('<p class="title-font" style="font-size:50px!important;">BookTok 📚</p>', unsafe_allow_html=True)
        st.markdown('<p class="quote-font">Discover your next obsession</p>', unsafe_allow_html=True)
        
        search_query = st.text_input("", placeholder="Search titles, authors, genres...")
        
        if search_query:
            if len(search_query) < 3:
                st.error("Error! Put relevant word to search for books (min 3 chars).")
            else:
                with st.spinner("Searching infinite library..."):
                    results = backend.search_google_books(search_query)
                
                if results:
                    st.write(f"Found {len(results)} books for **'{search_query}'**")
                    display_book_grid(results)
                else:
                    st.warning("No books found.")
        
        else:
            # Trending / Popular Tabs
            t1, t2 = st.tabs(["🔥 Popular & Trending", "💖 Recommended"])
            
            with t1:
                # We simulate trending by searching a popular term
                trending = backend.search_google_books("Best Sellers 2024")
                display_book_grid(trending)
            
            with t2:
                # Simulate recommended based on a genre
                recs = backend.search_google_books("Fantasy Magic")
                display_book_grid(recs)

def display_book_grid(books):
    """
    Renders books in a neat 5-column grid.
    Handles 'Click to View' logic.
    """
    # Create rows of 5
    for i in range(0, len(books), 5):
        cols = st.columns(5)
        # Fill the row
        for j in range(5):
            if i + j < len(books):
                book = books[i+j]
                with cols[j]:
                    with st.container():
                        # Cover
                        display_cover(book['image_url'], book['title'])
                        
                        # Truncate Title
                        short_title = (book['title'][:25] + '..') if len(book['title']) > 25 else book['title']
                        st.write(f"**{short_title}**")
                        
                        # View Details Button (Acts as the 'Select' trigger)
                        if st.button("View Info", key=f"btn_{book['id']}_{i+j}"):
                            st.session_state.selected_book = book
                            st.rerun()

# --- APP ROUTING ---
if st.session_state.page == 'intro':
    intro_page()
elif st.session_state.page == 'login':
    login_page()
else:
    main_app()