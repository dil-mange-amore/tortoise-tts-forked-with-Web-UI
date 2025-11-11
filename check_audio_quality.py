"""
Check audio file quality for voice cloning
"""
import torch
import torchaudio
import os
import sys

def check_audio(filepath):
    """Check audio file properties"""
    print(f"\n{'='*60}")
    print(f"File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        # Load audio
        audio, sr = torchaudio.load(filepath)
        
        print(f"Sample rate: {sr} Hz")
        print(f"Shape: {audio.shape} (channels={audio.shape[0]}, samples={audio.shape[1]})")
        print(f"Duration: {audio.shape[1]/sr:.2f} seconds")
        print(f"Data type: {audio.dtype}")
        
        # Stats
        print(f"\nAudio Statistics:")
        print(f"  Min: {audio.min():.6f}")
        print(f"  Max: {audio.max():.6f}")
        print(f"  Mean: {audio.mean():.6f}")
        print(f"  Std: {audio.std():.6f}")
        
        # Check for issues
        print(f"\nQuality Checks:")
        
        # DC offset
        dc_offset = abs(audio.mean().item())
        if dc_offset > 0.01:
            print(f"  ⚠️ DC offset: {dc_offset:.6f} (should be near 0)")
        else:
            print(f"  ✅ DC offset: {dc_offset:.6f}")
        
        # Normalization
        max_abs = torch.max(torch.abs(audio)).item()
        if max_abs < 0.5:
            print(f"  ⚠️ Low amplitude: {max_abs:.6f} (should be near 1.0)")
        elif max_abs > 0.99:
            print(f"  ✅ Well normalized: {max_abs:.6f}")
        else:
            print(f"  ⚠️ Not fully normalized: {max_abs:.6f} (should be near 1.0)")
        
        # Clipping
        clipped = torch.sum((torch.abs(audio) >= 0.99)).item()
        if clipped > 0:
            print(f"  ⚠️ Clipped samples: {clipped} ({clipped/audio.numel()*100:.2f}%)")
        else:
            print(f"  ✅ No clipping")
        
        # Silence
        silent_threshold = 0.01
        silent_samples = torch.sum(torch.abs(audio) < silent_threshold).item()
        silence_pct = silent_samples / audio.numel() * 100
        if silence_pct > 50:
            print(f"  ⚠️ Silence: {silence_pct:.1f}% (too much silence)")
        else:
            print(f"  ✅ Silence: {silence_pct:.1f}%")
        
        # Sign balance
        positive = torch.sum(audio > 0).item()
        negative = torch.sum(audio < 0).item()
        balance = min(positive, negative) / max(positive, negative) * 100
        if balance < 80:
            print(f"  ⚠️ Unbalanced waveform: {balance:.1f}% (should be ~100%)")
        else:
            print(f"  ✅ Balanced waveform: {balance:.1f}%")
        
        # NaN/Inf
        if torch.any(torch.isnan(audio)) or torch.any(torch.isinf(audio)):
            print(f"  ❌ Contains NaN or Inf values!")
        else:
            print(f"  ✅ No NaN/Inf values")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_audio_quality.py <voice_name>")
        print("Example: python check_audio_quality.py simp")
        sys.exit(1)
    
    voice_name = sys.argv[1]
    voice_dir = f"tortoise/voices/{voice_name}"
    
    if not os.path.exists(voice_dir):
        print(f"Error: Voice directory not found: {voice_dir}")
        sys.exit(1)
    
    print(f"\nChecking audio quality for voice: {voice_name}")
    print(f"Directory: {voice_dir}")
    
    # Find all audio files
    audio_files = []
    for file in os.listdir(voice_dir):
        if file.endswith(('.wav', '.mp3', '.flac')):
            audio_files.append(os.path.join(voice_dir, file))
    
    if not audio_files:
        print("No audio files found!")
        sys.exit(1)
    
    print(f"Found {len(audio_files)} audio files")
    
    # Check each file
    all_ok = True
    for filepath in sorted(audio_files):
        if not check_audio(filepath):
            all_ok = False
    
    print(f"\n{'='*60}")
    if all_ok:
        print("✅ All files checked successfully!")
    else:
        print("⚠️ Some files had errors")
    print(f"{'='*60}\n")
