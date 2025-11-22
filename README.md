# 🇲🇦 Morocco Data Stories

Moroccan public data is fragmented and hard to use. It lives in PDFs, Excel files, scattered portals like data.gov.ma, and ministry websites that most citizens and investors never touch. With a large low-literacy population, even “open data” is rarely truly understandable.

**Morocco Data Stories** turns this chaos into **short, simple, multilingual explainer videos** generated fully by AI — built on top of a unified API of Moroccan public data.

> Morocco has the data — we make it understandable.

---

## 🚀 What the MVP Does

1. **Scrape & unify Moroccan public data**
   A scraping layer pulls datasets from segregated online sources (open data portals, CSV/XLS files, etc.), cleans them, and loads them into a single, queryable store.

2. **Expose a public Data API**
   On top of this store, we expose an HTTP API for Moroccan statistics (starting with education). The goal is to become the **largest public data API in Morocco** by coverage and usability.

3. **Summarise data with OpenAI**
   For a given topic (e.g. education access 2023), the system aggregates the relevant data and asks an OpenAI model to generate a clear, persona-aware narrative.

4. **Generate narration with ElevenLabs (via fal)**
   The script is turned into natural-sounding MP3 narration using ElevenLabs Turbo v2.5, orchestrated through fal.

5. **Create a video with VEED (via fal)**
   Using VEED Fabric 1.0 on fal, the system combines the narration and a visual (e.g. education map/thumbnail) into a short explainer MP4 — always producing a **final video**, not just audio.

---

## 🧩 Architecture Overview

### 1. Scraper Layer

-   Scrapes Moroccan public datasets from multiple official sources (portals, CSV/XLS, etc.).
-   Normalises formats and merges them into a consistent schema.
-   Feeds into the internal data store.

### 2. Data & API Layer

-   Stores cleaned, structured Moroccan indicators (starting with school infrastructure by region).
-   Exposes a REST API so other apps can query Moroccan stats programmatically.
-   Designed to grow into the **largest public Moroccan data API** by number of themes and datasets.

### 3. AI Storytelling Pipeline

-   `prepare_data.py`
    Aggregates and prepares topic-specific datasets (e.g. education access 2023).
-   `pipeline.py`
    Orchestrates the full flow:

    1. Load + aggregate data
    2. Build a compact summary for the LLM
    3. Generate a persona-specific script with OpenAI
    4. Generate narration with ElevenLabs (via fal)
    5. Generate the final video with VEED Fabric (via fal)

### 4. Outputs

-   `outputs/tts_*.mp3` — narration audio files
-   `outputs/video_*.mp4` — final explainer videos
-   Script printed to stdout for transparency / localisation / editing

---

## 🛠️ Hackathon Technologies

This project uses **at least three** partner technologies:

-   **OpenAI** — data understanding & narrative script generation
-   **fal** — orchestration layer and model hosting (ElevenLabs + VEED)
-   **ElevenLabs (via fal)** — TTS for narration
-   **VEED (via fal)** — Fabric 1.0 for talking video generation

(Plus: the scraper uses official Moroccan open data endpoints like CKAN APIs.)

---

## ▶️ Usage (MVP Flow)

From project root:

```bash
# 1) Prepare aggregated education data
python prepare_data.py

# 2) Run the full storytelling pipeline
python pipeline.py
```

This will:

-   Query the prepared data (fed by the scraper layer)
-   Generate a short narration script tailored to the chosen persona
-   Produce an MP3 narration via ElevenLabs (fal)
-   Produce an MP4 explainer video via VEED Fabric (fal)
-   Print the narration text to the console

---

## 🌍 Vision

Today, the MVP focuses on **education access by region**.
The same stack can extend to:

-   Employment and unemployment
-   Healthcare access and hospital coverage
-   Infrastructure & transport
-   Climate and water resources
-   Investment and trade flows

The long-term vision is a **national AI storytelling layer for Morocco**:
one API for all public data, and one video interface that makes it understandable for **citizens, students, journalists, policymakers, and foreign investors** in any language.
