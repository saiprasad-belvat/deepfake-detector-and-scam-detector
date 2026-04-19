"""
backend.py — AI Scam Shield v2.0
Handles: Image, Video, Audio deepfake detection + VirusTotal + URL scanning
         + Text/SMS scam analysis + Email header parsing
"""

import cv2
import numpy as np
import tempfile
import os
import re
import socket
import requests
import librosa

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────
API_KEY = "0557477c478c3ff999c8c723673ab76a41a0aca4d8b652baa0d638846605c003"   # VirusTotal API key

# ─────────────────────────────────────────────
#  LOAD AI MODEL  (model.h5 — optional)
# ─────────────────────────────────────────────
model_image = None   # single-frame image / face model
model_video = None   # 10-frame video sequence model
model_audio = None   # audio spectrogram model

try:
    from tensorflow.keras.models import load_model

    # Image model  — input shape (128,128,3), output sigmoid 1
    if os.path.exists("model_image.h5"):
        model_image = load_model("model_image.h5")
        print("✅ Image model loaded")
    elif os.path.exists("model.h5"):
        model_image = load_model("model.h5")
        print("✅ Legacy model.h5 loaded for images")

    # Video model — input shape (1,10,128,128,3), output sigmoid 1
    if os.path.exists("model_video.h5"):
        model_video = load_model("model_video.h5")
        print("✅ Video model loaded")

    # Audio model — input shape (1,128,128,1), output sigmoid 1
    if os.path.exists("model_audio.h5"):
        model_audio = load_model("model_audio.h5")
        print("✅ Audio model loaded")

except Exception as e:
    print("⚠️  Keras not available or model load failed:", e)
    print("   Running in HEURISTIC-ONLY mode — all detections use rule-based fallbacks.")


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def _confidence_label(score: float):
    """Convert 0-1 prediction score to (result_str, confidence_int)."""
    if score >= 0.65:
        return "FAKE", int(score * 100)
    elif score >= 0.40:
        return "SUSPICIOUS", int(score * 100)
    else:
        return "REAL", int((1 - score) * 100)


# ─────────────────────────────────────────────
#  IMAGE DETECTION
# ─────────────────────────────────────────────
def process_image(file):
    """
    Returns: (result, confidence, signals)
    result     : "FAKE" | "SUSPICIOUS" | "REAL"
    confidence : int 0-100
    signals    : list[str]
    """
    file.seek(0)
    raw = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(raw, cv2.IMREAD_COLOR)

    if img is None:
        return "ERROR", 0, ["Could not decode image"]

    signals = []

    # ── Heuristic features ──────────────────
    gray   = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w   = gray.shape

    brightness = np.mean(gray)
    contrast   = np.std(gray)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()   # higher = sharper

    # ELA simulation: recompress and compare
    tmp_path = tempfile.mktemp(suffix=".jpg")
    cv2.imwrite(tmp_path, img, [cv2.IMWRITE_JPEG_QUALITY, 75])
    recompressed = cv2.imread(tmp_path)
    if recompressed is not None and recompressed.shape == img.shape:
        ela_diff = np.abs(img.astype(np.float32) - recompressed.astype(np.float32))
        ela_score = float(np.mean(ela_diff))
    else:
        ela_score = 0.0
    try:
        os.remove(tmp_path)
    except:
        pass

    # Noise analysis
    noise_std = float(np.std(img.astype(np.float32) - cv2.GaussianBlur(img, (5,5), 0).astype(np.float32)))

    # Build signal list
    signals.append(f"Brightness: {brightness:.1f}/255")
    signals.append(f"Contrast  : {contrast:.1f}")
    signals.append(f"Sharpness : {blur_score:.1f}")
    signals.append(f"ELA score : {ela_score:.2f}")
    signals.append(f"Noise σ   : {noise_std:.2f}")

    heuristic_score = 0.0

    if ela_score > 12:
        heuristic_score += 0.35
        signals.append("⚠️ High ELA anomaly — possible manipulation")
    if blur_score < 50:
        heuristic_score += 0.20
        signals.append("⚠️ Unusually low sharpness — GAN smoothing?")
    if noise_std < 3.5:
        heuristic_score += 0.20
        signals.append("⚠️ Unnaturally low noise — AI-generated?")
    if brightness < 60 or brightness > 220:
        heuristic_score += 0.10
        signals.append("⚠️ Extreme brightness may indicate compositing")

    # ── AI model (if loaded) ─────────────────
    if model_image is not None:
        try:
            inp = cv2.resize(img, (128, 128)).astype(np.float32) / 255.0
            inp = np.expand_dims(inp, axis=0)          # (1,128,128,3)
            ai_score = float(model_image.predict(inp, verbose=0)[0][0])
            # Blend: 70% AI, 30% heuristic
            final_score = 0.70 * ai_score + 0.30 * heuristic_score
            signals.append(f"🤖 AI model score: {ai_score:.3f}")
        except Exception as ex:
            final_score = heuristic_score
            signals.append(f"⚠️ AI model error ({ex}) — heuristic only")
    else:
        final_score = heuristic_score
        signals.append("ℹ️ Running heuristic analysis (no model_image.h5 found)")

    result, confidence = _confidence_label(final_score)
    return result, confidence, signals


