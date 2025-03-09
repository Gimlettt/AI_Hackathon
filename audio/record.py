from constant import stop_recording
import pyaudio
import wave

def record_voice(# Parameters for the recording
                FORMAT = pyaudio.paInt16,  # Audio format (16-bit PCM)
                CHANNELS = 1,  # Mono audio
                RATE = 44100,  # Sample rate (44.1kHz)
                CHUNK = 1024,  # Size of each chunk of data
                RECORD_SECONDS = 30,  # Maximum duration of the recording in seconds
                OUTPUT_FILENAME = "audio/recorded.wav"  # Output WAV file name and also a default parameter
                ):
  global stop_recording

  # Initialize the PyAudio object
  p = pyaudio.PyAudio()

  # Open a new audio stream
  stream = p.open(format=FORMAT,
                  channels=CHANNELS,
                  rate=RATE,
                  input=True,
                  frames_per_buffer=CHUNK)

  print("Recording...")

  frames = []
  
  # Record until either 1) space bar is pressed # Not currenntly used
  #                  or 2) maximum time specified in RECORD_SECONDS is reached
  i = 0
  while (not stop_recording and i < int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
    i+=1
    listening_time = i * CHUNK / RATE
    print(f"Listening... {listening_time:.2f} seconds", end="\r")

  # Stop and close the stream
  print("\nRecording finished.")
  stream.stop_stream()
  stream.close()
  p.terminate()

  # Save the recorded audio to a WAV file
  with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

  print(f"Audio saved to {OUTPUT_FILENAME}")
