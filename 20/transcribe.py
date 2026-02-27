from faster_whisper import WhisperModel
import os

def transcribe():
    model_size = "medium"
    # Run on CPU with INT8 quantization to save memory/speed
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    
    segments, info = model.transcribe("segment.mp3", beam_size=5)
    
    print(f"Detected language '{info.language}' with probability {info.language_probability}")
    
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

if __name__ == "__main__":
    transcribe()
