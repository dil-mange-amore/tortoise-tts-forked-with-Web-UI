"""
Test if .pth file quality differs from raw audio loading

This script will help diagnose if your .pth files have corrupted conditioning latents.
"""

import sys
import os

print("=" * 70)
print("Voice Cloning Quality Test")
print("=" * 70)
print()
print("THEORY: Your .pth files contain BAD conditioning latents because they")
print("were generated from audio that wasn't properly normalized.")
print()
print("SOLUTION: Delete ALL .pth files and let them regenerate with fixed code!")
print()
print("=" * 70)
print()

# Find all custom voices with .pth files
voices_dir = "tortoise/voices"
custom_voices = []

if os.path.exists(voices_dir):
    for voice_name in os.listdir(voices_dir):
        voice_path = os.path.join(voices_dir, voice_name)
        if os.path.isdir(voice_path):
            pth_file = os.path.join(voice_path, f"{voice_name}.pth")
            audio_files = [f for f in os.listdir(voice_path) 
                          if f.endswith(('.wav', '.mp3', '.flac'))]
            
            # Custom voice if it has audio files (not just built-in)
            if audio_files and os.path.exists(pth_file):
                # Get file creation time
                import datetime
                pth_time = os.path.getctime(pth_file)
                pth_date = datetime.datetime.fromtimestamp(pth_time)
                
                custom_voices.append({
                    'name': voice_name,
                    'pth_file': pth_file,
                    'audio_count': len(audio_files),
                    'created': pth_date
                })

if not custom_voices:
    print("No custom voices with .pth files found.")
    print()
    print("This is actually GOOD if you just uploaded voices!")
    print("It means the new .pth files will be generated with proper normalization.")
    sys.exit(0)

print(f"Found {len(custom_voices)} custom voice(s) with .pth files:\n")

for v in custom_voices:
    print(f"📁 {v['name']}")
    print(f"   Audio files: {v['audio_count']}")
    print(f"   .pth created: {v['created'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   File: {v['pth_file']}")
    print()

print("=" * 70)
print("RECOMMENDATION:")
print("=" * 70)
print()
print("If these .pth files were created BEFORE you restarted the web server")
print("with the DC offset fix, they contain BAD conditioning latents!")
print()
print("🔧 FIX: Delete the .pth files and regenerate them:")
print()

for v in custom_voices:
    print(f'   del "{v["pth_file"]}"')

print()
print("Then either:")
print("  1. Restart web server - it will auto-regenerate on first use")
print("  2. Delete and re-upload the voice (recommended)")
print()
print("=" * 70)
print()
print("WHY THIS MATTERS:")
print("=" * 70)
print()
print("• When a .pth file exists, Tortoise uses ONLY that file")
print("• It completely ignores the audio files")
print("• If .pth has bad data, you get bad cloning")
print("• YouTube tutorials likely DON'T have .pth files yet")
print("• So they're using raw audio (which processes correctly)")
print()
print("YOUR ISSUE: Old .pth files have pre-normalized audio data!")
print("Their SOLUTION: No .pth files, so audio is processed fresh each time")
print()
print("=" * 70)
