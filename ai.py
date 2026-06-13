import json
import os

import PIL.Image
from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    return _client


def summarize_text(text: str) -> str:
    response = _get_client().models.generate_content(
        model=MODEL,
        contents=(
            "Summarize the following news article as 3-5 concise bullet points. "
            "Focus on key facts, trends, and important information.\n\n"
            f"{text[:8000]}"
        ),
    )
    return response.text


def summarize_image(image_path: str) -> str:
    img = PIL.Image.open(image_path)
    response = _get_client().models.generate_content(
        model=MODEL,
        contents=[
            "This is an Instagram screenshot or news image. "
            "Describe the content, extract any visible text, captions, hashtags, "
            "and key trends or topics. Summarize as 3-5 bullet points.",
            img,
        ],
    )
    return response.text


def generate_presentation_structure(summaries: list) -> list:
    items_text = "\n\n".join(
        f"Item {i + 1} (source: {s.get('source', 'unknown')}):\n{s['summary']}"
        for i, s in enumerate(summaries)
    )
    prompt = (
        "You are preparing a news overview presentation. "
        "Based on the following news summaries, group them into logical slides. "
        "Include a trends/conclusions slide at the end.\n\n"
        f"{items_text}\n\n"
        "Return ONLY a JSON array (no markdown, no explanation) with this structure:\n"
        '[{"title": "Slide Title", "bullets": ["bullet 1", "bullet 2", ...]}, ...]'
    )
    response = _get_client().models.generate_content(model=MODEL, contents=prompt)
    raw = response.text.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())
