from moviepy.editor import *
import numpy as np

"""
This script will generate a video from two video and multiple audio sources.
This program is being written for a scene/stage with two cameras, one primary and the other being secondary.
"""

clip1 = VideoFileClip("sample1.mp4") #Footage from the primary camera
clip2 = VideoFileClip("sample2.mp4") #Footage from the secondary camera

clip1_duration = clip1.duration #Duration in seconds
clip2_duration = clip2.duration #Ideally equal to the first one

#Let us define some parameters for our edit:
secondary_clip_fraction = 0.2 # 0.2 means that 20% of the scene will be from the secondary camera
secondary_clip_frequency = 0.5 # The unit is per minute, so 0.5 means that the scene will put on the secondary camera once every two minutes (or 0.5 per minute)
randomness_interval = 0.5 # Range: [0-1). This will determine if the secondary shots are placed at random or placed uniformly across the clip. 0 means no randomness at all and 1 means totally random.
randomness_duration = 0.4 # Range: [0,1). This will determine the randomness in the length of the secondary clip durations, if it is 0 then all the secondary clips will have the same length, if it is larger then they will have quite a spread, one could be only for 1s and the next one for 60s; so keep it small

number_of_mid_clips = int(clip2_duration/60*secondary_clip_frequency) #Divided by 60 to get minutes and multiplied by frequency to get the number of occurences
total_clip2_footage_duration = clip2_duration*secondary_clip_fraction
average_mid_clip_durations = total_clip2_footage_duration/number_of_mid_clips
std_dev_mid_clip_durations = average_mid_clip_durations * randomness_duration

mid_clip_durations = np.random.normal(average_mid_clip_durations,std_dev_mid_clip_durations,number_of_mid_clips).astype(int) #Generates an array with lengths of mid-clip durations
mid_clip_insertion_times = np.arange(0,clip2_duration,clip2_duration/number_of_mid_clips)
mid_clip_insertion_times += np.random.normal(0,average_mid_clip_durations*randomness_interval,number_of_mid_clips).astype(int)

snippets = []

for duration, start_time in zip(mid_clip_durations[1:], mid_clip_insertion_times[1:]):
    snippet = clip2.subclip(0,duration).set_start(start_time)
    snippets.append(snippet)

final_clip = CompositeVideoClip([clip1]+snippets)

final_clip.write_videofile("output.mp4", codec="libx264")

clip1.close()
clip2.close()