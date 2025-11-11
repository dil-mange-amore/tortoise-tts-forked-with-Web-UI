"""
Voice Cloning Audio Normalization Test

This script tests that audio files are properly normalized to [-1, 1] range
after processing through the voice cloning pipeline.

Usage:
    python test_audio_normalization.py <voice_name>

Example:
    python test_audio_normalization.py my_voice
"""

import torch
import torchaudio
import sys
import os
from pathlib import Path

def test_audio_normalization(voice_name):
    """Test that all audio files for a voice are normalized to [-1, 1]"""
    
    voice_dir = Path("tortoise") / "voices" / voice_name
    
    if not voice_dir.exists():
        print(f"❌ Voice directory not found: {voice_dir}")
        return False
    
    audio_files = list(voice_dir.glob("*.wav"))
    
    if not audio_files:
        print(f"❌ No WAV files found in {voice_dir}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Testing Audio Normalization for Voice: {voice_name}")
    print(f"{'='*60}\n")
    print(f"Found {len(audio_files)} audio files\n")
    
    all_passed = True
    
    for audio_file in sorted(audio_files):
        try:
            # Load audio
            audio, sr = torchaudio.load(audio_file)
            
            # Get min and max values
            min_val = torch.min(audio).item()
            max_val = torch.max(audio).item()
            abs_max = torch.max(torch.abs(audio)).item()
            
            # Check if normalized
            is_normalized = (abs_max <= 1.0) and (min_val >= -1.0) and (max_val <= 1.0)
            
            # Check for issues
            has_nan = torch.any(torch.isnan(audio)).item()
            has_inf = torch.any(torch.isinf(audio)).item()
            is_silent = abs_max < 0.001
            
            # Print results
            status = "✅" if is_normalized and not has_nan and not has_inf and not is_silent else "❌"
            print(f"{status} {audio_file.name}")
            print(f"   Range: [{min_val:.6f}, {max_val:.6f}]")
            print(f"   Max Abs: {abs_max:.6f}")
            
            if not is_normalized:
                print(f"   ⚠️  WARNING: Audio not in [-1, 1] range!")
                all_passed = False
            
            if has_nan:
                print(f"   ⚠️  ERROR: Audio contains NaN values!")
                all_passed = False
            
            if has_inf:
                print(f"   ⚠️  ERROR: Audio contains Infinity values!")
                all_passed = False
            
            if is_silent:
                print(f"   ⚠️  WARNING: Audio is silent or near-silent!")
                all_passed = False
            
            print()
            
        except Exception as e:
            print(f"❌ {audio_file.name}")
            print(f"   ERROR: {str(e)}\n")
            all_passed = False
    
    print(f"{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED - Audio properly normalized!")
    else:
        print("❌ TESTS FAILED - Some audio files have issues")
    print(f"{'='*60}\n")
    
    return all_passed

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_audio_normalization.py <voice_name>")
        print("\nExample: python test_audio_normalization.py my_voice")
        print("\nAvailable voices:")
        voices_dir = Path("tortoise") / "voices"
        if voices_dir.exists():
            for voice_dir in sorted(voices_dir.iterdir()):
                if voice_dir.is_dir() and not voice_dir.name.startswith('.'):
                    audio_count = len(list(voice_dir.glob("*.wav")))
                    has_pth = (voice_dir / f"{voice_dir.name}.pth").exists()
                    status = "✅" if has_pth else "📁"
                    print(f"  {status} {voice_dir.name} ({audio_count} WAV files)")
        sys.exit(1)
    
    voice_name = sys.argv[1]
    success = test_audio_normalization(voice_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
