"""Streamlit web UI for Guess The Word."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _apply_streamlit_secrets() -> None:
  try:
    secrets = st.secrets
    if "GEMINI_API_KEY" in secrets:
      os.environ["GEMINI_API_KEY"] = secrets["GEMINI_API_KEY"]
    if "GEMINI_MODEL" in secrets:
      os.environ["GEMINI_MODEL"] = secrets["GEMINI_MODEL"]
  except (FileNotFoundError, AttributeError):
    pass


_apply_streamlit_secrets()

from game_engine import GameEngine, Phase  # noqa: E402
from hint_generator import MAX_HINTS, _client  # noqa: E402

_client.cache_clear()


def _init_session() -> None:
  if "engine" not in st.session_state:
    st.session_state.engine = GameEngine()
  if "messages" not in st.session_state:
    st.session_state.messages = []
  if "round_active" not in st.session_state:
    st.session_state.round_active = False


def _append(role: str, content: str) -> None:
  st.session_state.messages.append({"role": role, "content": content})


def _bot_reply(text: str) -> None:
  _append("assistant", text)


def _start_round() -> None:
  engine: GameEngine = st.session_state.engine
  with st.spinner("Host is thinking up a hint..."):
    reply = engine.new_game()
  st.session_state.round_active = engine.phase is Phase.PLAYING
  _bot_reply(reply)


def _handle_guess(guess: str) -> None:
  _append("user", guess)
  engine: GameEngine = st.session_state.engine
  with st.spinner("Checking your guess..."):
    reply = engine.process_input(guess)
  st.session_state.round_active = engine.phase is Phase.PLAYING
  _bot_reply(reply)


def _handle_give_up() -> None:
  engine: GameEngine = st.session_state.engine
  reply = engine.give_up()
  st.session_state.round_active = False
  _bot_reply(reply)


def main() -> None:
  st.set_page_config(
    page_title="Guess The Word",
    page_icon="🎯",
    layout="centered",
  )

  _init_session()
  engine: GameEngine = st.session_state.engine

  st.title("🎯 Guess The Word")
  st.caption("AI-hosted · dynamic Gemini hints · max 5 per round")

  if not os.getenv("GEMINI_API_KEY", "").strip():
    st.error(
      "Missing **GEMINI_API_KEY**. "
      "Add it to `.env` locally, or to Streamlit **Secrets** when deploying."
    )
    st.code(
      "GEMINI_API_KEY = \"your-key\"\nGEMINI_MODEL = \"gemini-flash-latest\"",
      language="toml",
    )
    st.stop()

  with st.sidebar:
    st.header("Game")
    if st.button("🆕 New game", use_container_width=True):
      st.session_state.messages = []
      _start_round()
      st.rerun()

    if st.button("🏳️ Give up", use_container_width=True, disabled=not st.session_state.round_active):
      _handle_give_up()
      st.rerun()

    st.divider()
    st.metric("Hints used", f"{len(engine.hints_used)} / {MAX_HINTS}")
    st.metric("Guesses", len(engine.guesses))

    if engine.hints_used:
      st.subheader("Clues so far")
      for i, hint in enumerate(engine.hints_used, start=1):
        st.markdown(f"**{i}.** {hint}")

    st.divider()
    st.markdown(
      "**Deploy:** push to GitHub, then [share.streamlit.io](https://share.streamlit.io) "
      "→ New app → set **Main file** to `app.py` and add secrets."
    )

  for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
      st.markdown(msg["content"])

  if not st.session_state.messages:
    st.info("Press **New game** in the sidebar to start!")
  elif st.session_state.round_active:
    guess = st.chat_input("Your guess...")
    if guess:
      _handle_guess(guess)
      st.rerun()


if __name__ == "__main__":
  main()