# ─────────────────────────────────────────────
#  VIDEO DETECTION
# ─────────────────────────────────────────────
def process_video(file):
    """
    Returns: (result, confidence, signals, frames_list, frame_results, frame_scores)
    frames_list  : list of (128,128,3) uint8 BGR arrays (displayable)
    frame_results: list of "FAKE"|"SUSPICIOUS"|"REAL" per frame
    frame_scores : list of float 0-1 per frame
    """
    file.seek(0)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(file.read())
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()

    cap = cv2.VideoCapture(tmp_path)

    frames_raw     = []   # (128,128,3) float32 normalized — for model
    frames_display = []   # (128,128,3) uint8               — for UI
    frame_scores   = []
    frame_results  = []

    TARGET_FRAMES = 10
    total_vid_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    step = max(1, total_vid_frames // TARGET_FRAMES)

    frame_idx = 0
    while len(frames_raw) < TARGET_FRAMES:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += step

        resized      = cv2.resize(frame, (128, 128))
        normalized   = resized.astype(np.float32) / 255.0
        frames_raw.append(normalized)
        frames_display.append(resized)  # keep uint8 for st.image

        # Per-frame heuristic: brightness as proxy
        score_h = 1.0 - np.mean(normalized)   # darker = more suspicious (rough)
        frame_scores.append(float(score_h))
        if score_h > 0.65:
            frame_results.append("FAKE")
        elif score_h > 0.45:
            frame_results.append("SUSPICIOUS")
        else:
            frame_results.append("REAL")

    cap.release()
    try:
        os.remove(tmp_path)
    except:
        pass

    if len(frames_raw) == 0:
        return "ERROR", 0, ["No frames extracted"], [], [], []

    # Pad to TARGET_FRAMES if video was too short
    while len(frames_raw) < TARGET_FRAMES:
        frames_raw.append(frames_raw[-1])
        frame_scores.append(frame_scores[-1])
        frame_results.append(frame_results[-1])

    frames_np = np.array(frames_raw[:TARGET_FRAMES])       # (10,128,128,3)
    frames_np = np.expand_dims(frames_np, axis=0)          # (1,10,128,128,3)

    heuristic_score = float(np.mean(frame_scores[:TARGET_FRAMES]))

    # ── AI model (if loaded) ─────────────────
    if model_video is not None:
        try:
            ai_score    = float(model_video.predict(frames_np, verbose=0)[0][0])
            final_score = 0.70 * ai_score + 0.30 * heuristic_score
        except Exception as ex:
            final_score = heuristic_score
    else:
        final_score = heuristic_score

    # Map 0-1 score to percentage list for chart
    chart_scores = [round(s * 100, 1) for s in frame_scores[:TARGET_FRAMES]]

    result, confidence = _confidence_label(final_score)
    signals = [
        f"Frames analyzed : {len(frames_raw[:TARGET_FRAMES])}",
        f"Mean risk score : {final_score:.3f}",
        f"Peak frame score: {max(frame_scores[:TARGET_FRAMES]):.3f}",
    ]
    return result, confidence, signals, frames_display[:TARGET_FRAMES], frame_results[:TARGET_FRAMES], chart_scores


# ─────────────────────────────────────────────
#  AUDIO DETECTION
# ─────────────────────────────────────────────
def process_audio(file):
    """
    Returns: (result, confidence, signals)
    """
    file.seek(0)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(file.read())
    tmp.flush()
    tmp_path = tmp.name
    tmp.close()

    signals = []

    try:
        y, sr = librosa.load(tmp_path, sr=None, mono=True)
    except Exception as ex:
        try:
            os.remove(tmp_path)
        except:
            pass
        return "ERROR", 0, [f"Audio load failed: {ex}"]

    try:
        os.remove(tmp_path)
    except:
        pass

    # ── Heuristic features ──────────────────
    zcr         = float(np.mean(librosa.feature.zero_crossing_rate(y)))
    rms         = float(np.mean(librosa.feature.rms(y=y)))
    mfccs       = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mfcc_mean   = float(np.mean(np.std(mfccs, axis=1)))  # variance of MFCCs
    spec_flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))

    signals.append(f"ZCR           : {zcr:.4f}")
    signals.append(f"RMS energy    : {rms:.4f}")
    signals.append(f"MFCC variance : {mfcc_mean:.4f}")
    signals.append(f"Spectral flat : {spec_flatness:.4f}")

    heuristic_score = 0.0

    if zcr > 0.25:
        heuristic_score += 0.35
        signals.append("⚠️ High zero-crossing rate — synthetic speech pattern")
    if spec_flatness > 0.15:
        heuristic_score += 0.25
        signals.append("⚠️ High spectral flatness — noise-like timbre (TTS signal)")
    if mfcc_mean < 5.0:
        heuristic_score += 0.20
        signals.append("⚠️ Low MFCC variance — unnaturally consistent prosody")
    if rms < 0.01:
        heuristic_score += 0.10
        signals.append("⚠️ Very low RMS — possibly silence-padded synthetic audio")

    # ── AI model (if loaded) ─────────────────
    if model_audio is not None:
        try:
            # Build mel spectrogram (128x128 single channel)
            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            mel_db = librosa.power_to_db(mel, ref=np.max)
            # Resize to 128x128
            mel_resized = cv2.resize(mel_db, (128, 128))
            mel_resized = (mel_resized - mel_resized.min()) / (mel_resized.max() - mel_resized.min() + 1e-6)
            inp = mel_resized[np.newaxis, :, :, np.newaxis].astype(np.float32)  # (1,128,128,1)
            ai_score    = float(model_audio.predict(inp, verbose=0)[0][0])
            final_score = 0.70 * ai_score + 0.30 * heuristic_score
            signals.append(f"🤖 AI model score: {ai_score:.3f}")
        except Exception as ex:
            final_score = heuristic_score
            signals.append(f"⚠️ Audio model error ({ex}) — heuristic only")
    else:
        final_score = heuristic_score
        signals.append("ℹ️ Running heuristic analysis (no model_audio.h5 found)")

    result, confidence = _confidence_label(final_score)
    return result, confidence, signals


