# Track 3: Vision & Multimodal AI — Hackathon Ideas

> AMD Developer Hackathon | May 4–10, 2026
> Hardware: AMD Instinct MI300X (192 GB HBM3e, 5.3 TB/s bandwidth)
> Stack: Llama 3.2 Vision, Qwen2.5-VL, vLLM/SGLang on ROCm

---

## Idea 1 — **InspectAI: Real-Time Industrial Defect Inspector with Conversational Explanation**

### Problem
Manufacturing quality control relies on narrow, single-class defect detectors that flag anomalies but never explain *why* something is defective. Operators must still interpret every alert manually.

### What You Build
A **multimodal inspection assistant** that ingests live camera frames from a production line, detects surface defects (scratches, dents, discoloration, cracks), and produces a **natural-language explanation** of every defect — type, severity, probable root cause, and recommended action — all in real time.

### Architecture

```
Camera Feed (images/video frames)
        │
        ▼
┌─────────────────────────────┐
│  vLLM serving Qwen2.5-VL   │  ← ROCm on MI300X
│  (batch data-parallel mode) │
└────────────┬────────────────┘
             │  structured JSON: {defect_type, severity, bbox, explanation}
             ▼
┌─────────────────────────────┐
│  Streamlit / Gradio Web UI  │
│  - Live annotated feed      │
│  - Operator chat sidebar    │
│  - Shift-level analytics    │
└─────────────────────────────┘
```

### Key Technical Highlights
- **Throughput showcase**: Use vLLM's batch-level data-parallel vision encoder (up to 45% throughput gain on MI300X) to process many frames/sec.
- **Structured output**: Constrain the model to return JSON with bounding boxes + explanations using guided decoding.
- **Conversational follow-up**: Operator can click a defect and ask "What caused this?" or "Show me similar defects from the last hour."

### Datasets to Bootstrap
- MVTec Anomaly Detection dataset (free, 5000+ high-res industrial images, 15 object/texture categories).
- SteelDefectX vision-language dataset for steel surfaces.

### Why It Wins
Judges want **high throughput** — this directly benchmarks MI300X bandwidth by streaming frames through a large VLM. It's also practical: every factory needs this.

---

## Idea 2 — **MedSight: Multimodal Radiology Co-Pilot**

### Problem
Radiologists review hundreds of scans per day. Missed findings on chest X-rays are one of the leading sources of diagnostic error. Existing CAD tools highlight regions but don't communicate reasoning.

### What You Build
A **radiology assistant** that accepts a chest X-ray (or CT slice), produces a structured radiology report draft, highlights suspicious regions with bounding boxes, and lets the physician ask follow-up questions in natural language ("Is this consolidation or atelectasis?", "Compare with the prior study").

### Architecture

```
DICOM / PNG X-ray upload
        │
        ▼
┌───────────────────────────────────┐
│ Llama 3.2 Vision 90B via vLLM    │  ← single MI300X (fits in 192 GB)
│ System prompt: radiology expert   │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│  Report Generation Module         │
│  - Findings + Impressions text    │
│  - Annotated image overlay        │
│  - Confidence scores per finding  │
└────────────┬──────────────────────┘
             │
             ▼
┌───────────────────────────────────┐
│  Gradio Chat Interface            │
│  - Upload image                   │
│  - View annotated results         │
│  - Conversational follow-up       │
└───────────────────────────────────┘
```

