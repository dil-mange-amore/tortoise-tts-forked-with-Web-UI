"""
Test audio normalization by saving and reloading
"""
import torch
import torchaudio

# Create test audio
print("Creating test audio...")
audio = torch.randn(1, 22050)  # 1 second of random audio
print(f"Before normalization: min={audio.min():.4f}, max={audio.max():.4f}")

# Normalize to [-1, 1]
audio = audio - audio.mean()  # Remove DC offset
max_val = torch.max(torch.abs(audio))
audio = audio / max_val
print(f"After normalization: min={audio.min():.4f}, max={audio.max():.4f}")

# Save
print("\nSaving as test.wav...")
torchaudio.save("test.wav", audio, 22050)

# Reload
print("Reloading test.wav...")
loaded, sr = torchaudio.load("test.wav")
print(f"After reload: min={loaded.min():.4f}, max={loaded.max():.4f}")
print(f"Sample rate: {sr}")
print(f"Shape: {loaded.shape}")
print(f"Dtype: {loaded.dtype}")

# Check if values changed
if torch.allclose(audio, loaded, atol=1e-4):
    print("\n✅ Values preserved correctly!")
else:
    print("\n⚠️ Values changed after save/load!")
    print(f"Difference: {torch.max(torch.abs(audio - loaded)):.6f}")