# ─────────────────────────────────────────────
#  TEXT / SMS SCAM ANALYSIS
# ─────────────────────────────────────────────
def analyze_text_for_scam(text: str):
    """
    Heuristic pattern-matching scam detector for plain text messages.
    Returns: (result, confidence, signals)
    signals: list of (class_str, message_str)  class ∈ {"ok","warn","bad"}
    """
    signals = []
    score   = 0
    t       = text.lower()

    rule_sets = [
        (["urgent", "act now", "limited time", "expires soon", "immediately", "respond now"],
         "Urgency / pressure language detected", "bad", 15),
        (["click here", "verify your account", "confirm your details", "login now", "sign in immediately"],
         "Phishing call-to-action detected", "bad", 20),
        (["congratulations", "you have won", "selected winner", "unclaimed prize", "claim your prize"],
         "Lottery / prize scam language", "bad", 20),
        (["wire transfer", "bitcoin", "crypto", "gift card", "itunes card", "western union", "moneygram"],
         "Suspicious payment method requested", "bad", 25),
        (["social security", "ssn", "bank account number", "credit card number", "full password", "pin number"],
         "Sensitive data solicitation", "bad", 30),
        (["free money", "make money fast", "work from home guaranteed", "passive income", "no experience needed"],
         "Get-rich-quick / work-from-home scam", "bad", 15),
        (["irs", "tax refund pending", "government grant", "fbi warning", "interpol", "court order"],
         "Government impersonation signals", "bad", 20),
        (["my darling", "sweetheart", "my love", "beloved", "kindly send", "dear friend, i need"],
         "Romance / advance-fee scam patterns", "bad", 15),
        (["your package is on hold", "usps", "fedex", "dhl delivery fee", "customs clearance fee"],
         "Fake delivery / package scam", "bad", 20),
        (["your account has been suspended", "unusual activity detected", "security alert"],
         "Account suspension phishing", "bad", 20),
    ]

    for keywords, label, cls, weight in rule_sets:
        if any(kw in t for kw in keywords):
            signals.append((cls, label))
            score += weight

    # Positive signals
    if len(text) > 600:
        signals.append(("ok", "Message has substantial length (less common in spam)"))
    if not re.search(r'http|bit\.ly|tinyurl|t\.co', t):
        signals.append(("ok", "No suspicious short URLs detected"))
    else:
        signals.append(("warn", "Contains URLs — verify before clicking"))
        score += 5

    # Scam category
    category = "Unknown / General Fraud"
    if any(kw in t for kw in ["prize", "winner", "congratulations", "lottery"]):
        category = "🎰 Lottery / Prize Scam"
    elif any(kw in t for kw in ["bank", "account", "verify", "login", "suspended"]):
        category = "🎣 Phishing / Credential Theft"
    elif any(kw in t for kw in ["love", "sweetheart", "darling", "dear friend"]):
        category = "💔 Romance / Advance-Fee Fraud"
    elif any(kw in t for kw in ["irs", "tax", "government", "grant", "fbi"]):
        category = "🏛️ Government Impersonation"
    elif any(kw in t for kw in ["bitcoin", "crypto", "investment", "trading"]):
        category = "💰 Crypto / Investment Fraud"
    elif any(kw in t for kw in ["package", "usps", "fedex", "dhl", "customs"]):
        category = "📦 Fake Delivery Scam"
    elif any(kw in t for kw in ["work from home", "make money", "passive income"]):
        category = "💼 Work-From-Home / MLM Scam"

    score = min(score, 100)
    if score >= 55:
        result, confidence = "FAKE", score
    elif score >= 25:
        result, confidence = "SUSPICIOUS", score
    else:
        result, confidence = "REAL", max(60, 100 - score)

    return result, confidence, signals, category


