import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from elevenlabs.client import ElevenLabs
import uuid
import requests

import fal_client


load_dotenv()

DATA_PATH = "data/education_access_2023.csv"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None

FAL_KEY = os.getenv("FAL_KEY")


def load_education_data() -> pd.DataFrame:
    """Load the aggregated education access data."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Expected aggregated data at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    expected_cols = {
        "region",
        "year",
        "total_schools",
        "public_schools",
        "private_schools",
    }
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {DATA_PATH}: {missing}")
    return df


def summarise_for_llm(df: pd.DataFrame) -> str:
    """Build a compact textual summary of the dataset for the LLM."""
    year = int(df["year"].iloc[0]) if "year" in df.columns else 2023

    total_schools = int(df["total_schools"].sum())
    total_public = int(df["public_schools"].sum())
    total_private = int(df["private_schools"].sum())

    n_regions = df["region"].nunique()

    df_sorted = df.sort_values("total_schools", ascending=False)
    top_regions = df_sorted.head(3)[["region", "total_schools"]].values.tolist()
    bottom_regions = df_sorted.tail(3)[["region", "total_schools"]].values.tolist()

    lines = []
    lines.append(f"Education access in Morocco in {year}.")
    lines.append(f"There are {total_schools} schools across {n_regions} regions.")
    lines.append(
        f"Of these, {total_public} are public and {total_private} are private (in this dataset)."
    )

    if top_regions:
        top_str = "; ".join([f"{r} ({int(n)} schools)" for r, n in top_regions])
        lines.append(f"Regions with the highest number of schools: {top_str}.")

    if bottom_regions:
        bottom_str = "; ".join([f"{r} ({int(n)} schools)" for r, n in bottom_regions])
        lines.append(f"Regions with the fewest schools: {bottom_str}.")

    lines.append(
        "This data highlights regional inequalities in access to education infrastructure across Morocco."
    )

    return " ".join(lines)


def generate_script_stub(persona: str, summary: str) -> str:
    """Simple fallback script if OpenAI is not available."""
    if persona.lower() == "investor":
        persona_intro = "This story is tailored for investors interested in regional opportunities in Morocco. "
    else:
        persona_intro = "This story is tailored for citizens and students who want to understand education access in Morocco. "

    script = (
        f"{persona_intro}"
        f"Based on official school data, here is a simple overview: "
        f"{summary} "
        "In the full version of this system, this narration would be turned into audio and a short explainer video."
    )

    return script


def generate_script_llm(persona: str, summary: str, language: str = "en") -> str:
    """
    Use OpenAI Chat Completions to turn the summary into a narration script.
    """
    if client is None:
        print("WARNING: OPENAI_API_KEY not set, using stub script.")
        return generate_script_stub(persona, summary)

    persona_desc = (
        "a Moroccan citizen with limited technical background"
        if persona.lower() == "citizen"
        else "a foreign investor interested in regional opportunities in Morocco"
    )

    lang_desc = {
        "en": "English",
        "fr": "French",
        "ar": "Arabic",
    }.get(language, "English")

    system_prompt = (
        "You are an expert policy communicator. "
        "You write short, clear narration scripts based on structured data summaries. "
        "Avoid jargon, keep it accessible, and speak in a warm, natural tone. "
        "The script will be voiced over in a short explainer video about Morocco."
    )

    user_prompt = f"""
Write a narration script of about 70 to 100 words in {lang_desc}.
Absolutely do not exceed 100 words.

Audience: {persona_desc}.

Topic: Education access across Moroccan regions.

Data summary (you must base your story on this, but you may reorder and rephrase):

\"\"\"{summary}\"\"\".

Requirements:
- Start with 1–2 sentences setting the context (Morocco, education, regions).
- Explain what the total number of schools and regions means in simple terms.
- Highlight the regions with the most and fewest schools and what that implies.
- For citizens: focus on fairness, access, and development.
- For investors: also hint at where infrastructure or human capital may be under-served.
- End with a forward-looking, hopeful sentence about using data to improve education.
- No bullet points, just continuous spoken text.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        text = response.choices[0].message.content.strip()
        if not text:
            print("Empty LLM response, using stub script.")
            return clamp_script_length(
                generate_script_stub(persona, summary),
                max_words=100,
            )
        return clamp_script_length(text, max_words=100)
    except Exception as e:
        print("OpenAI error, using stub script:", repr(e))
        return clamp_script_length(
            generate_script_stub(persona, summary),
            max_words=100,
        )


def generate_video_story(
    persona: str = "Citizen",
    topic: str = "Education Access 2023",
    language: str = "en",
):
    """
    Orchestration function.

    - Generate narration script with OpenAI
    - Generate MP3 narration with ElevenLabs (via fal)
    - Generate talking video with VEED Fabric 1.0 Fast (via fal), if an image is available
    """
    df = load_education_data()
    summary = summarise_for_llm(df)
    script = generate_script_llm(persona=persona, summary=summary, language=language)

    audio_path = text_to_speech_file(script)

    # Make sure this file actually exists
    image_path = "assets/morocco_education.png"

    video_path = generate_video_with_veed_fal(script, audio_path, image_path)

    return audio_path, script, video_path


