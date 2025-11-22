import os
import pandas as pd

DATA_PATH = "data/education_access_2023.csv"


def load_education_data() -> pd.DataFrame:
    """Load the aggregated education access data."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Expected aggregated data at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    # Basic sanity checks
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
    """
    Build a compact textual summary of the dataset
    that we'll later feed to the LLM (for now we just print it).
    """
    year = int(df["year"].iloc[0]) if "year" in df.columns else 2023

    total_schools = int(df["total_schools"].sum())
    total_public = int(df["public_schools"].sum())
    total_private = int(df["private_schools"].sum())

    n_regions = df["region"].nunique()

    # Top / bottom regions by total schools
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


def generate_script_stub(persona: str = "Citizen") -> str:
    """
    For now, generate a simple narration script WITHOUT calling OpenAI.
    We'll plug OpenAI in later using this as a fallback / template.
    """
    df = load_education_data()
    summary = summarise_for_llm(df)

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


def generate_video_story(
    persona: str = "Citizen", topic: str = "Education Access 2023"
):
    """
    Orchestration function.

    For now:
    - Ignores topic (we only have one)
    - Returns (video_path=None, script=text)

    Later:
    - Will call OpenAI for a richer script
    - Will call ElevenLabs for TTS
    - Will build an MP4 with moviepy or VEED
    """
    script = generate_script_stub(persona=persona)
    video_path = None  # placeholder for later
    return video_path, script


if __name__ == "__main__":
    # Quick manual test
    vid, script = generate_video_story("Citizen", "Education Access 2023")
    print("Video path (placeholder):", vid)
    print("\n=== Generated Script ===\n")
    print(script)
