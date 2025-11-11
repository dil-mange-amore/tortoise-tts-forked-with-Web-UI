"""
Quick voice diagnostic using basic tools
"""
import os
import wave
import struct
from pathlib import Path

def analyze_wav(filepath):
    """Analyze a WAV file"""
    try:
        with wave.open(str(filepath), 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            duration = n_frames / framerate
            
            # Read all frames
            frames = wf.readframes(n_frames)
            
            # Convert to values
            if sample_width == 2:  # 16-bit
                fmt = f'{n_frames * channels}h'
                samples = struct.unpack(fmt, frames)
                # Normalize to [-1, 1]
                samples = [s / 32768.0 for s in samples]
            elif sample_width == 4:  # 32-bit
                fmt = f'{n_frames * channels}i'
                samples = struct.unpack(fmt, frames)
                samples = [s / 2147483648.0 for s in samples]
            else:
                return None, "Unsupported sample width"
            
            # Calculate stats
            min_val = min(samples)
            max_val = max(samples)
            mean_val = sum(samples) / len(samples)
            
            has_positive = any(s > 0 for s in samples)
            has_negative = any(s < 0 for s in samples)
            
            return {
                'duration': duration,
                'sample_rate': framerate,
                'channels': channels,
                'min': min_val,
                'max': max_val,
                'mean': mean_val,
                'has_positive': has_positive,
                'has_negative': has_negative,
                'abs_max': max(abs(min_val), abs(max_val))
            }, None
    except Exception as e:
        return None, str(e)

def main():
    voice_name = "Amol"
    voice_dir = Path("tortoise") / "voices" / voice_name
    
    print(f"\n{'='*70}")
    print(f"Voice Diagnostic: {voice_name}")
    print(f"{'='*70}\n")
    
    if not voice_dir.exists():
        print(f"❌ Voice directory not found: {voice_dir}")
        return
    
    # Check .pth
    pth_file = voice_dir / f"{voice_name}.pth"
    print(f"Conditioning latents (.pth): {'✅ EXISTS' if pth_file.exists() else '❌ MISSING'}")
    
    # Find audio files
    audio_files = sorted(list(voice_dir.glob("*.wav")))
    print(f"Audio files: {len(audio_files)}\n")
    
    if not audio_files:
        print("❌ No audio files found")
        return
    
    total_duration = 0
    issues = []
    
    for i, audio_file in enumerate(audio_files[:5], 1):  # Show first 5
        stats, error = analyze_wav(audio_file)
        
        if error:
            print(f"❌ {audio_file.name}: {error}")
            continue
        
        total_duration += stats['duration']
        
        status = "✅"
        file_issues = []
        
        if not stats['has_negative'] or not stats['has_positive']:
            status = "❌"
            file_issues.append("NOT CENTERED (missing negative/positive values)")
            issues.append("not_centered")
        
        if abs(stats['mean']) > 0.01:
            status = "⚠️"
            file_issues.append(f"DC offset: {stats['mean']:.4f}")
            issues.append("dc_offset")
        
        if stats['abs_max'] > 0.99:
            status = "⚠️"
            file_issues.append("Clipping")
            issues.append("clipping")
        
        if stats['abs_max'] < 0.1:
            status = "⚠️"
            file_issues.append("Too quiet")
            issues.append("too_quiet")
        
        print(f"{status} {audio_file.name}")
        print(f"    {stats['duration']:.1f}s | {stats['sample_rate']}Hz")
        print(f"    Range: [{stats['min']:.4f}, {stats['max']:.4f}] | Mean: {stats['mean']:.4f}")
        
        if file_issues:
            for issue in file_issues:
                print(f"    ⚠️  {issue}")
        print()
    
    if len(audio_files) > 5:
        print(f"... and {len(audio_files) - 5} more files\n")
    
    # Summary
    print(f"{'='*70}")
    print(f"Summary")
    print(f"{'='*70}\n")
    
    print(f"Total files: {len(audio_files)}")
    print(f"Total duration: ~{total_duration * len(audio_files) / 5 if len(audio_files) > 5 else total_duration:.1f}s\n")
    
    if "not_centered" in issues:
        print("❌ CRITICAL ISSUE: Audio not centered around zero!")
        print("   This is WHY your voice cloning isn't working!")
        print("   The old audio has DC offset or isn't properly normalized.\n")
    
    if issues:
        print("🔧 SOLUTION:")
        print("   1. Delete the .pth file:")
        print(f"      del tortoise\\voices\\{voice_name}\\{voice_name}.pth")
        print("   2. Restart web server")
        print("   3. Re-record or re-upload your voice")
        print("   4. New code will fix DC offset automatically")
        print()
    else:
        print("✅ Audio looks good!\n")
    
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
