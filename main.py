import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- CONFIGURATION ---
BOOKS_FILE = 'books_data/books.csv'
RATINGS_FILE = 'books_data/ratings.csv'

# --- PART 1: LOAD AND MERGE DATA ---
print("\n" + "="*50)
print(" SYSTEM STARTUP: LOADING DATABASES")
print("="*50)

# 1. Load Books
print("1. Loading Books... (Please wait)")
books_df = pd.read_csv(BOOKS_FILE, sep=';', encoding='latin-1', on_bad_lines='skip', dtype={'Year-Of-Publication': str})

# Rename columns
books_df = books_df.rename(columns={
    'Book-Title': 'title', 
    'Book-Author': 'author', 
    'Publisher': 'publisher',
    'Year-Of-Publication': 'year'
})

# 2. Load Ratings
print("2. Loading Ratings... (This handles millions of votes)")
ratings_df = pd.read_csv(RATINGS_FILE, sep=';', encoding='latin-1', on_bad_lines='skip')

# 3. Calculate Average Rating and Count per Book
# Group by ISBN (unique book ID) and do math
print("3. Calculating Average Ratings...")
rating_stats = ratings_df.groupby('ISBN')['Book-Rating'].agg(['mean', 'count']).reset_index()
rating_stats.columns = ['ISBN', 'average_rating', 'rating_count']

# 4. Merge Data (Combine Books + Ratings)
print("4. Merging Tables...")
df = pd.merge(books_df, rating_stats, on='ISBN', how='left')

# Fill books with no ratings with 0
df['average_rating'] = df['average_rating'].fillna(0)
df['rating_count'] = df['rating_count'].fillna(0)

# Round the rating to 1 decimal place (e.g., 4.2333 -> 4.2)
df['average_rating'] = df['average_rating'].round(1)

print(f"--> Database Ready! Loaded {len(df)} books.")

# --- PART 2: CREATE SEARCH ENGINE ---
print("5. Building Search Index...")

# Create Soup (Author + Publisher)
def create_soup(x):
    return str(x['author']) + ' ' + str(x['publisher'])

df['soup'] = df.apply(create_soup, axis=1)

# Vectorize (Turn text to numbers)
# We limit max_features to 5000 unique words to keep it fast
count = CountVectorizer(stop_words='english', max_features=5000) 
count_matrix = count.fit_transform(df['soup'])

# --- PART 3: FUNCTIONS ---

def search_books(query):
    """
    Search by Title OR Author
    """
    # Convert query to lowercase
    query = query.lower()
    
    # Check if query is in Title OR Author
    mask = (df['title'].str.lower().str.contains(query, na=False)) | \
           (df['author'].str.lower().str.contains(query, na=False))
           
    return df[mask]

def get_recommendations(idx):
    """
    Get similar books based on Author and Publisher
    """
    # Get vector for selected book
    selected_vector = count_matrix[idx]
    
    # Calculate similarity
    sim_scores = cosine_similarity(selected_vector, count_matrix)
    
    # Get top 6 matches
    sim_scores = sim_scores[0]
    top_indices = sim_scores.argsort()[-7:][::-1]
    
    # Remove the book itself
    top_indices = [i for i in top_indices if i != idx]
    
    return df.iloc[top_indices]

# --- PART 4: THE INTERFACE ---
while True:
    print("\n" + "="*60)
    print(" TYPE A BOOK TITLE OR AUTHOR NAME (or 'exit'):")
    user_query = input(" > ")
    
    if user_query.lower() == 'exit':
        break
    
    # 1. SEARCH
    results = search_books(user_query)
    
    if len(results) == 0:
        print("No results found.")
        continue
    
    # 2. SHOW LIST
    # Sort by number of ratings so popular books show up first
    results = results.sort_values('rating_count', ascending=False).head(10)
    results = results.reset_index() # Reset so we can select by 0, 1, 2...
    
    print(f"\nFound {len(results)} matches. Which one did you mean?")
    print("-" * 60)
    print(f"{'No.':<5} {'Title':<40} {'Author':<20} {'Ratings'}")
    print("-" * 60)
    
    for i, row in results.iterrows():
        # Truncate long titles so they fit on screen
        short_title = (row['title'][:35] + '..') if len(row['title']) > 35 else row['title']
        print(f"{i:<5} {short_title:<40} {row['author']:<20} {row['average_rating']}/10 ({int(row['rating_count'])})")

    # 3. USER SELECTION
    try:
        selection = int(input("\nEnter the 'No.' of your book: "))
        if selection < 0 or selection >= len(results):
            print("Invalid number.")
            continue
            
        # Get the actual row from the main dataframe
        selected_row = results.iloc[selection]
        original_idx = selected_row['index'] # The index in the main 'df'
        
    except ValueError:
        print("Please type a number.")
        continue

    # 4. DISPLAY DETAILS
    print("\n" + "#"*60)
    print(f" SELECTED BOOK: {selected_row['title']}")
    print("#"*60)
    print(f"Author:    {selected_row['author']}")
    print(f"Year:      {selected_row['year']}")
    print(f"Publisher: {selected_row['publisher']}")
    print(f"Rating:    {selected_row['average_rating']} / 10  (based on {int(selected_row['rating_count'])} votes)")
    print("#"*60)
    
    # 5. DISPLAY RECOMMENDATIONS
    print("\n--> Generating Recommendations based on Author & Publisher...")
    recs = get_recommendations(original_idx)
    
    print("\nYOU MIGHT ALSO LIKE:")
    print("-" * 60)
    for i, row in recs.iterrows():
        print(f"* {row['title']} (by {row['author']}) - Rating: {row['average_rating']}")
    print("-" * 60)

