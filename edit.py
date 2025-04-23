import json
import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

BEATS_JSON = 'beat_cache.json'        # JSON file with structure: {"beat_times": [t1, t2, ...]}
AUDIO_FILE = 'C:/Users/Hrithik/OneDrive/Documents/AI/beatfinder/resources/audio/test.wav'
IMAGES_DIR = 'resources/images/'                # Directory containing your 20 images
OUTPUT_VIDEO = 'slideshow.mp4'

# 1. Load beat times from JSON
def load_beat_times(json_path, start_sec=25.0, end_sec=30.0):
    with open(json_path, 'r') as f:
        data = json.load(f)
    raw_beats = data.get('test.mp3', [])
    # Keep only beats between start and end
    filtered = [t for t in raw_beats if start_sec <= t < end_sec]
    # Offset to video timeline (0 = start_sec)
    return [t - start_sec for t in filtered]

# 2. Compute clip durations between successive beats
def compute_durations(beat_offsets, total_duration=5.0):
    durations = []
    previous = 0.0
    for b in beat_offsets:
        durations.append(b - previous)
        previous = b
    # Last segment until end
    durations.append(total_duration - previous)
    return durations

# 3. Load and prepare image clips in vertical format
def make_image_clips(image_dir, durations, target_size=(720, 1280)):
    # Sort image filenames for deterministic order
    files = sorted(os.listdir(image_dir))
    if len(files) < len(durations):
        raise ValueError(f"Not enough images ({len(files)}) for beats ({len(durations)} segments)")
    clips = []
    for img_file, dur in zip(files, durations):
        path = os.path.join(image_dir, img_file)
        clip = ImageClip(path)
        # Center-crop to exact aspect ratio if needed
        clip = clip.resized((target_size[0], target_size[1]))
        clips.append(clip.with_duration(dur))
    return clips

# 4. Assemble the slideshow and attach audio
if __name__ == '__main__':
    START_SEC = 15.0
    END_SEC = 30.0
    TOTAL_DUR = END_SEC - START_SEC

    # Load and process beat offsets
    beat_offsets = load_beat_times(BEATS_JSON, START_SEC, END_SEC)
    durations = compute_durations(beat_offsets, TOTAL_DUR)

    # Create image clips
    clips = make_image_clips(IMAGES_DIR, durations)

    # Concatenate clips into a vertical slideshow
    slideshow = concatenate_videoclips(clips, method='compose')

    # Load and trim audio, then set it on the video
    audio = AudioFileClip(str(AUDIO_FILE)).subclipped(START_SEC, END_SEC)
    final = slideshow.with_audio(audio)

    # Export
    final.write_videofile(OUTPUT_VIDEO, fps=24)