def text_to_speech_file(text: str, voice: str = "Brian") -> str | None:
    """
    Generate MP3 narration using ElevenLabs Turbo v2.5 via fal.
    Returns local file path to the MP3, or None on failure.
    """
    if not FAL_KEY:
        print("WARNING: FAL_KEY not set, skipping audio generation.")
        return None

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", f"tts_{uuid.uuid4().hex[:8]}.mp3")

    try:
        result = fal_client.subscribe(
            "fal-ai/elevenlabs/tts/turbo-v2.5",
            arguments={
                "text": text,
                # Optional tunables – safe defaults:
                "voice": voice,
                "stability": 0.5,
                "similarity_boost": 0.75,
                "speed": 1.0,
            },
            with_logs=False,
        )

        # According to docs: { "audio": { "url": "https://..." } }
        audio = result.get("audio")
        if not audio or "url" not in audio:
            print("fal TTS result missing audio.url:", result)
            return None

        audio_url = audio["url"]

        resp = requests.get(audio_url, stream=True)
        resp.raise_for_status()

        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return out_path

    except Exception as e:
        print("Error generating audio via fal ElevenLabs:", repr(e))
        return None


def upload_audio_to_fal(audio_path: str) -> str | None:
    """
    Upload local MP3 file to fal storage so VEED (or any fal model) can access it.
    Returns a public HTTPS URL.
    """
    if not FAL_KEY:
        print("WARNING: FAL_KEY not set, skipping upload.")
        return None

    if not os.path.exists(audio_path):
        print("Audio file does not exist:", audio_path)
        return None

    try:
        uploaded = fal_client.upload_file(audio_path)

        # Handle several possible return formats

        # 1) Already a string URL
        if isinstance(uploaded, str):
            return uploaded

        # 2) Dict-like: {"url": "..."}
        if isinstance(uploaded, dict):
            url = uploaded.get("url")
            if url:
                return url

        # 3) Object with .url attribute
        if hasattr(uploaded, "url"):
            return uploaded.url

        print("Unexpected response from fal_client.upload_file:", repr(uploaded))
        return None

    except Exception as e:
        print("Error uploading audio to fal storage:", repr(e))
        return None


def upload_file_to_fal(path: str) -> str | None:
    """
    Upload a local file (audio/image/etc.) to fal storage and return a public HTTPS URL.
    """
    if not FAL_KEY:
        print("WARNING: FAL_KEY not set, skipping upload.")
        return None

    if not os.path.exists(path):
        print("File does not exist:", path)
        return None

    try:
        uploaded = fal_client.upload_file(path)

        # 1) String URL
        if isinstance(uploaded, str):
            return uploaded

        # 2) Dict with "url"
        if isinstance(uploaded, dict):
            url = uploaded.get("url")
            if url:
                return url

        # 3) Object with .url attribute
        if hasattr(uploaded, "url"):
            return uploaded.url

        print("Unexpected response from fal_client.upload_file:", repr(uploaded))
        return None

    except Exception as e:
        print("Error uploading file to fal storage:", repr(e))
        return None


def generate_video_with_veed_fal(
    script: str,
    audio_path: str | None,
    image_path: str | None,
) -> str | None:
    """
    Use VEED Fabric 1.0 Fast via fal to generate a simple explainer MP4.
    Requires:
      - audio_path: local MP3 from TTS
      - image_path: local PNG/JPG to animate
    Returns local path to the MP4 or None.
    """
    if not FAL_KEY:
        print("WARNING: FAL_KEY not set, skipping VEED video generation.")
        return None

    if not audio_path:
        print("No audio available for video.")
        return None

    if not image_path:
        print("No image provided for Fabric 1.0 video.")
        return None

    # Upload audio and image to fal storage
    audio_url = upload_file_to_fal(audio_path)
    if not audio_url:
        print("Could not upload audio to fal. No audio URL:", audio_url)
        return None

    image_url = upload_file_to_fal(image_path)
    if not image_url:
        print("Could not upload image to fal. No image URL:", image_url)
        return None

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", f"video_{uuid.uuid4().hex[:8]}.mp4")

    try:
        # Fabric 1.0 Fast endpoint
        result = fal_client.subscribe(
            "veed/fabric-1.0",
            arguments={
                "image_url": image_url,
                "audio_url": audio_url,
                "resolution": "720p",
            },
            with_logs=False,
        )

        # Expected: { "video": { "content_type": "video/mp4", "url": "https://..." } }
        video_info = None
        if isinstance(result, dict):
            video_info = result.get("video") or result.get("output") or result

        if not video_info or "url" not in video_info:
            print("Could not find video URL in fal response:", result)
            return None

        video_url = video_info["url"]

        resp = requests.get(video_url, stream=True)
        resp.raise_for_status()

        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return out_path

    except Exception as e:
        print("Error generating VEED Fabric video via fal:", repr(e))
        return None


def clamp_script_length(text: str, max_words: int = 150) -> str:
    """
    Ensure the script is no longer than `max_words` words.
    We keep whole words and just truncate, which is fine for narration.
    """
    if not text:
        return text

    words = text.split()
    if len(words) <= max_words:
        return text

    # Cut to max_words and make sure it ends with a period.
    trimmed = " ".join(words[:max_words])
    trimmed = trimmed.rstrip()

    if not trimmed.endswith((".", "!", "?")):
        trimmed += "."

    return trimmed


if __name__ == "__main__":
    audio_path, script, video_path = generate_video_story(
        "Citizen", "Education Access 2023", language="en"
    )
    print("Audio:", audio_path)
    print("Video:", video_path)
    print("\n=== Script ===\n")
    print(script)
