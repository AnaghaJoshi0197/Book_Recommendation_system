import backend

# 1. Initialize Database
print("--- 1. Setting up Database ---")
backend.init_db()
print("Database 'booktok.db' created successfully.")

# 2. Test Google API
print("\n--- 2. Testing Google API ---")
query = "Harry Potter"
print(f"Searching for '{query}'...")
results = backend.search_google_books(query)

if len(results) > 0:
    first_book = results[0]
    print(f"Success! Found: {first_book['title']} by {first_book['authors']}")
    print(f"Description snippet: {first_book['description'][:100]}...")
else:
    print("API Search failed.")

# 3. Test User Creation
print("\n--- 3. Testing User Accounts ---")
user = "testuser"
pw = "password123"

# Try to create user
if backend.create_user(user, pw):
    print(f"User '{user}' created.")
else:
    print(f"User '{user}' already exists (that's okay).")

# Try to login
if backend.check_login(user, pw):
    print("Login Successful!")
else:
    print("Login Failed.")

# 4. Test Adding to Library
print("\n--- 4. Testing Personal Library ---")
if len(results) > 0:
    # Add the first book we found to 'To Be Read'
    backend.add_book_to_library(user, results[0], 'tbr')
    
    # Retrieve library
    my_books = backend.get_user_library(user, 'tbr')
    print(f"My TBR List has {len(my_books)} book(s).")
    print(f"First book in list: {my_books[0]['title']}")