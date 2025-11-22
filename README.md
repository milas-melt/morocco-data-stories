# morocco-data-stories

Moroccan data is extremely fragmented. It sits in PDFs, Excel files, and government portals that most people never access — and with a large low-literacy population, even when data is available, it’s not understandable.
Investors face the same issue: they know Morocco is full of potential, but the information is hidden behind messy, inconsistent datasets.

Our solution is Morocco Data Stories — an AI system that transforms raw national data into short, simple, multilingual explainer videos.
We use OpenAI to interpret the data, ElevenLabs to narrate it, and VEED to automatically generate clean, animated videos.
In seconds, complex statistics become clear stories for citizens, students, and foreign investors.

Morocco has the data — we make it understandable.

## Components

-   UI

    -   Select the topic based on what's available
    -   Select language
    -   Short descriptio of who you are (maybe via audio?)

-   Data loader

    -   Local csv for now

-   Data processor

    -   Aggregation
    -   Summary table

-   Data summarisation for LLM input

-   Insight genetation

    -   OpenAI GPT 5

-   Narration audio engine

    -   ElevenLabs TTS API

-   Video composer

    -   Veed API via Fal
    -   img + audio => mp4

-   mp4 downloader
    -   To get back the output
