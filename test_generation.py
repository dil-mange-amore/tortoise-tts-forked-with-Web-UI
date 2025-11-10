"""
Quick test script to verify Tortoise TTS is working
"""
import torch
import torchaudio
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_voices

print("=" * 60)
print("TORTOISE TTS - QUICK TEST")
print("=" * 60)

# Check CUDA
print(f"\n1. CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   CUDA Version: {torch.version.cuda}")

# Initialize TTS with very small batch size
print("\n2. Loading TTS models...")
print("   Using batch_size=2 for maximum safety")
tts = TextToSpeech(autoregressive_batch_size=2)
print("   ✓ Models loaded!")

# Test with ultra_fast preset and minimal text
test_text = "Hello world."
test_voice = "angie"

print(f"\n3. Testing generation:")
print(f"   Text: '{test_text}'")
print(f"   Voice: {test_voice}")
print(f"   Preset: ultra_fast (fastest possible)")
print(f"   Candidates: 1")

print("\n4. Loading voice samples...")
voice_samples, conditioning_latents = load_voices([test_voice])
print("   ✓ Voice samples loaded!")

print("\n5. Starting generation...")
print("   This should take 10-30 seconds with ultra_fast preset")
print("   If it hangs here, there's a problem with your setup\n")

try:
    gen = tts.tts_with_preset(
        test_text,
        voice_samples=voice_samples,
        conditioning_latents=conditioning_latents,
        preset='ultra_fast',
        k=1,
        verbose=True  # Show progress
    )
    
    print("\n   ✓ Generation successful!")
    print(f"   Output shape: {gen.shape}")
    
    # Save test output - handle tensor dimensions correctly
    output_file = "test_output.wav"
    
    # Shape is (1, 1, samples) - need (channels, samples) which is (1, samples)
    if len(gen.shape) == 3:
        gen = gen[0]  # Now (1, samples)
    
    # Don't squeeze further - torchaudio.save needs (channels, samples)
    print(f"   Final shape for saving: {gen.shape}")
    torchaudio.save(output_file, gen.cpu(), 24000)
    print(f"   ✓ Saved to: {output_file}")
    
    print("\n" + "=" * 60)
    print("SUCCESS! Tortoise TTS is working correctly.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n   ✗ Generation FAILED!")
    print(f"   Error: {str(e)}")
    print("\n" + "=" * 60)
    print("FAILED - See error above")
    print("=" * 60)
    import traceback
    traceback.print_exc()
