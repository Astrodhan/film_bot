from moviepy.editor import *
import numpy as np

# Load the video files
clip1 = VideoFileClip("sample1.mp4").subclip(0,150)  # Footage from the primary camera
clip2 = VideoFileClip("sample2.mp4").subclip(0,150)  # Footage from the secondary camera

clip1_duration = clip1.duration  # Duration in seconds
clip2_duration = clip2.duration  # Ideally equal to the first one

# Parameters for the edit
secondary_clip_fraction = 0.2  # 20% of the scene will be from the secondary camera
secondary_clip_frequency = 3  # 0.5 per minute means once every two minutes
randomness_interval = 0.5  # Determines randomness in placement of secondary clips
randomness_duration = 0.4  # Determines randomness in length of secondary clip durations

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

snippets = []

# Create subclips from clip2
for duration, start_time in zip(mid_clip_durations[1:], mid_clip_insertion_times[1:]):
    if start_time + duration <= clip2_duration:
        snippet = clip2.subclip(start_time, start_time + duration).set_start(start_time)
        snippets.append(snippet)

# Combine the primary clip with the snippets from the secondary clip
final_clip = CompositeVideoClip([clip1] + snippets)

# Write the final video file
final_clip.write_videofile("output.mp4", codec="libx264")

# Close the video clips
clip1.close()
clip2.close()
