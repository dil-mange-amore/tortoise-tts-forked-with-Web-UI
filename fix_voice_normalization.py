"""
Re-normalize existing voice files to fix low amplitude issues
"""
import torch
import torchaudio
import os
import sys
import shutil

def normalize_voice_folder(voice_name, backup=True):
    """
    Re-normalize all audio files in a voice folder
    """
    voice_dir = f"tortoise/voices/{voice_name}"
    
    if not os.path.exists(voice_dir):
        print(f"❌ Error: Voice directory not found: {voice_dir}")
        return False
    
    # Find all audio files
    audio_files = []
    for file in os.listdir(voice_dir):
        if file.endswith(('.wav', '.mp3', '.flac')) and not file.endswith('_backup.wav'):
            audio_files.append(os.path.join(voice_dir, file))
    
    if not audio_files:
        print(f"❌ No audio files found in {voice_dir}")
        return False
    
    print(f"\nRe-normalizing voice: {voice_name}")
    print(f"Found {len(audio_files)} audio files")
    
    if backup:
        print("\n📦 Creating backups...")
        for filepath in audio_files:
            backup_path = filepath.rsplit('.', 1)[0] + '_backup.wav'
            shutil.copy2(filepath, backup_path)
            print(f"  Backed up: {os.path.basename(filepath)}")
    
    print("\n🔄 Normalizing files...")
    
    for filepath in audio_files:
        try:
            # Load audio
            audio, sr = torchaudio.load(filepath)
            
            # Get original stats
            orig_max = torch.max(torch.abs(audio)).item()
            orig_mean = audio.mean().item()
            
            # Remove DC offset
            audio = audio - audio.mean()
            
            # Normalize to [-1, 1]
            max_val = torch.max(torch.abs(audio))
            if max_val > 0:
                audio = audio / max_val
            
            # Get new stats
            new_max = torch.max(torch.abs(audio)).item()
            new_mean = audio.mean().item()
            
            # Save normalized version
            torchaudio.save(filepath, audio, sr)
            
            print(f"  ✅ {os.path.basename(filepath)}: {orig_max:.3f} → {new_max:.3f}")
            
        except Exception as e:
            print(f"  ❌ Failed to normalize {os.path.basename(filepath)}: {str(e)}")
            return False
    
    # Delete .pth file if it exists (needs regeneration)
    pth_file = os.path.join(voice_dir, f"{voice_name}.pth")
    if os.path.exists(pth_file):
        os.remove(pth_file)
        print(f"\n🗑️  Deleted {voice_name}.pth (will be regenerated on next use)")
    
    print(f"\n✅ Successfully normalized voice: {voice_name}")
    print("   Next generation will auto-create new .pth file")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_voice_normalization.py <voice_name>")
        print("Example: python fix_voice_normalization.py simp")
        print("\nThis will:")
        print("  1. Backup original files")
        print("  2. Normalize audio to [-1, 1] range")
        print("  3. Delete .pth file (will regenerate)")
        sys.exit(1)
    
    voice_name = sys.argv[1]
    
    print("="*60)
    print("Voice Normalization Fix")
    print("="*60)
    
    success = normalize_voice_folder(voice_name, backup=True)
    
    if success:
        print("\n" + "="*60)
        print("✅ DONE! Voice should now work better!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Generate speech with this voice")
        print("  2. It will auto-create new .pth file")
        print("  3. Voice quality should now match input better")
    else:
        print("\n" + "="*60)
        print("❌ Failed to normalize voice")
        print("="*60)
        sys.exit(1)
