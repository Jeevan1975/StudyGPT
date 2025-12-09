# 📚 StudyGPT – RAG-Based Book Question Answering

An AI-powered learning platform where users upload books (PDFs), and the system uses Retrieval-Augmented Generation (RAG) to answer questions based solely on the uploaded book. Users can chat with the book, ask questions, and receive real-time streaming responses.


## ✨ Features

### 🔐 User Authentication (Supabase Auth)
- Signup & Login via Supabase email/password auth
- Token-based authentication (`Bearer <token>`)
- Secured endpoints using `get_current_user` dependency

### 📕 User Book Management
- Upload PDF books
- Store books securely in Supabase Storage
- Track ingestion status (`uploaded` | `ingesting` | `ready`)
- List all books per user (`GET /books`)
- Get a single book (`GET /books/{book_id}`)
- Delete a book + vectorstore + database entry

### 🔍 RAG Pipeline (Retrieval-Augmented Generation)
Each book has its own vectorstore at: `vectorstores/<user_id>/<book_id>/`

The system performs:
- Chunking the PDF
- Embedding using Google Gemini embeddings
- Storing chunks in Chroma
- Real-time retrieval at query time

### 💬 Book Chat System
- `/chat/stream` → ChatGPT-style streaming responses
- Every question is answered using only the content of the uploaded book


## ⚙️ Environment Variables

Create `.env` outside `backend/`:

```env
GOOGLE_API_KEY=your-google-api
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=your-database-url
```

## 🚀 Installation

### 1. Clone the repo
```bash
git clone https://github.com/Jeevan1975/StudyGPT.git
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

### 3. Install requirements
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
For SQLAlchemy, use Alembic or create tables manually:

```python
from models.db_models import Base
from core.database import engine
Base.metadata.create_all(bind=engine)
```

### 5. Start FastAPI
```bash
uvicorn app:app --reload
```

## 🔐 Authentication Endpoints

### Signup
```http
POST /auth/signup
Content-Type: application/json

{
  "email": "user@email.com",
  "password": "Password123"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@email.com",
  "password": "Password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "...",
  "refresh_token": "...",
  "user": {...}
}
```

**Use token in headers:**
```
Authorization: Bearer <access_token>
```

## 📚 Book Endpoints

### Upload Book
```http
POST /books/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

file=<PDF file>
```

### List Books
```http
GET /books
Authorization: Bearer <token>
```

### Get Single Book
```http
GET /books/{book_id}
Authorization: Bearer <token>
```

### Delete Book
```http
DELETE /books/{book_id}
Authorization: Bearer <token>
```

## 🤖 Chat Endpoint
```

### Streaming (ChatGPT-like)
```http
POST /chat/stream
Content-Type: application/json
Authorization: Bearer <token>

{
  "question": "What is the main idea in chapter 2?",
  "book_id": "uuid"
}
```

Returns incremental text chunks (`text/plain`).

## 🧩 How Ingestion Works

1. User uploads PDF → stored in Supabase Storage
2. DB row created in `books` table
3. Background task downloads PDF → saves temporarily
4. LangChain:
   - Loads PDF via `PyPDFLoader`
   - Splits content into chunks
   - Generates embeddings
   - Stores in Chroma vectorstore
5. Book status updated to `ready`
6. User can now chat with that book

## 🧠 Core Tech Stack

| Component | Technology |
|-----------|-----------|
| **LLM** | Google Gemini |
| **Embeddings** | Gemini embedding |
| **Vector DB** | ChromaDB |
| **Auth** | Supabase Auth |
| **Storage** | Supabase Storage |
| **Framework** | FastAPI |
| **Database** | PostgreSQL + SQLAlchemy |
| **Streaming** | FastAPI StreamingResponse |
| **Background Tasks** | FastAPI BackgroundTasks |

## 🛡️ Security Notes

- All book operations are authenticated
- Only the owner can access or delete their books
- Supabase Storage is private (no public access)
- Tokens validated using Supabase Admin API
- Vectorstores isolated per user & per book
