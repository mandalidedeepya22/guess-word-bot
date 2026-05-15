# Guess The Word

AI-hosted word guessing game with dynamic hints powered by Google Gemini.

## Features

- Random secret word from 42 categories
- Up to 5 progressive AI-generated hints
- CLI (`main.py`) and web UI (`app.py` via Streamlit)
- Anti-cheat: blocks early answer requests

## Setup (local)

1. Clone the repo and open the project folder.

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your Gemini API key:

   ```env
   GEMINI_API_KEY=your-gemini-api-key-here
   GEMINI_MODEL=gemini-flash-latest
   ```

   Get a key at [Google AI Studio](https://aistudio.google.com/apikey).

## Run locally

**Terminal:**

```bash
python main.py
```

**Web (Streamlit):**

```bash
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app.
3. Set **Main file path** to `app.py`.
4. Add **Secrets** (Settings → Secrets):

   ```toml
   GEMINI_API_KEY = "your-gemini-api-key-here"
   GEMINI_MODEL = "gemini-flash-latest"
   ```

5. Deploy.

## Project structure

| File | Description |
|------|-------------|
| `app.py` | Streamlit web app |
| `main.py` | CLI entry point |
| `game_engine.py` | Game logic and state |
| `hint_generator.py` | Gemini hint generation |
| `word_bank.py` | Words and categories |

## License

MIT (or your choice)
