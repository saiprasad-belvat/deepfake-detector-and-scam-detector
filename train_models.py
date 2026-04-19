"""
train_models.py — AI Scam Shield v2.0
======================================
Trains three CNN models for deepfake detection:
  • model_image.h5  — single-frame image classifier     (input: 128x128x3)
  • model_video.h5  — 10-frame video sequence classifier (input: 10x128x128x3)
  • model_audio.h5  — mel-spectrogram audio classifier   (input: 128x128x1)

HOW TO USE
──────────
1. Install dependencies:
       pip install tensorflow opencv-python librosa numpy scikit-learn

2. Organise your dataset like this:
       dataset/
         image/
           real/   ← real face photos  (.jpg / .png)
           fake/   ← deepfake photos   (.jpg / .png)
         video/
           real/   ← real video clips  (.mp4 / .avi)
           fake/   ← deepfake clips    (.mp4 / .avi)
         audio/
           real/   ← genuine speech    (.wav / .mp3)
           fake/   ← cloned / TTS      (.wav / .mp3)

   Free datasets to get started:
       • FaceForensics++  — https://github.com/ondyari/FaceForensics
       • DFDC Preview     — https://ai.facebook.com/datasets/dfdc/
       • ASVspoof 2019    — https://www.asvspoof.org/

3. Run:
       python train_models.py

4. Copy the output .h5 files into the same folder as backend.py / app.py.
   The backend auto-loads them at startup.

QUICK-START (no dataset yet)
─────────────────────────────
Run with --demo flag to train on synthetic dummy data so you can test
the full pipeline immediately:
       python train_models.py --demo
"""

import os
import sys
import argparse
import numpy as np
import cv2
import librosa

# ── Optional progress bar ──
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(it, **kw):
        return it

# ─────────────────────────────────────────────
#  CONFIG — edit these as needed
# ─────────────────────────────────────────────
IMAGE_SIZE   = 128        # pixels — do not change without also changing backend.py
N_FRAMES     = 10         # frames per video clip sampled
N_MELS       = 128        # mel bands for audio spectrogram
EPOCHS_IMG   = 20
EPOCHS_VID   = 15
EPOCHS_AUD   = 20
BATCH_SIZE   = 16
DATASET_ROOT = "dataset"

# ─────────────────────────────────────────────
#  TENSORFLOW / KERAS IMPORTS
# ─────────────────────────────────────────────
try:
    import tensorflow as tf
    from tensorflow.keras import layers, models, callbacks, optimizers
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from sklearn.model_selection import train_test_split
    print(f"✅ TensorFlow {tf.__version__} ready")
except ImportError:
    print("❌  TensorFlow not installed.\n    Run:  pip install tensorflow")
    sys.exit(1)

gpus = tf.config.list_physical_devices("GPU")
if gpus:
    print(f"🚀 GPU detected: {gpus[0].name}")
    tf.config.experimental.set_memory_growth(gpus[0], True)
else:
    print("ℹ️  No GPU found — training on CPU (slower but works fine for demo)")


# ─────────────────────────────────────────────
#  CALLBACKS  (used by all three trainers)
# ─────────────────────────────────────────────
def make_callbacks(model_name: str):
    return [
        callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True, verbose=1
        ),
        callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1
        ),
        callbacks.ModelCheckpoint(
            filepath=f"{model_name}_checkpoint.h5",
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
    ]


