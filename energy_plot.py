import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

# Path to your audio file
audio_file = 'speech_test_0.mp3'

# Load the audio file
y, sr = librosa.load(audio_file)

# Calculate the energy of the audio
energy = librosa.feature.rms(y=y)[0]
energy_smoothed = np.convolve(energy, np.ones(50)/50, mode='same')

# Create a time array
times = librosa.times_like(energy, sr=sr)

print(len(y), len(energy), len(times))
print(times)

# Plot the energy with respect to time
plt.figure(figsize=(12, 6))
#librosa.display.waveshow(y, sr=sr, alpha=0.5)
plt.plot(times, energy, color='r')
plt.plot(times, energy_smoothed, color='b')
plt.xlabel('Time (s)')
plt.ylabel('Energy')
plt.title('Energy of Audio File')
plt.show()
