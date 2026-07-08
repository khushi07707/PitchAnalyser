# AI Augmented Pitch Analyser - Backend

This is the production-grade Python FastAPI backend for the **AI Augmented Pitch Analyser** college project. It manages user authentication, file uploads, audio extraction, DSP audio processing, Speech-to-Text, NLP analytics, and VC feedback generation.

## Technical Architecture

The backend follows Clean Architecture principles:
- **API Routes (`app/api/`)**: Handlers validating schemas and mapping REST routes.
- **Pydantic Schemas (`app/schemas/`)**: Strict input/output payload shapes.
- **SQLAlchemy Models (`app/models/`)**: Relational mappings representing user files, transcripts, metrics, feedback, and reports.
- **Core Configurations (`app/core/`, `app/config/`)**: Environment settings, exception mappings, and security tokens.
- **Services (`app/services/`)**: Encapulated reusable business calculations (audio processing, sentiment scoring, report compilers).

---

## Prerequisite Setup

Ensure the following tools are installed:
1. **Python 3.10+** (Developed and tested on Python 3.13)
2. **PostgreSQL Server** (Running locally or accessible remotely)
3. **ffmpeg** (Highly recommended for extracting audio from video uploads)

---

## Quick Start Installation

### 1. Clone & Set Up Virtual Environment
Open a terminal in the `backend/` folder:
```bash
# Create python virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Activate on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Create the Database
In PostgreSQL, create a database named `pitch_analyser`:
```sql
CREATE DATABASE pitch_analyser;
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in credentials:
```bash
cp .env.example .env
```
Ensure your `DATABASE_URL` is set:
```ini
DATABASE_URL="postgresql://postgres:password@localhost:5432/pitch_analyser"
```

### 5. Start the Server
Run the FastAPI development server:
```bash
uvicorn app.main:app --reload
```
The server will boot and automatically initialize the database schema tables. It listens on `http://127.0.0.1:8000`.

---

## API Documentation & Testing

Once running, navigate to:
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Schema View**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Core Features & AI Fallbacks

- **Dual-Mode AI Engine**:
  - If a valid `OPENAI_API_KEY` is provided in `.env`, the pipeline transcribes files using **OpenAI Whisper** and generates evaluations via **GPT-4o**.
  - If no key is set, the system falls back to a **local mock engine**: it uses heuristic word-timestamp structures for the transcription page and rules-based logic to evaluate pitch and speaking rate scores.
- **DSP librosa Analytics**:
  - Calculates speaking speed (WPM).
  - Tracks Fundamental Frequency (F0 / Pitch in Hz) and pitch stability.
  - Determines pauses count and silent gaps using decibel checks.
  - Measures voice modulation variance to classify delivery style.
- **NLP Text Analyzer**:
  - Counts filler phrases (um, uh, like, you know, etc.).
  - Tracks repetitive sequence markers.
  - Calculates sentiment polarity and subjectivity using TextBlob.
  - Generates top keyword lists and checks readability constraints.