# ═══════════════════════════════════════════
#  1.  IMAGE MODEL
# ═══════════════════════════════════════════
def build_image_model() -> tf.keras.Model:
    """
    CNN for single-image deepfake detection.
    Input : (128, 128, 3)  float32 in [0, 1]
    Output: sigmoid scalar — 1 = FAKE, 0 = REAL
    """
    inp = layers.Input(shape=(IMAGE_SIZE, IMAGE_SIZE, 3))

    x = layers.Conv2D(32, 3, activation="relu", padding="same")(inp)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(128, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(256, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dense(256, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(64,  activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(1,  activation="sigmoid")(x)

    model = models.Model(inp, out, name="image_deepfake_detector")
    model.compile(
        optimizer=optimizers.Adam(1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")],
    )
    model.summary()
    return model


def load_image_dataset(root: str):
    """Load real/fake images from dataset/image/real|fake/"""
    X, y = [], []
    for label, folder in [(0, "real"), (1, "fake")]:
        path = os.path.join(root, "image", folder)
        if not os.path.isdir(path):
            print(f"  ⚠️  Missing folder: {path}")
            continue
        files = [f for f in os.listdir(path) if f.lower().endswith((".jpg",".jpeg",".png",".webp"))]
        print(f"  → {folder}: {len(files)} images")
        for fname in tqdm(files, desc=folder):
            img = cv2.imread(os.path.join(path, fname))
            if img is None:
                continue
            img = cv2.resize(img, (IMAGE_SIZE, IMAGE_SIZE)).astype(np.float32) / 255.0
            X.append(img)
            y.append(label)
    return np.array(X), np.array(y)


def train_image_model(demo=False):
    print("\n" + "═"*50)
    print("  TRAINING IMAGE MODEL")
    print("═"*50)

    if demo:
        print("  [DEMO] Generating synthetic data...")
        N = 200
        X = np.random.rand(N, IMAGE_SIZE, IMAGE_SIZE, 3).astype(np.float32)
        # Fake images are slightly brighter (synthetic signal)
        y = np.array([0]*100 + [1]*100)
        X[100:] += 0.15
        X = np.clip(X, 0, 1)
    else:
        X, y = load_image_dataset(DATASET_ROOT)
        if len(X) == 0:
            print("  ❌ No image data found. Skipping image model.")
            return

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    print(f"  Train: {len(X_train)}  Val: {len(X_val)}")

    # Data augmentation
    datagen = ImageDataGenerator(
        rotation_range=15,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True,
        zoom_range=0.1,
        brightness_range=[0.8, 1.2],
    )
    datagen.fit(X_train)

    model = build_image_model()
    model.fit(
        datagen.flow(X_train, y_train, batch_size=BATCH_SIZE),
        validation_data=(X_val, y_val),
        epochs=EPOCHS_IMG,
        callbacks=make_callbacks("model_image"),
        verbose=1,
    )
    model.save("model_image.h5")
    print("  ✅ Saved → model_image.h5")


# ═══════════════════════════════════════════
#  2.  VIDEO MODEL  (TimeDistributed CNN + LSTM)
# ═══════════════════════════════════════════
def build_video_model() -> tf.keras.Model:
    """
    TimeDistributed CNN + LSTM for video sequence deepfake detection.
    Input : (N_FRAMES, 128, 128, 3)
    Output: sigmoid scalar
    """
    inp = layers.Input(shape=(N_FRAMES, IMAGE_SIZE, IMAGE_SIZE, 3))

    # Per-frame feature extraction (shared weights)
    x = layers.TimeDistributed(layers.Conv2D(32, 3, activation="relu", padding="same"))(inp)
    x = layers.TimeDistributed(layers.MaxPooling2D())(x)
    x = layers.TimeDistributed(layers.Conv2D(64, 3, activation="relu", padding="same"))(x)
    x = layers.TimeDistributed(layers.MaxPooling2D())(x)
    x = layers.TimeDistributed(layers.Conv2D(128, 3, activation="relu", padding="same"))(x)
    x = layers.TimeDistributed(layers.GlobalAveragePooling2D())(x)  # → (batch, N_FRAMES, 128)

    # Temporal reasoning
    x = layers.LSTM(128, return_sequences=True)(x)
    x = layers.LSTM(64)(x)

    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    out = layers.Dense(1, activation="sigmoid")(x)

    model = models.Model(inp, out, name="video_deepfake_detector")
    model.compile(
        optimizer=optimizers.Adam(1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()
    return model


def load_video_dataset(root: str):
    """Sample N_FRAMES evenly from each video."""
    X, y = [], []
    for label, folder in [(0, "real"), (1, "fake")]:
        path = os.path.join(root, "video", folder)
        if not os.path.isdir(path):
            print(f"  ⚠️  Missing folder: {path}")
            continue
        files = [f for f in os.listdir(path) if f.lower().endswith((".mp4",".avi",".mov",".mkv"))]
        print(f"  → {folder}: {len(files)} videos")
        for fname in tqdm(files, desc=folder):
            cap = cv2.VideoCapture(os.path.join(path, fname))
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
            step  = max(1, total // N_FRAMES)
            frames = []
            for i in range(N_FRAMES):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i * step)
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.resize(frame, (IMAGE_SIZE, IMAGE_SIZE)).astype(np.float32) / 255.0
                frames.append(frame)
            cap.release()
            if len(frames) < N_FRAMES:
                while len(frames) < N_FRAMES:
                    frames.append(frames[-1] if frames else np.zeros((IMAGE_SIZE, IMAGE_SIZE, 3), np.float32))
            X.append(np.array(frames[:N_FRAMES]))
            y.append(label)
    return np.array(X), np.array(y)


def train_video_model(demo=False):
    print("\n" + "═"*50)
    print("  TRAINING VIDEO MODEL")
    print("═"*50)

    if demo:
        print("  [DEMO] Generating synthetic video sequences...")
        N = 60
        X = np.random.rand(N, N_FRAMES, IMAGE_SIZE, IMAGE_SIZE, 3).astype(np.float32)
        y = np.array([0]*30 + [1]*30)
        X[30:] += 0.1
        X = np.clip(X, 0, 1)
    else:
        X, y = load_video_dataset(DATASET_ROOT)
        if len(X) == 0:
            print("  ❌ No video data found. Skipping video model.")
            return

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    print(f"  Train: {len(X_train)}  Val: {len(X_val)}")

    model = build_video_model()
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS_VID,
        batch_size=max(4, BATCH_SIZE // 2),
        callbacks=make_callbacks("model_video"),
        verbose=1,
    )
    model.save("model_video.h5")
    print("  ✅ Saved → model_video.h5")


# ═══════════════════════════════════════════
#  3.  AUDIO MODEL  (Mel-Spectrogram CNN)
# ═══════════════════════════════════════════
def build_audio_model() -> tf.keras.Model:
    """
    CNN trained on mel-spectrogram images for voice-clone detection.
    Input : (128, 128, 1)  — grayscale mel spectrogram
    Output: sigmoid scalar
    """
    inp = layers.Input(shape=(N_MELS, IMAGE_SIZE, 1))

    x = layers.Conv2D(32, 3, activation="relu", padding="same")(inp)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(64, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.MaxPooling2D()(x)

    x = layers.Conv2D(128, 3, activation="relu", padding="same")(x)
    x = layers.BatchNormalization()(x)
    x = layers.GlobalAveragePooling2D()(x)

    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.4)(x)
    out = layers.Dense(1,   activation="sigmoid")(x)

    model = models.Model(inp, out, name="audio_deepfake_detector")
    model.compile(
        optimizer=optimizers.Adam(1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )
    model.summary()
    return model


def load_audio_dataset(root: str):
    """Load audio files and convert to mel spectrogram arrays."""
    X, y = [], []
    for label, folder in [(0, "real"), (1, "fake")]:
        path = os.path.join(root, "audio", folder)
        if not os.path.isdir(path):
            print(f"  ⚠️  Missing folder: {path}")
            continue
        files = [f for f in os.listdir(path) if f.lower().endswith((".wav",".mp3",".ogg",".flac",".m4a"))]
        print(f"  → {folder}: {len(files)} audio files")
        for fname in tqdm(files, desc=folder):
            try:
                aud_path = os.path.join(path, fname)
                y_aud, sr = librosa.load(aud_path, sr=22050, mono=True, duration=5.0)
                mel   = librosa.feature.melspectrogram(y=y_aud, sr=sr, n_mels=N_MELS)
                mel_db = librosa.power_to_db(mel, ref=np.max)
                mel_resized = cv2.resize(mel_db, (IMAGE_SIZE, IMAGE_SIZE))
                mel_norm = (mel_resized - mel_resized.min()) / (mel_resized.max() - mel_resized.min() + 1e-6)
                X.append(mel_norm[:, :, np.newaxis].astype(np.float32))
                y.append(label)
            except Exception as e:
                print(f"    ⚠️  Skipped {fname}: {e}")
    return np.array(X), np.array(y)


def train_audio_model(demo=False):
    print("\n" + "═"*50)
    print("  TRAINING AUDIO MODEL")
    print("═"*50)

    if demo:
        print("  [DEMO] Generating synthetic spectrograms...")
        N = 200
        X = np.random.rand(N, N_MELS, IMAGE_SIZE, 1).astype(np.float32)
        y = np.array([0]*100 + [1]*100)
        X[100:] += 0.12
        X = np.clip(X, 0, 1)
    else:
        X, y = load_audio_dataset(DATASET_ROOT)
        if len(X) == 0:
            print("  ❌ No audio data found. Skipping audio model.")
            return

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    print(f"  Train: {len(X_train)}  Val: {len(X_val)}")

    model = build_audio_model()
    model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS_AUD,
        batch_size=BATCH_SIZE,
        callbacks=make_callbacks("model_audio"),
        verbose=1,
    )
    model.save("model_audio.h5")
    print("  ✅ Saved → model_audio.h5")


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Scam Shield — Model Trainer")
    parser.add_argument("--demo",  action="store_true", help="Train on synthetic dummy data (no dataset needed)")
    parser.add_argument("--image", action="store_true", help="Train only image model")
    parser.add_argument("--video", action="store_true", help="Train only video model")
    parser.add_argument("--audio", action="store_true", help="Train only audio model")
    args = parser.parse_args()

    # If no specific model flag, train all three
    train_all = not (args.image or args.video or args.audio)

    if args.image or train_all:
        train_image_model(demo=args.demo)

    if args.video or train_all:
        train_video_model(demo=args.demo)

    if args.audio or train_all:
        train_audio_model(demo=args.demo)

    print("\n" + "═"*50)
    print("  🎉 ALL MODELS TRAINED SUCCESSFULLY")
    print("  Copy model_image.h5, model_video.h5, model_audio.h5")
    print("  into your project folder alongside backend.py & app.py.")
    print("  Restart the Streamlit app — backend.py will auto-load them.")
    print("═"*50)
