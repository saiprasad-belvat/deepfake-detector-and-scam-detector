# 🛡️ AI Scam Shield

> **Advanced AI-powered detection for deepfakes, voice cloning, phishing, malware, and social engineering scams.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-red?logo=streamlit)](https://streamlit.io)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-orange?logo=tensorflow)](https://tensorflow.org)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-70%2B%20Engines-green)](https://virustotal.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the App](#-running-the-app)
- [AI Models](#-ai-models)
  - [How the Models Work](#how-the-models-work)
  - [Training Your Own Models](#training-your-own-models)
  - [Connecting Models to the App](#connecting-models-to-the-app)
  - [Free Datasets](#free-datasets)
- [Detection Modules](#-detection-modules)
- [API Reference (backend.py)](#-api-reference-backendpy)
- [VirusTotal Integration](#-virustotal-integration)
- [Deployment](#-deployment)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Disclaimer](#-disclaimer)

---

## 🔍 Overview

AI Scam Shield is a full-stack **Streamlit web application** that protects users from modern digital scams using a combination of:

- **Deep learning models** (CNN + LSTM) for deepfake image, video, and audio detection
- **Heuristic signal analysis** as a robust fallback when models are not loaded
- **VirusTotal integration** — scans files and URLs across 70+ antivirus and reputation engines
- **Rule-based NLP** for SMS/text scam and email header forensics

The app is designed for everyday users — no technical knowledge required to operate it.

---

## ✨ Features

| Module | What It Detects |
|--------|----------------|
| 🎥 **Video Analysis** | Deepfake face-swaps, lip-sync manipulation, fully synthetic clips, temporal inconsistencies |
| 🖼️ **Image Analysis** | AI-generated images (DALL-E / Midjourney / SD), Photoshop edits, face morphing, fake screenshots |
| 🎤 **Voice Analysis** | AI voice cloning, text-to-speech fraud, audio splicing, phone scam audio |
| 🌐 **URL Scanner** | Phishing domains, malware sites, suspicious TLDs, raw IP links, redirect chains |
| 💬 **Text / SMS Scam** | Urgency language, lottery scams, romance fraud, crypto scams, delivery scams — 10 rule sets |
| 📧 **Email Header** | SPF / DKIM / DMARC forensics, reply-to mismatch, bulk mailer detection, hop count |
| 🛡️ **Malware Scan** | VirusTotal file scan across 70+ AV engines for any uploaded file |
| 📊 **Scan History** | Session-wide log of all scans with type, verdict, confidence, and timestamp |
| 🎓 **Scam Academy** | 6 in-depth guides + interactive quiz + personal protection checklist |

---

## 📁 Project Structure

```
ai-scam-shield/
│
├── app.py                  # Main Streamlit frontend (all UI pages)
├── backend.py              # Detection logic, AI model loader, API integrations
├── train_models.py         # AI model training script (image / video / audio)
├── requirements.txt        # Python dependencies
│
├── model_image.h5          # (generated) Single-frame image deepfake model
├── model_video.h5          # (generated) 10-frame video sequence model
├── model_audio.h5          # (generated) Mel-spectrogram audio model
│
└── dataset/                # (you create) Training data — see AI Models section
    ├── image/
    │   ├── real/
    │   └── fake/
    ├── video/
    │   ├── real/
    │   └── fake/
    └── audio/
        ├── real/
        └── fake/
```

> **Note:** The `.h5` model files are not included in the repository. You must train them yourself using `train_models.py`. The app runs in heuristic-only mode without them.

---

## ⚙️ Installation

### Prerequisites

- Python **3.9 or higher**
- pip
- (Optional but recommended) A CUDA-compatible GPU for faster model training

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-scam-shield.git
cd ai-scam-shield
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Full dependency list:**

```
streamlit>=1.32.0
tensorflow>=2.13.0
opencv-python-headless>=4.8.0
numpy>=1.24.0
librosa>=0.10.0
requests>=2.31.0
pandas>=2.0.0
scikit-learn>=1.3.0
tqdm>=4.66.0
soundfile>=0.12.0
```

> ⚠️ On some systems, `librosa` requires `ffmpeg` for MP3 support:
> - **Ubuntu/Debian:** `sudo apt install ffmpeg`
> - **macOS:** `brew install ffmpeg`
> - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org) and add to PATH

---

## 🔧 Configuration

### VirusTotal API Key

Open `backend.py` and replace the placeholder with your own key:

```python
# backend.py — line ~14
API_KEY = "your_virustotal_api_key_here"
```

**Getting a free VirusTotal API key:**
1. Go to [virustotal.com](https://www.virustotal.com) and create a free account
2. Navigate to your profile → **API Key**
3. Copy the key and paste it into `backend.py`

> The free tier allows **4 requests/minute** and **500 requests/day** — sufficient for personal or demo use. For production, consider the premium API.

---

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

To specify a custom port:

```bash
streamlit run app.py --server.port 8080
```

---

## 🤖 AI Models

The app supports three separate deep learning models. All are **optional** — if a model file is not found, the corresponding detector falls back to heuristic-only analysis automatically.

### How the Models Work

| Model File | Architecture | Input Shape | Detects |
|------------|-------------|-------------|---------|
| `model_image.h5` | 4-layer CNN + Dense | `(128, 128, 3)` | Fake images |
| `model_video.h5` | TimeDistributed CNN + LSTM | `(10, 128, 128, 3)` | Fake video sequences |
| `model_audio.h5` | CNN on mel spectrogram | `(128, 128, 1)` | Cloned / synthetic voices |

When a model **is** loaded, predictions are blended:

```
final_score = 0.70 × AI_model_score + 0.30 × heuristic_score
```

This makes the system more robust — heuristics act as a sanity check against model overconfidence.

---

### Training Your Own Models

#### Step 1 — Install training dependencies

```bash
pip install tensorflow scikit-learn tqdm
```

#### Step 2 — Quick test with dummy data (no dataset needed)

This trains all three models on synthetic random data in about 2 minutes, just to confirm the pipeline works end-to-end:

```bash
python train_models.py --demo
```

#### Step 3 — Prepare your real dataset

Create the following folder structure and populate it with labelled media files:

```
dataset/
├── image/
│   ├── real/        ← authentic face photos (.jpg / .png / .webp)
│   └── fake/        ← deepfake / AI-generated face photos
├── video/
│   ├── real/        ← real video clips (.mp4 / .avi / .mov)
│   └── fake/        ← deepfake video clips
└── audio/
    ├── real/        ← genuine human speech (.wav / .mp3 / .flac)
    └── fake/        ← AI-cloned or TTS audio files
```

**Minimum recommended data per class:**
- Images: 500+ per class (real / fake)
- Videos: 200+ per class
- Audio:  500+ per class

#### Step 4 — Train the models

```bash
# Train all three models
python train_models.py

# Train only a specific model
python train_models.py --image
python train_models.py --video
python train_models.py --audio

# Combine flags
python train_models.py --image --audio
```

Training output files:

```
model_image.h5           ← final image model
model_video.h5           ← final video model
model_audio.h5           ← final audio model
model_image_checkpoint.h5   ← best checkpoint during training
model_video_checkpoint.h5
model_audio_checkpoint.h5
```

**Typical training time (CPU):**
| Model | ~200 samples/class | ~1000 samples/class |
|-------|--------------------|---------------------|
| Image | 5–10 min | 30–60 min |
| Video | 15–30 min | 1–3 hours |
| Audio | 5–10 min | 20–40 min |

GPU training is 5–10× faster.

---

### Connecting Models to the App

1. Copy the trained `.h5` files into the **same folder** as `app.py` and `backend.py`:

```
ai-scam-shield/
├── app.py
├── backend.py
├── model_image.h5      ← place here
├── model_video.h5      ← place here
└── model_audio.h5      ← place here
```

2. Restart the Streamlit app:

```bash
# Stop the running app with Ctrl+C, then:
streamlit run app.py
```

3. Check the terminal output — you should see:

```
✅ Image model loaded
✅ Video model loaded
✅ Audio model loaded
```

**No code changes are needed.** `backend.py` checks for the `.h5` files at startup and loads them automatically.

---

### Free Datasets

| Dataset | Type | Link |
|---------|------|------|
| FaceForensics++ | Video + Image | [github.com/ondyari/FaceForensics](https://github.com/ondyari/FaceForensics) |
| DFDC (Facebook) | Video | [ai.facebook.com/datasets/dfdc](https://ai.facebook.com/datasets/dfdc/) |
| Celeb-DF | Video | [github.com/yuezunli/celeb-deepfakeforensics](https://github.com/yuezunli/celeb-deepfakeforensics) |
| ASVspoof 2019 | Audio | [asvspoof.org](https://www.asvspoof.org/) |
| WaveFake | Audio | [github.com/RUB-SysSec/WaveFake](https://github.com/RUB-SysSec/WaveFake) |
| 140k Real/Fake Faces | Image | [kaggle.com/datasets/xhlulu/140k-real-and-fake-faces](https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces) |

---

## 🔬 Detection Modules

### Image Analysis — Forensic Signals

The image detector runs four parallel checks:

1. **Error Level Analysis (ELA)** — Re-compresses the image at 75% JPEG quality and computes pixel-level difference. Manipulated regions show higher ELA values because they have been compressed more times than the original.

2. **Sharpness / Blur Detection** — Uses the Laplacian variance. GAN-generated images often have unnaturally smooth textures, resulting in low sharpness scores.

3. **Noise Pattern Analysis** — Subtracts a Gaussian blur and measures the standard deviation of the residual. AI-generated images lack the natural sensor noise of real cameras.

4. **Brightness / Contrast Extremes** — Very dark or very bright images often indicate compositing artefacts.

---

### Video Analysis — Frame Pipeline

1. **Even Frame Sampling** — 10 frames are sampled evenly across the full clip, not just the beginning.
2. **Per-Frame Heuristic Scoring** — Each frame is scored independently.
3. **LSTM Temporal Reasoning** — The video model uses an LSTM layer to look for inconsistencies across frames over time (flicker, lighting shifts, unnatural motion).
4. **Aggregated Verdict** — Mean risk score across all frames determines the final result.
5. **Confidence Chart** — An area chart shows fake probability frame-by-frame so users can pinpoint the suspicious segment.

---

### Audio Analysis — Spectral Features

Four acoustic features are extracted:

| Feature | Fake Signal |
|---------|-------------|
| Zero Crossing Rate (ZCR) | TTS voices have unnaturally high ZCR |
| Spectral Flatness | Synthetic audio is more noise-like (flat spectrum) |
| MFCC Variance | Cloned voices have low prosodic variation across MFCCs |
| RMS Energy | Very low RMS can indicate silence-padded synthetic clips |

The audio model is trained on **mel spectrograms** — converting audio to a 128×128 grayscale image which a CNN can analyse like a photo.

---

### Text / SMS Scam — Rule Engine

10 weighted rule sets scan for:

- Urgency / pressure language
- Phishing call-to-action phrases
- Lottery and prize language
- Suspicious payment methods (gift cards, crypto, wire transfer)
- Sensitive data solicitation
- Get-rich-quick patterns
- Government impersonation
- Romance / advance-fee fraud markers
- Fake delivery scam language
- Account suspension phishing

Each match adds a weighted score. Final verdict: **FAKE** (≥55), **SUSPICIOUS** (25–54), **REAL** (<25).

---

### Email Header — Authentication Forensics

Parses raw email headers for:

| Check | What It Means |
|-------|---------------|
| **SPF FAIL** | Email not sent from an authorised server — strong spoofing indicator |
| **DKIM FAIL** | Email was modified in transit — tampered content |
| **DMARC FAIL** | From domain doesn't match sender — definitive spoofing |
| **Reply-To mismatch** | Reply goes to a different domain than the sender — common phishing trick |
| **Bulk mailer** | PHPMailer / Sendinblue / Mailchimp in X-Mailer header |
| **High hop count** | More than 8 Received hops — email routed unusually |

---

## 📦 API Reference (backend.py)

### `process_image(file) → (result, confidence, signals)`

| Param | Type | Description |
|-------|------|-------------|
| `file` | `BytesIO` | Uploaded image file object |

Returns `result` ∈ `{"FAKE", "SUSPICIOUS", "REAL", "ERROR"}`, `confidence` int 0–100, `signals` list of strings.

---

### `process_video(file) → (result, confidence, signals, frames, frame_results, frame_scores)`

| Return | Type | Description |
|--------|------|-------------|
| `frames` | `list[ndarray]` | 10 × (128,128,3) uint8 BGR arrays for display |
| `frame_results` | `list[str]` | Per-frame verdict strings |
| `frame_scores` | `list[float]` | Per-frame risk score 0–100 for chart |

---

### `process_audio(file) → (result, confidence, signals)`

Returns same structure as `process_image`.

---

### `analyze_text_for_scam(text) → (result, confidence, signals, category)`

| Return | Type | Description |
|--------|------|-------------|
| `signals` | `list[tuple]` | `(class_str, message)` where class ∈ `{"ok","warn","bad"}` |
| `category` | `str` | Classified scam type e.g. `"🎣 Phishing / Credential Theft"` |

---

### `analyze_email_headers(headers_text) → (result, confidence, signals, parsed)`

| Return | Type | Description |
|--------|------|-------------|
| `parsed` | `dict` | SPF, DKIM, DMARC values and any extra flags |

---

### `scan_with_virustotal(file) → analysis_id | None`

Uploads file to VirusTotal. Returns the analysis ID string for polling.

---

### `get_vt_result(analysis_id) → stats_dict | None`

Polls VirusTotal for a completed analysis. Returns `{"malicious": N, "suspicious": N, "harmless": N, ...}` or `None` if still pending.

---

### `scan_url(url) → result_dict`

Returns a dict containing:

```python
{
  "status":    "SAFE" | "SUSPICIOUS" | "UNSAFE" | "ERROR",
  "url":       str,
  "ip":        str,
  "country":   str,
  "city":      str,
  "isp":       str,
  "org":       str,
  "hosting":   bool,
  "vt_stats":  {"malicious": N, "suspicious": N, "harmless": N}
}
```

---

## 🌐 VirusTotal Integration

The app uses two VirusTotal v3 API endpoints:

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v3/files` | Upload a file for malware scanning |
| `POST /api/v3/urls` | Submit a URL for reputation check |
| `GET /api/v3/analyses/{id}` | Poll for scan results |

**File scanning flow:**
```
Upload file → get analysis_id → poll every 3s (up to 30s) → display stats
```

**URL scanning flow:**
```
Submit URL → get analysis_id → poll every 3s (up to 18s) → display verdict
```

**Free tier limits:**
- 4 requests per minute
- 500 requests per day
- Files up to 32 MB

---

## 🚀 Deployment

### Streamlit Community Cloud (Free)

1. Push your project to a **public GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Set `app.py` as the main file
4. Add your VirusTotal API key as a **Secret**:
   - In Streamlit Cloud dashboard → **Settings** → **Secrets**
   - Add: `VT_API_KEY = "your_key_here"`
   - Update `backend.py` to read it: `import streamlit as st; API_KEY = st.secrets["VT_API_KEY"]`

> ⚠️ Do not commit your API key directly to a public repo.

---

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y ffmpeg libgl1-mesa-glx && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t ai-scam-shield .
docker run -p 8501:8501 ai-scam-shield
```

---

### Local Network Sharing

To make the app accessible on your local network (e.g. from a phone on the same Wi-Fi):

```bash
streamlit run app.py --server.address 0.0.0.0
```

Then visit `http://YOUR_LOCAL_IP:8501` from any device on the network.

---

## 🛠️ Troubleshooting

### `cv2` import error
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless
```

### `librosa` fails to load MP3 files
Install ffmpeg (see Installation section). For WAV files, no ffmpeg is needed.

### TensorFlow not found / model not loading
```bash
pip install tensorflow
```
The app will still run without TensorFlow — it falls back to heuristic analysis. The terminal will show:
```
⚠️ Running in HEURISTIC-ONLY mode
```

### VirusTotal returns 403 / 401
Your API key is invalid or quota exceeded. Get a fresh key at [virustotal.com](https://www.virustotal.com).

### Streamlit file uploader size limit
By default, Streamlit limits uploads to 200 MB. To increase it, create `.streamlit/config.toml`:

```toml
[server]
maxUploadSize = 500
```

### `model_image.h5` not being detected
Ensure the file is in the **exact same directory** as `backend.py`, not in a subfolder.

---

## 🤝 Contributing

Contributions are welcome! Areas where help is most valuable:

- **Better AI models** — Training on larger, more diverse datasets (FaceForensics++, DFDC)
- **Additional detection modules** — QR code URL extraction, document forgery detection
- **Performance** — Model quantisation for faster inference on CPU
- **Mobile UI** — Responsive layout improvements for small screens

To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/better-audio-model`
3. Make your changes and add tests if applicable
4. Open a Pull Request with a clear description

---

## ⚠️ Disclaimer

This tool is provided for **educational and protective purposes only**.

- Detection results are probabilistic — no AI system achieves 100% accuracy. Always cross-verify important findings through independent means.
- The heuristic-only mode (without trained `.h5` models) uses simple signal thresholds and should not be relied upon for high-stakes decisions.
- The VirusTotal integration scans files against third-party engines. Files you upload are subject to VirusTotal's [Terms of Service](https://www.virustotal.com/gui/terms-of-service).
- Do not use this tool for any illegal or unethical purpose.

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <strong>🛡️ AI Scam Shield</strong> — Built to protect people from digital deception<br>
  Powered by TensorFlow · OpenCV · Librosa · VirusTotal · Streamlit
</div>
