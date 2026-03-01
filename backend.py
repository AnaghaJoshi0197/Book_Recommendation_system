import sqlite3
import hashlib
import requests
import pandas as pd

# --- PART 1: GOOGLE BOOKS API (THE DATA) ---

def search_google_books(query):
    """
    Searches Google Books API.
    Fetched 40 results to simulate infinite scroll.
    """
    if not query:
        return []

    # Increased maxResults to 40
    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        books_clean = []
        
        if 'items' in data:
            for item in data['items']:
                info = item.get('volumeInfo', {})
                
                # Get High Quality Image if available, else thumbnail
                image_links = info.get('imageLinks', {})
                img = image_links.get('thumbnail', '')
                
                # Clean Data
                book = {
                    'id': item.get('id'),
                    'title': info.get('title', 'Unknown Title'),
                    'authors': ", ".join(info.get('authors', ['Unknown Author'])),
                    'published_date': info.get('publishedDate', 'N/A'),
                    'description': info.get('description', 'No summary available.'),
                    'rating': info.get('averageRating', 'N/A'),
                    'rating_count': info.get('ratingsCount', 0),
                    'categories': ", ".join(info.get('categories', ['General'])), # Added Genres
                    'image_url': img
                }
                books_clean.append(book)
                
        return books_clean

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def init_db():
    """Create the database tables if they don't exist"""
    conn = sqlite3.connect('booktok.db')
    c = conn.cursor()
    
    # Create Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    
    # Create Library Table (Links user to books)
    c.execute('''
        CREATE TABLE IF NOT EXISTS library (
            username TEXT,
            book_id TEXT,
            title TEXT,
            author TEXT,
            image_url TEXT,
            status TEXT, -- 'tbr' (To Be Read) or 'read'
            UNIQUE(username, book_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def make_hash(password):
    """Turn password into a secret code so we don't store it as plain text"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def create_user(username, password):
    conn = sqlite3.connect('booktok.db')
    c = conn.cursor()
    
    hashed_pw = make_hash(password)
    
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_pw))
        conn.commit()
        conn.close()
        return True # Success
    except sqlite3.IntegrityError:
        conn.close()
        return False # Username already exists

def check_login(username, password):
    conn = sqlite3.connect('booktok.db')
    c = conn.cursor()
    
    hashed_pw = make_hash(password)
    
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_pw))
    data = c.fetchall()
    conn.close()
    
    return len(data) > 0 # Returns True if user found

# --- PART 3: LIBRARY FUNCTIONS (MANAGING BOOKS) ---

def add_book_to_library(username, book_data, status):
    """Saves a book to the user's personal list"""
    conn = sqlite3.connect('booktok.db')
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT OR REPLACE INTO library (username, book_id, title, author, image_url, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, book_data['id'], book_data['title'], book_data['authors'], book_data['image_url'], status))
        conn.commit()
        print(f"Added {book_data['title']} to {status}")
    except Exception as e:
        print(f"Error adding book: {e}")
        
    conn.close()

def get_user_library(username, status_filter=None):
    """Gets all books for a specific user"""
    conn = sqlite3.connect('booktok.db')
    c = conn.cursor()
    
    if status_filter:
        c.execute('SELECT * FROM library WHERE username = ? AND status = ?', (username, status_filter))
    else:
        c.execute('SELECT * FROM library WHERE username = ?', (username,))
        
    data = c.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    library_books = []
    for row in data:
        library_books.append({
            'book_id': row[1],
            'title': row[2],
            'author': row[3],
            'image_url': row[4],
            'status': row[5]
        })
        
    return library_books