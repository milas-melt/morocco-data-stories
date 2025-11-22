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
Write a narration script of about 160 to 220 words in {lang_desc}.

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
            return generate_script_stub(persona, summary)
        return text
    except Exception as e:
        print("OpenAI error, using stub script:", repr(e))
        return generate_script_stub(persona, summary)


def generate_video_story(
    persona: str = "Citizen",
    topic: str = "Education Access 2023",
    language: str = "en",
):
    """
    Orchestration function.

    For now:
    - Generate narration script with OpenAI
    - Generate MP3 narration with ElevenLabs
    - Return (audio_path, script, video_path=None)
    """
    df = load_education_data()
    summary = summarise_for_llm(df)
    script = generate_script_llm(persona=persona, summary=summary, language=language)

    audio_path = text_to_speech_file(script)
    video_path = None  # placeholder for VEED / fal integration later

    return audio_path, script, video_path


def text_to_speech_file(text: str, voice: str = "Rachel") -> str | None:
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
                "voice": voice,  # defaults to "Rachel" if omitted
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
    Upload local audio file to fal storage and return a URL fal/VEED can see.
    """
    if fal_client is None:
        print("WARNING: FAL_KEY not set, skipping video generation.")
        return None

    if not os.path.exists(audio_path):
        print(f"Audio file not found, cannot upload: {audio_path}")
        return None

    try:
        with open(audio_path, "rb") as f:
            uploaded = fal_client.storage.upload_file(
                f, filename=os.path.basename(audio_path)
            )
        # uploaded.url should be an HTTPS URL accessible to VEED within fal
        return uploaded.url
    except Exception as e:
        print("Error uploading audio to fal:", repr(e))
        return None


if __name__ == "__main__":
    audio_path, script, vid = generate_video_story(
        "Citizen", "Education Access 2023", language="en"
    )
    print("Audio path:", audio_path)
    print("Video path (placeholder):", vid)
    print("\n=== Generated Script ===\n")
    print(script)