# ─────────────────────────────────────────────
#  EMAIL HEADER ANALYSIS
# ─────────────────────────────────────────────
def analyze_email_headers(headers_text: str):
    """
    Parse raw email headers for SPF / DKIM / DMARC results.
    Returns: (result, confidence, signals, parsed_dict)
    """
    signals    = []
    score      = 0
    t          = headers_text.lower()
    parsed     = {}

    # ── SPF ─────────────────────────────────
    spf_match = re.search(r'spf=(pass|fail|softfail|neutral|none|temperror|permerror)', t)
    if spf_match:
        spf = spf_match.group(1)
        parsed["SPF"] = spf.upper()
        if spf == "pass":
            signals.append(("ok",   "SPF: PASS — sender server is authorised"))
        elif spf in ("fail", "permerror"):
            signals.append(("bad",  "SPF: FAIL — sender domain is SPOOFED"))
            score += 35
        elif spf in ("softfail", "neutral"):
            signals.append(("warn", "SPF: SOFTFAIL — domain not fully restricted"))
            score += 15
    else:
        signals.append(("warn", "SPF record not found in headers"))
        parsed["SPF"] = "NOT FOUND"
        score += 10

    # ── DKIM ────────────────────────────────
    dkim_match = re.search(r'dkim=(pass|fail|none|neutral|policy|temperror|permerror)', t)
    if dkim_match:
        dkim = dkim_match.group(1)
        parsed["DKIM"] = dkim.upper()
        if dkim == "pass":
            signals.append(("ok",  "DKIM: PASS — email signature is valid"))
        elif dkim in ("fail", "permerror"):
            signals.append(("bad", "DKIM: FAIL — email was TAMPERED in transit"))
            score += 35
        else:
            signals.append(("warn", f"DKIM: {dkim.upper()} — inconclusive"))
            score += 10
    else:
        signals.append(("warn", "DKIM record not found in headers"))
        parsed["DKIM"] = "NOT FOUND"
        score += 10

    # ── DMARC ───────────────────────────────
    dmarc_match = re.search(r'dmarc=(pass|fail|none|bestguesspass)', t)
    if dmarc_match:
        dmarc = dmarc_match.group(1)
        parsed["DMARC"] = dmarc.upper()
        if dmarc == "pass":
            signals.append(("ok",  "DMARC: PASS — policy satisfied"))
        elif dmarc == "fail":
            signals.append(("bad", "DMARC: FAIL — definitive spoofing indicator"))
            score += 30
    else:
        signals.append(("warn", "DMARC record not found in headers"))
        parsed["DMARC"] = "NOT FOUND"
        score += 5

    # ── Extra heuristics ────────────────────
    # Reply-To mismatch
    from_match    = re.search(r'from:\s*[\w.+-]+@([\w.-]+)', t)
    replyto_match = re.search(r'reply-to:\s*[\w.+-]+@([\w.-]+)', t)
    if from_match and replyto_match:
        if from_match.group(1) != replyto_match.group(1):
            signals.append(("bad", f"Reply-To domain ({replyto_match.group(1)}) differs from From domain — common phishing trick"))
            score += 20
            parsed["Reply-To Mismatch"] = "YES"

    # Bulk mailer
    if re.search(r'x-mailer:\s*(phpmailer|massmailer|bulk|sendinblue|mailchimp)', t):
        signals.append(("warn", "Bulk mailing software detected in X-Mailer"))
        score += 10
        parsed["Bulk Mailer"] = "YES"

    # Received hops count
    hops = len(re.findall(r'^received:', t, re.MULTILINE))
    parsed["Received Hops"] = hops
    if hops > 8:
        signals.append(("warn", f"Unusually high hop count ({hops}) — email routed through many servers"))
        score += 5

    score = min(score, 100)
    if score >= 50:
        result, confidence = "FAKE", score
    elif score >= 25:
        result, confidence = "SUSPICIOUS", score
    else:
        result, confidence = "REAL", max(60, 100 - score)

    return result, confidence, signals, parsed


