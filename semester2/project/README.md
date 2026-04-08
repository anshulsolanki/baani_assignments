# Identity-Verified Multiplayer Arena

This project is a full-stack, real-time multiplayer web application with biometric authentication, polyglot persistence, and an Elo rating system.

## Project Structure

- `scraper.py`: Autonomous data harvesting script.
- `main.py`: FastAPI backend serving API and WebSockets.
- `facial_recognition_module.py`: Mocked module for facial recognition.
- `batch_data.csv`: Mocked input data for players.
- `static/`: Frontend assets (HTML, CSS, JS).

## Assumptions

1. **Missing Files**: `batch_data.csv` and `facial_recognition_module.py` were not found in the workspace and have been mocked for development purposes.
2. **Package Manager**: `uv` was recommended but not found on the system. Standard `pip` and `requirements.txt` are used instead.

## Database Schemas

### MySQL (Relational Metadata)

```sql
CREATE TABLE users (
    uid VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    elo_rating INT DEFAULT 1200,
    is_online BOOLEAN DEFAULT FALSE
);
```

### MongoDB (Unstructured Asset Storage)

- Collection: `profile_images`
- Document structure:
  ```json
  {
      "uid": "string",
      "image_data": "base64_string_or_binary"
  }
  ```

## Instructions

### Installation

1. (Optional) Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Database Initialization

1. Ensure MySQL and MongoDB are running.
2. Run the setup script to create databases and tables:
   ```bash
   python db_setup.py
   ```

### Running the Scraper

To populate the database with mock player data and images:
```bash
python scraper.py
```

### Running the Application

To start the FastAPI server and WebSocket services:
```bash
uvicorn main:app --reload
```
The application will be available at `http://localhost:8000`.
