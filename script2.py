from moviepy.editor import *
import numpy as np
import librosa

def detect_speech_intervals(audio_path, threshold=0.02, min_silence_len=0.3):
    """Detects speech intervals based on energy levels."""
    y, sr = librosa.load(audio_path, sr=None)  # Load the audio file, keeping its original sampling rate
    

    # Fixed frame_length and hop_length for initial analysis
    #frame_length = 4410
    #hop_length = 2205

    energies = librosa.feature.rms(y=y)[0]  # Calculate the RMS energy for each frame
    window_length = 150
    energies_smoothed = np.convolve(energies, np.ones(window_length)/window_length, mode='same')
    times = librosa.times_like(energies, sr=sr)
    # Frame the energy signal
    #frames = librosa.util.frame(energy, frame_length=frame_length, hop_length=hop_length).T

    intervals = []
    start = None

    for energy, time in zip(energies_smoothed, times):
        if energy > threshold:  # Check if the average energy of the frame exceeds the threshold
            if start is None:
                start = time  # Mark the start of a speech interval
        else:
            if start is not None:
                end = time # Mark the end of a speech interval
                intervals.append((start, end))  # Store the interval
                start = None

    if start is not None:
        intervals.append((start, times[-1]))  # Handle the case where the audio ends while still in a speech interval

    return intervals



# Load the video files
clip1 = VideoFileClip("sample1.mp4").subclip(0, 100)  # Footage from the primary camera
clip2 = VideoFileClip("sample2.mp4").subclip(0, 100)  # Footage from the secondary camera

clip1_duration = clip1.duration  # Duration in seconds
clip2_duration = clip2.duration  # Ideally equal to the first one

# Load the audio files
audio1 = AudioFileClip("interstellar_bg.mp3").subclip(0, clip1_duration)  # First audio source
audio2 = AudioFileClip("speech_test_0.mp3").subclip(0, clip1_duration)  # Second audio source
audio3 = AudioFileClip("speech_test_1.mp3").subclip(0, clip1_duration)  # Second audio source
audio4 = AudioFileClip("speech_test_2.mp3").subclip(0, clip1_duration)  # Second audio source

# Detect speech intervals in audio2
speech_intervals = detect_speech_intervals(audio2.filename)

# Parameters for the edit
secondary_clip_fraction = 0.2  # fraction of the scene will be from the secondary camera
secondary_clip_frequency = 1  #  per minute
randomness_interval = 0.2  # Determines randomness in placement of secondary clips
randomness_duration = 0.2  # Determines randomness in length of secondary clip durations

number_of_mid_clips = int(clip1_duration / 60 * secondary_clip_frequency)
total_clip2_footage_duration = clip1_duration * secondary_clip_fraction
average_mid_clip_durations = total_clip2_footage_duration / number_of_mid_clips
std_dev_mid_clip_durations = average_mid_clip_durations * randomness_duration

# Generate random mid-clip durations and insertion times
mid_clip_durations = np.random.normal(average_mid_clip_durations, std_dev_mid_clip_durations, number_of_mid_clips)
mid_clip_durations = np.clip(mid_clip_durations, 1, clip2_duration)  # Ensure durations are positive and within bounds

mid_clip_insertion_times = np.linspace(0, clip1_duration, number_of_mid_clips)
mid_clip_insertion_times += np.random.uniform(-average_mid_clip_durations * randomness_interval,
                                              average_mid_clip_durations * randomness_interval,
                                              number_of_mid_clips)
mid_clip_insertion_times = np.clip(mid_clip_insertion_times, 0, clip1_duration)  # Ensure insertion times are within bounds

# Insert speech intervals into mid_clip_insertion_times and mid_clip_durations
for start, end in speech_intervals:
    mid_clip_insertion_times = np.append(mid_clip_insertion_times, start)
    mid_clip_durations = np.append(mid_clip_durations, end - start)

# Sort the times and durations by insertion times
sorted_indices = np.argsort(mid_clip_insertion_times)
mid_clip_insertion_times = mid_clip_insertion_times[sorted_indices]
mid_clip_durations = mid_clip_durations[sorted_indices]

snippets = []

# Create subclips from clip2
for duration, start_time in zip(mid_clip_durations[1:], mid_clip_insertion_times[1:]):
    if start_time + duration <= clip2_duration:
        snippet = clip2.subclip(start_time, start_time + duration).set_start(start_time)
        snippets.append(snippet)

# Combine the primary clip with the snippets from the secondary clip
final_clip = CompositeVideoClip([clip1] + snippets)

# Combine the audio clips
combined_audio = CompositeAudioClip([audio1, audio2, audio3, audio4])

# Set the combined audio as the audio for the final video
final_clip = final_clip.set_audio(combined_audio)

# Write the final video file
final_clip.write_videofile("output.mp4", codec="libx264")

# Close the video clips
clip1.close()
clip2.close()

# Close the audio clips
audio1.close()
audio2.close()
