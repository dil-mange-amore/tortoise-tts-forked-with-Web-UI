"""
Voice Cloning Diagnostic Tool

Analyzes voice samples to identify potential quality issues.
"""

import os
import sys
import torch
import torchaudio
from pathlib import Path

def diagnose_voice(voice_name):
    """Comprehensive voice quality analysis"""
    
    voice_dir = Path("tortoise") / "voices" / voice_name
    
    if not voice_dir.exists():
        print(f"❌ Voice directory not found: {voice_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"Voice Cloning Diagnostic Report: {voice_name}")
    print(f"{'='*70}\n")
    
    # Check for .pth file
    pth_file = voice_dir / f"{voice_name}.pth"
    if pth_file.exists():
        print(f"✅ Conditioning latents file (.pth) exists: {pth_file.stat().st_size / 1024:.1f} KB")
    else:
        print(f"❌ No .pth file found - voice will load slowly")
    
    # Find audio files
    audio_files = sorted(list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3")))
    
    if not audio_files:
        print(f"❌ No audio files found in {voice_dir}")
        return
    
    print(f"\n📊 Found {len(audio_files)} audio file(s)\n")
    
    # Analyze each audio file
    total_duration = 0
    issues = []
    
    for i, audio_file in enumerate(audio_files, 1):
        try:
            audio, sr = torchaudio.load(audio_file)
            duration = audio.shape[1] / sr
            total_duration += duration
            
            # Calculate stats
            audio_np = audio.numpy()
            min_val = audio_np.min()
            max_val = audio_np.max()
            mean_val = audio_np.mean()
            std_val = audio_np.std()
            abs_max = abs(max(min_val, max_val, key=abs))
            
            # Check for issues
            has_positive = (audio_np > 0).any()
            has_negative = (audio_np < 0).any()
            is_clipping = abs_max > 0.99
            is_too_quiet = abs_max < 0.1
            has_dc_offset = abs(mean_val) > 0.01
            
            status = "✅"
            file_issues = []
            
            if not has_negative or not has_positive:
                status = "❌"
                file_issues.append("No negative values" if not has_negative else "No positive values")
            
            if is_clipping:
                status = "⚠️"
                file_issues.append("Possible clipping")
            
            if is_too_quiet:
                status = "⚠️"
                file_issues.append("Very quiet")
            
            if has_dc_offset:
                status = "⚠️"
                file_issues.append(f"DC offset: {mean_val:.4f}")
            
            print(f"{status} {i:2d}. {audio_file.name}")
            print(f"      Duration: {duration:.2f}s | SR: {sr}Hz")
            print(f"      Range: [{min_val:.4f}, {max_val:.4f}] | Mean: {mean_val:.4f} | Std: {std_val:.4f}")
            
            if file_issues:
                print(f"      Issues: {', '.join(file_issues)}")
                issues.extend(file_issues)
            
            print()
            
        except Exception as e:
            print(f"❌ {i:2d}. {audio_file.name}")
            print(f"      Error: {str(e)}\n")
            issues.append(f"Failed to load {audio_file.name}")
    
    # Summary
    print(f"{'='*70}")
    print(f"Summary")
    print(f"{'='*70}\n")
    
    print(f"Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
    print(f"Segment Count: {len(audio_files)}")
    
    # Quality assessment
    if len(audio_files) < 5:
        print(f"\n❌ CRITICAL: Less than 5 segments - quality will be VERY POOR")
        print(f"   Recommendation: Provide at least 70 seconds (7 segments)")
    elif len(audio_files) < 7:
        print(f"\n⚠️  WARNING: Less than 7 segments - quality may be suboptimal")
        print(f"   Recommendation: Provide 70-100 seconds (7-10 segments)")
    elif len(audio_files) < 10:
        print(f"\n✅ GOOD: {len(audio_files)} segments - acceptable for cloning")
        print(f"   For best results: 100+ seconds (10+ segments)")
    else:
        print(f"\n✅ EXCELLENT: {len(audio_files)} segments - great for cloning!")
    
    if total_duration < 50:
        print(f"\n❌ CRITICAL: Total duration {total_duration:.1f}s is too short")
        print(f"   Minimum: 50 seconds | Recommended: 70-100 seconds")
    elif total_duration < 70:
        print(f"\n⚠️  WARNING: Total duration {total_duration:.1f}s is below recommended")
        print(f"   Recommended: 70-100 seconds for better quality")
    else:
        print(f"\n✅ Duration is good: {total_duration:.1f}s")
    
    # Issues found
    if issues:
        print(f"\n⚠️  Issues Detected:")
        unique_issues = set(issues)
        for issue in unique_issues:
            count = issues.count(issue)
            print(f"   - {issue} ({count} file(s))")
        
        print(f"\n💡 Recommendations:")
        if any("No negative" in i or "No positive" in i for i in issues):
            print(f"   - Audio not properly centered around zero")
            print(f"   - This WILL cause poor voice matching!")
            print(f"   - Re-process audio with DC offset removal")
        
        if any("clipping" in i.lower() for i in issues):
            print(f"   - Reduce recording volume to avoid clipping")
        
        if any("quiet" in i.lower() for i in issues):
            print(f"   - Increase recording volume or normalize audio")
        
        if any("DC offset" in i for i in issues):
            print(f"   - Remove DC offset from recordings")
    else:
        print(f"\n✅ No issues detected - audio looks good!")
    
    # Regenerate .pth recommendation
    if pth_file.exists() and issues:
        print(f"\n🔄 IMPORTANT: Issues found in audio files")
        print(f"   Delete {pth_file.name} and re-upload voice to fix issues")
        print(f"   Command: del \"tortoise\\voices\\{voice_name}\\{voice_name}.pth\"")
    
    print(f"\n{'='*70}\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python diagnose_voice.py <voice_name>")
        print("\nAvailable voices:")
        voices_dir = Path("tortoise") / "voices"
        if voices_dir.exists():
            for voice_dir in sorted(voices_dir.iterdir()):
                if voice_dir.is_dir() and not voice_dir.name.startswith('.'):
                    audio_count = len(list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3")))
                    has_pth = (voice_dir / f"{voice_dir.name}.pth").exists()
                    status = "✅" if has_pth else "📁"
                    print(f"  {status} {voice_dir.name} ({audio_count} audio files)")
        sys.exit(1)
    
    voice_name = sys.argv[1]
    diagnose_voice(voice_name)

if __name__ == "__main__":
    main()
