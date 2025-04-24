import os
import json
import time
import numpy as np
import soundfile as sf
import sounddevice as sd
import librosa

CACHE_PATH = "beat_cache.json"

def get_beat_times(audio_path):
    # Load or init cache
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as cf:
            cache = json.load(cf)
    else:
        cache = {}

    fname = os.path.basename(audio_path)
    if fname in cache:
        print(f"✔️ Loaded '{fname}' from cache")
        return cache[fname]

    # 1. Read audio into NumPy array + sample rate
    y, sr = librosa.load(audio_path, dtype='float32')

    # 2a. Compute low-band Mel spectrogram (fmax=2000 Hz)
    S = librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=64,
        hop_length=512,
        fmin=20,
        fmax=300
    )  # limits spectral flux to low frequencies :contentReference[oaicite:1]{index=1}

    # 2b. Convert power to dB and compute onset envelope
    S_db = librosa.power_to_db(S, ref=np.max)  # dB scaling for stability :contentReference[oaicite:2]{index=2}
    onset_env = librosa.onset.onset_strength(
        S=S_db,
        sr=sr,
        hop_length=512,
        aggregate=np.mean
    )  # uses our band-limited S instead of full-band default :contentReference[oaicite:3]{index=3}

    # 3. Beat tracking on custom onset envelope
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env,
        sr=sr,
        hop_length=512,
        start_bpm=120.0,
        tightness=100,
        units='frames'
    )  # dynamic-programming tracker on low-freq onsets :contentReference[oaicite:4]{index=4}

    # 4. Frames → seconds
    beat_times = librosa.frames_to_time(
        beat_frames,
        sr=sr,
        hop_length=512
    ).tolist()

    # 5. Cache & return
    cache[fname] = beat_times
    with open(CACHE_PATH, "w") as cf:
        json.dump(cache, cf, indent=2)

    print(f"⏳ Computed and cached beats for '{fname}'")
    return beat_times

def play_and_print_beats(audio_path):
    beat_times = get_beat_times(audio_path)

    # Load track for playback
    data, sr = sf.read(audio_path, dtype='float32')

    # Play asynchronously
    sd.play(data, sr)
    start_time = time.time()

    # Print beat prints in real time
    for t in beat_times:
        wait = t - (time.time() - start_time)
        if wait > 0:
            time.sleep(wait)
        print(f"▶  Beat at {t:.3f} s")

    # Wait for end of playback
    sd.wait()

if __name__ == "__main__":
    play_and_print_beats("resources/audio/test2.wav")