# ─────────────────────────────────────────────
#  VIRUSTOTAL — FILE SCAN
# ─────────────────────────────────────────────
def scan_with_virustotal(file):
    """Upload file to VT and return analysis ID."""
    file.seek(0)
    url     = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": API_KEY}
    try:
        res = requests.post(url, files={"file": file.read()}, headers=headers, timeout=30)
        if res.status_code == 200:
            return res.json()["data"]["id"]
        print(f"VT upload failed: {res.status_code} {res.text[:200]}")
    except Exception as e:
        print(f"VT upload exception: {e}")
    return None


def get_vt_result(analysis_id: str):
    """Poll VT analysis result."""
    url     = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {"x-apikey": API_KEY}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            attrs = res.json()["data"]["attributes"]
            if attrs.get("status") == "completed":
                return attrs.get("stats", {})
    except Exception as e:
        print(f"VT poll exception: {e}")
    return None


# ─────────────────────────────────────────────
#  URL SCAN
# ─────────────────────────────────────────────
def get_website_info(url: str):
    """Resolve domain to IP and geolocate via ip-api.com."""
    try:
        if not url.startswith("http"):
            url = "https://" + url
        domain = url.split("//")[-1].split("/")[0].split("?")[0]
        ip     = socket.gethostbyname(domain)
        res    = requests.get(f"http://ip-api.com/json/{ip}", timeout=8)
        data   = res.json()
        return {
            "ip":      ip,
            "country": data.get("country", "Unknown"),
            "region":  data.get("regionName", "Unknown"),
            "city":    data.get("city", "Unknown"),
            "isp":     data.get("isp", "Unknown"),
            "org":     data.get("org", "Unknown"),
            "hosting": data.get("hosting", False),
        }
    except Exception as e:
        return {"ip": "Unresolvable", "country": "Unknown", "org": str(e), "hosting": False}


def scan_url(url: str):
    """
    Full URL scan: geo-info + VirusTotal.
    Returns a dict with status, geo info, and VT stats.
    """
    result = {"status": "UNKNOWN", "url": url}
    result.update(get_website_info(url))

    headers = {"x-apikey": API_KEY}
    try:
        scan = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url},
            timeout=20,
        )
        if scan.status_code != 200:
            result["status"] = "ERROR"
            result["error"]  = f"VT submit failed: {scan.status_code}"
            return result

        url_id = scan.json()["data"]["id"]
        import time

        for attempt in range(6):
            time.sleep(3)
            analysis = requests.get(
                f"https://www.virustotal.com/api/v3/analyses/{url_id}",
                headers=headers,
                timeout=15,
            )
            if analysis.status_code == 200:
                attrs = analysis.json()["data"]["attributes"]
                if attrs.get("status") == "completed":
                    stats = attrs.get("stats", {})
                    result["vt_stats"] = stats
                    mal = stats.get("malicious", 0)
                    sus = stats.get("suspicious", 0)
                    if mal > 0:
                        result["status"] = "UNSAFE"
                    elif sus > 0:
                        result["status"] = "SUSPICIOUS"
                    else:
                        result["status"] = "SAFE"
                    break
            result["status"] = "PENDING"

    except Exception as e:
        result["status"] = "ERROR"
        result["error"]  = str(e)

    return result
