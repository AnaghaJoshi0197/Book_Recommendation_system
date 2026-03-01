# 📖 Book Recommendation System

A full-stack Python application that provides book recommendations using **Content-Based Filtering** (Cosine Similarity). It features a modern web interface built with **Streamlit** and a **SQLite** backend for data management.

## 🚀 Features
- **Smart Recommendations:** Uses `CountVectorizer` and `Cosine Similarity` to find related books.
- **Web Interface:** Interactive UI built with Streamlit (`app.py`).
- **Data Persistence:** Uses SQLite (`booktok`) for storing book information and user data.
- **API Integration:** Fetches additional book data via Google Books API (`backend.py`).

## 🛠️ Installation & Setup
1. **Clone the project:**
   git clone [https://github.com/YOUR_USERNAME/your-repo-name.git]
   cd "Book Recommendation System"

2. **Setup Environment:**
   python -m venv venv
   venv\Scripts\activate

3. **Install Dependencies:**
   pip install -r requirements.txt

4. **Run the App:**
   streamlit run app.py