### Key Technical Highlights
- **90B model on a single GPU**: Llama 3.2 Vision 90B fits entirely in MI300X's 192 GB — impossible on most competing hardware. This is your differentiator.
- **Chain-of-thought prompting**: Use structured CoT to make the model reason step-by-step through anatomy before concluding, improving accuracy (AMD's own blog showed 2.3x accuracy gains with CoT on charts).
- **Multi-image comparison**: Leverage long context to feed current + prior study side by side.

### Datasets to Bootstrap
- NIH Chest X-ray dataset (112,000 images, 14 pathology labels, free).
- MIMIC-CXR (radiology reports paired with images).

### Why It Wins
Medical AI is a hackathon crowd-pleaser. Running the full 90B model on one GPU is a powerful hardware demo. The conversational interface goes beyond a simple classifier.

---

## Idea 3 — **SafetyLens: Construction Site Safety Monitor (Video + Audio)**

### Problem
Construction sites are dangerous. OSHA reports ~1,000 fatalities/year in the US alone. Current monitoring is manual or uses simple object detectors that can't interpret *context* (e.g., a worker near heavy machinery without a hard hat while a warning siren is sounding).

### What You Build
A **multimodal safety monitoring system** that processes video feeds and ambient audio from a job site, identifies safety violations (missing PPE, unauthorized zone entry, unsafe postures), and generates real-time alerts with natural-language explanations.

### Architecture

```
IP Camera Stream          Microphone Stream
   (video)                    (audio)
      │                          │
      ▼                          ▼
┌──────────────┐        ┌───────────────────┐
│ Frame sampler │        │ Whisper-large-v3  │
│ (1-5 FPS)    │        │ (audio → text)    │
└──────┬───────┘        └────────┬──────────┘
       │                         │
       ▼                         ▼
┌────────────────────────────────────────────┐
│  Qwen2.5-VL 72B (4-GPU TP=4)              │
│  Prompt: image + audio transcript          │
│  → safety violation analysis               │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│  Alert Dashboard                           │
│  - Violation type + severity               │
│  - Annotated frame snapshot                │
│  - Audio context ("alarm sounding")        │
│  - Historical violation trends             │
└────────────────────────────────────────────┘
```

### Key Technical Highlights
- **True multimodal** (video + audio): Goes beyond image-only to fuse visual and auditory signals — exactly what the track description asks for.
- **Temporal reasoning**: Feed sequences of frames to detect *actions* (worker climbing without harness), not just static poses.
- **Scalable serving**: vLLM with tensor parallelism across multiple MI300X GPUs for parallel stream processing.

### Datasets to Bootstrap
- SODA (Site Object Detection and Analysis) dataset.
- MOCS (Monitoring of Construction Sites) dataset for PPE detection.
- AudioSet for environmental sound classification.

### Why It Wins
It's **multimodal in the truest sense** (images + audio + text). Safety monitoring is a massive, underserved market. The video processing angle stresses MI300X memory bandwidth — exactly what AMD wants to showcase.

---

## Idea 4 — **AgriVision: Crop Disease Diagnosis from Drone Imagery + Weather Data**

### Problem
Farmers lose up to 40% of crop yield to diseases and pests annually. Drone imagery is increasingly available, but interpreting thousands of aerial images to spot early disease signs requires expert agronomists that are scarce and expensive.

### What You Build
A **multimodal agricultural assistant** that takes drone/satellite images of crop fields, combines them with structured weather data (temperature, humidity, rainfall), and produces per-field disease diagnoses with treatment recommendations in natural language.

### Architecture

```
Drone Images              Weather API (JSON)
(field patches)           (temp, humidity, rain)
      │                          │
      ▼                          ▼
┌────────────────────────────────────────────┐
│  Llama 3.2 Vision 11B via vLLM             │
│  Multimodal prompt:                        │
│  [image] + "Weather: 32°C, 95% humidity,  │
│   48mm rain last 3 days. Diagnose."        │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│  Output:                                   │
│  - Disease: Late Blight (Phytophthora)     │
│  - Confidence: High                        │
│  - Evidence: dark lesions on leaf margins  │
│  - Weather correlation: ideal conditions   │
│  - Rx: Apply fungicide within 48 hours     │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│  Map UI (Leaflet/Mapbox)                   │
│  - Geo-tagged field overlay                │
│  - Color-coded disease risk heatmap        │
│  - Click field → detailed diagnosis chat   │
└────────────────────────────────────────────┘
```

### Key Technical Highlights
- **Batch processing at scale**: Process hundreds of field patches in parallel using MI300X throughput — a realistic drone-survey scenario.
- **Cross-modal fusion**: Combine visual symptoms with weather context — the model must reason across both to make accurate diagnoses.
- **Actionable output**: Not just "disease detected" but specific treatment timelines.

### Datasets to Bootstrap
- PlantVillage dataset (54,000 images, 38 disease classes).
- PlantDoc dataset (real-field images with disease annotations).

### Why It Wins
Agriculture + AI is a high-impact, underrepresented category at hackathons — it stands out. The batch processing of drone imagery directly showcases MI300X throughput. It has clear social impact (food security).

---

## Idea 5 — **DocuMind: Multimodal Document Intelligence Pipeline**

### Problem
Enterprises drown in unstructured documents — invoices, contracts, engineering drawings, handwritten forms, scanned reports — that contain mixed text, tables, diagrams, and images. Current OCR pipelines extract text but lose spatial and visual context.

### What You Build
A **document understanding system** that accepts any document image (PDF page, photo of a form, technical drawing), extracts all structured data (tables, fields, amounts, signatures), understands diagrams and charts visually, and enables conversational Q&A over the document.

### Architecture

```
Document Upload (PDF / image / photo)
        │
        ▼
┌─────────────────────────────────┐
│  Page Renderer / Image Pipeline │
│  - PDF → page images           │
│  - Deskew, enhance             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Qwen2.5-VL 32B via SGLang     │  ← ROCm, MI300X
│  - OCR + layout understanding  │
│  - Table extraction → JSON     │
│  - Chart/diagram interpretation │
│  - Handwriting recognition     │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│  Document Chat Interface        │
│  - Extracted data sidebar       │
│  - "What's the total on pg 3?"  │
│  - "Summarize all line items"   │
│  - Export to CSV / structured   │
└─────────────────────────────────┘
```

### Key Technical Highlights
- **High-resolution support**: Qwen2.5-VL natively handles high-res document scans — critical for reading fine print and table cells.
- **Multi-page reasoning**: Use the 128K context window to feed multiple pages and reason across an entire document.
- **Practical demo**: Live demo with real receipts, invoices, or technical drawings is immediately impressive.

### Datasets to Bootstrap
- FUNSD (form understanding), SROIE (receipt OCR), DocVQA (document visual QA).
- Custom: Scan a few real invoices/contracts for live demo.

### Why It Wins
Document AI is a multi-billion dollar market. This is practical, demo-friendly (upload any document live), and directly leverages VLM capabilities. The 128K context window for multi-page docs is a strong MI300X memory showcase.

---

## Idea 6 (Bonus) — **AccessLens: Real-Time Visual Assistant for Visually Impaired Users**

### Problem
800+ million people globally live with vision impairment. Existing assistive tools provide basic object labeling but lack contextual, conversational understanding of complex scenes.

### What You Build
A **real-time visual assistant** that processes camera input (phone or smart glasses), describes the scene with spatial awareness, reads text (signs, labels, menus), identifies people and objects, and answers follow-up questions via voice.

### Architecture

```
Phone Camera / Smart Glasses
        │
        ▼
┌─────────────────────────────────┐
│  Llama 3.2 Vision 11B (fast)   │  ← vLLM on MI300X
│  + Whisper (speech-to-text)    │
│  + TTS engine (text-to-speech) │
└────────────┬────────────────────┘
             │
             ▼
     Voice response to user:
     "You're at a crosswalk. The
      signal shows 'Don't Walk'.
      A bus is approaching from
      your left, about 30 feet."
```

### Why It Wins
Maximum social impact. Voice-in, voice-out makes it truly multimodal (image + audio + text). The real-time requirement showcases MI300X inference speed. Accessibility projects resonate strongly with judges.

---

## Comparison Matrix

| Idea | Modalities | Model | Throughput Demo | Market Impact | Demo Appeal | Difficulty |
|------|-----------|-------|----------------|--------------|------------|------------|
| 1. InspectAI | Image + Text | Qwen2.5-VL | Very High (streaming) | Manufacturing | High | Medium |
| 2. MedSight | Image + Text | Llama 3.2 90B | Medium | Healthcare | Very High | Medium |
| 3. SafetyLens | Video + Audio + Text | Qwen2.5-VL 72B | High (multi-stream) | Construction | Very High | High |
| 4. AgriVision | Image + Structured Data | Llama 3.2 11B | High (batch) | Agriculture | High | Low-Medium |
| 5. DocuMind | Document Image + Text | Qwen2.5-VL 32B | Medium | Enterprise | Very High | Low-Medium |
| 6. AccessLens | Image + Audio + Text | Llama 3.2 11B | High (real-time) | Accessibility | Very High | Medium |

---

## Recommended Strategy

### If you want to maximize winning probability:
**Go with Idea 3 (SafetyLens)** — it's the most genuinely multimodal (video + audio + text), directly exercises MI300X memory bandwidth with video processing, and addresses a clear real-world problem. Judges will see you fully leveraged the hardware.

### If you want the easiest path to a polished demo:
**Go with Idea 5 (DocuMind)** — document upload → structured extraction → chat is straightforward to build, demo-friendly (everyone has documents), and still impressive. You can have a working prototype in hours.

### If you want maximum social impact points:
**Go with Idea 6 (AccessLens)** — accessibility projects consistently win hackathons because judges value social impact. The real-time voice interaction is a compelling demo.

---

## Quick-Start Checklist (Any Idea)

1. **Get MI300X access**: Register on AMD Developer Cloud, claim your $100 credits
2. **Set up the environment**:
   ```bash
   # Install vLLM with ROCm
   pip install vllm  # ROCm wheels auto-detected on AMD Developer Cloud

   # Or use SGLang
   pip install sglang[all]
   ```
3. **Launch model server**:
   ```bash
   # Example: Qwen2.5-VL-32B on single MI300X
   vllm serve Qwen/Qwen2.5-VL-32B-Instruct \
     --dtype bfloat16 \
     --max-model-len 32768 \
     --trust-remote-code

   # Example: Llama 3.2 Vision 90B on single MI300X
   vllm serve meta-llama/Llama-3.2-90B-Vision-Instruct \
     --dtype bfloat16 \
     --max-model-len 8192
   ```
4. **Build the frontend**: Gradio for fastest iteration, Streamlit for dashboards
5. **Prepare 3-minute pitch**: Problem → Solution → Live Demo → Impact → Tech Stack
6. **"Build in Public"**: Post progress on social media for the bonus prize track
