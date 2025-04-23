import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt

# Load the audio file
sample_rate, audio = wavfile.read('resources/audio/test.wav')

# stereo to mono
if len(audio.shape) == 2:
    print("Stereo audio detected, converting to mono.")
    audio = audio.mean(axis=1)

print(audio)

# Normalize the audio to range [-1, 1]
audio = audio / np.max(np.abs(audio))

print(audio)

def frame_signal(signal, frame_size, hop_size):
    # print(len(signal), frame_size, hop_size)
    num_frames = 1 + int((len(signal) - frame_size) / hop_size)
    frames = np.zeros((num_frames, frame_size))

    for i in range(num_frames):
        start = i * hop_size
        frames[i] = signal[start:start + frame_size]

    return frames

# Define frame parameters
frame_size = 1024  # Number of samples per frame
hop_size = 512     # Number of samples to step

# Frame the signal
frames = frame_signal(audio, frame_size, hop_size)
print(frames.shape)

# Apply Hann window to each frame
hann_window = np.hanning(frame_size)
windowed_frames = frames * hann_window

# Number of frequency bins in the one-sided spectrum
num_bins = windowed_frames.shape[1] // 2 + 1

# Pre-allocate array: rows = frames, cols = frequency bins
magnitude_spectra = np.zeros((windowed_frames.shape[0], num_bins))

for i, frame in enumerate(windowed_frames):
    # Compute real FFT (one-sided)
    spectrum = np.fft.rfft(frame)
    # Take magnitudes
    magnitude_spectra[i, :] = np.abs(spectrum)

# Pre-allocate spectral flux vector
spectral_flux = np.zeros(magnitude_spectra.shape[0])

# For all frames after the first
for n in range(1, magnitude_spectra.shape[0]):
    # Difference between current and previous magnitude spectrum
    diff = magnitude_spectra[n] - magnitude_spectra[n - 1]
    # Keep only positive values (onset energy increases)
    positive_diff = np.maximum(diff, 0)
    # Sum across all frequency bins
    spectral_flux[n] = np.sum(positive_diff)

# Avoid division by zero
if np.max(spectral_flux) > 0:
    spectral_flux /= np.max(spectral_flux)

#Visualize
frame_index = 100  # You can choose any frame index
frame = windowed_frames[frame_index]

# Compute the FFT
spectrum = np.fft.rfft(frame)
magnitude = np.abs(spectrum)

# Generate frequency axis
freqs = np.fft.rfftfreq(len(frame), d=1/sample_rate)

# Plot the magnitude spectrum
# plt.figure(figsize=(10, 4))
# plt.plot(freqs, magnitude)
# plt.title(f'Magnitude Spectrum - Frame {frame_index}')  
# plt.xlabel('Frequency (Hz)')
# plt.ylabel('Magnitude')
# plt.grid(True)
# plt.tight_layout()
# plt.show()

from scipy.ndimage import median_filter

smoothed_flux = median_filter(spectral_flux, size=7)

window = 21
threshold = np.convolve(smoothed_flux, np.ones(window)/window, mode='same') * 1.5

# Visualize the smoothed novelty and threshold to check the curves
plt.figure(figsize=(12, 6))
plt.plot(smoothed_flux, label='Smoothed Novelty')
plt.plot(threshold, label='Threshold', linestyle='--')
plt.legend()
plt.title('Novelty Curve and Threshold')
plt.xlabel('Frame Index')
plt.ylabel('Normalized Flux')
plt.show()


peaks = []
for n in range(1, len(smoothed_flux)-1):
    if smoothed_flux[n] > threshold[n] and smoothed_flux[n] > smoothed_flux[n-1] and smoothed_flux[n] > smoothed_flux[n+1]:
        peaks.append(n)

print(f"Number of peaks detected: {len(peaks)}")

iois = np.diff(peaks)                             # frame-differences
busiest_bin = np.bincount(iois).argmax()          # most common interval
bpm = 60 * sample_rate / (hop_size * busiest_bin)  # convert to beats-per-minute
print(f"Estimated tempo: {bpm:.1f} BPM")


# Prune your peak list to lie on that steady grid
expected = busiest_bin
beat_frames = [peaks[0]]
for p in peaks[1:]:
    if abs(p - beat_frames[-1] - expected) < expected * 0.2:
        beat_frames.append(p)

beat_times = [peak * hop_size / sample_rate for peak in peaks]
print(f"Detected beat times: {beat_times[:10]}")