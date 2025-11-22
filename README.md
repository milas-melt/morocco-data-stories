# 🇲🇦 **Morocco Data Stories**

Moroccan data is fragmented. Critical national information lives in PDFs, Excel files, and government portals that most people never access — and with a large low-literacy population, even when data is available, it is not understandable.
Investors face the same issue: Morocco’s economic potential is huge, but insights are buried in inconsistent datasets.

**Morocco Data Stories** transforms raw national data into **simple, multilingual explainer videos**.
We combine **OpenAI**, **ElevenLabs**, and **VEED** to convert complex datasets into short, narrated videos that any Moroccan citizen — including those who cannot read — and international investors can instantly understand.

**Morocco has the data.
We make it understandable.**

---

# 🎯 **MVP Focus: Education Access by Region (Morocco – 2023)**

For the MVP, we use fresh 2023 datasets on Morocco’s school infrastructure:

-   Public primary schools
-   Public middle schools
-   Public high schools
-   Private schools

From these sources, the system computes:

-   **Total schools per region**
-   **Public vs private distribution**
-   **Basic indicators of education access**
-   **Regional inequalities**

This enables a powerful narrative:

> “Some Moroccan regions offer far more education access than others. This video explains where the gaps are — in clear, everyday language.”

---

# 🧱 **Architecture Overview**

### **1. Modern Web UI (Lovable – React + Next.js + Tailwind + shadcn/ui)**

A clean, elegant interface that allows users to:

-   Select persona (Citizen or Investor)
-   Select language (English, French, Arabic)
-   Select topic (Education Access — 2023)
-   Generate the video story
-   View the script and final MP4 directly in the browser

Lovable instantly produces a polished, production-grade UI with animations and components — perfect for hackathon demo quality.

---

### **2. Backend (FastAPI)**

The backend exposes a single endpoint:

```
POST /generate
→ persona, language, topic
→ returns: narration script + video (base64)
```

It orchestrates the full pipeline:

1. Load local cleaned CSV
2. Process data and summarize it for LLM
3. Generate narration script with OpenAI
4. Produce voiceover using ElevenLabs
5. Create video (MVP: local moviepy; full: VEED via fal.ai)
6. Return MP4 to the frontend

---

### **3. Data Loader**

Currently uses one cleaned CSV:

```
data/education_access_2023.csv
region,year,total_schools,public_schools,private_schools
```

Loaded locally for speed and reliability during the live demo.

---

### **4. Data Processor**

-   Normalizes region names
-   Aggregates schools by category
-   Builds a concise summary for the LLM
-   Computes top/bottom regions and totals

---

### **5. LLM Insight Generator (OpenAI)**

OpenAI creates a 160–200-word narration script tailored to the persona:

-   **Citizen:** simple, warm, accessible
-   **Investor:** analytical, opportunity-focused

---

### **6. Narration Engine (ElevenLabs)**

Converts the script to human-quality audio in:

-   English
-   French
-   Arabic (Darija optional)

---

### **7. Video Composer (MVP: moviepy)**

The soundtrack is combined with basic visuals:

-   static background
-   title card
-   summary text
-   later upgrade: charts + animations via VEED

The result is a short **MP4 video** returned to the UI.

---

# 🗺️ **Roadmap (Beyond the MVP)**

### 🚀 **1. VEED Integration via fal.ai**

Dynamic, animated videos with transitions, subtitles, and chart overlays.

### 🟩 **2. Chart generation**

-   Schools per region
-   Public vs private share
-   Regional inequality maps

### 🎤 **3. Voice-input persona detection**

User describes themselves → system infers persona via speech-to-text + LLM.

### 🌐 **4. Multilingual UI & narration**

Darija, Standard Arabic, French, English.

### 🔄 **5. Automated ingestion (CKAN API)**

Direct integration with Morocco’s open data portal.

---

# 🛠️ **Tech Stack**

| Layer            | Technology                                   |
| ---------------- | -------------------------------------------- |
| UI               | **Lovable (Next.js + Tailwind + shadcn/ui)** |
| Backend          | **FastAPI**                                  |
| LLM              | **OpenAI (GPT-4.1-mini)**                    |
| Audio Narration  | **ElevenLabs TTS**                           |
| Video Generation | **VEED (via fal.ai)** / moviepy fallback     |
| Data Source      | data.gov.ma (cleaned CSV)                    |

This satisfies the hackathon requirement of using **3+ partner technologies**.

---

# 💡 **How to Run (MVP)**

### Backend:

```
uvicorn server:app --reload
```

### Frontend:

```
npm install
npm run dev
```

Visit your localhost
