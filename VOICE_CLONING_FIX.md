# Voice Cloning Quality Fix

## Issue

User reported that cloned voices sounded completely different from the input voice:
> "the cloned voice is not coming out exactly as expected clone. instead i hear a lot different voice"

## Root Cause

Audio samples were not being properly normalized before being saved for voice cloning. Tortoise TTS expects audio in the **[-1, 1] normalized range** for proper voice matching in conditioning latents.

### Technical Details

From `tortoise/utils/audio.py`:
```python
def load_audio(audiopath, sampling_rate):
    # ... loads audio ...
    # Expects audio in [-1, 1] range
    audio.clip_(-1, 1)  # Clips to ensure range
    
    # Has assumptions checks:
    if torch.any(audio > 2) or not torch.any(audio < 0):
        # Audio outside expected range!
```

Our preprocessing was:
1. Loading audio with torchaudio
2. Resampling to 22050Hz
3. Converting to mono
4. **NOT normalizing before saving** ❌
5. Saving as float32 PCM WAV

This meant audio values could be in arbitrary ranges (e.g., 0-32768 for int16, or unnormalized float), causing Tortoise to receive audio outside the expected [-1, 1] range, resulting in poor voice matching.

## Fixes Implemented

### Fix 1: Explicit Audio Normalization

Added normalization step in `process_audio_for_cloning()` before splitting into segments:

```python
# Normalize audio to [-1, 1] range (CRITICAL for Tortoise)
max_val = torch.max(torch.abs(audio))
if max_val > 0:
    audio = audio / max_val
    add_debug_log(f"Normalized audio to [-1, 1] range (max was {max_val:.4f})", "info")
else:
    add_debug_log("⚠️ WARNING: Audio is silent (all zeros)!", "error")
    raise ValueError("Audio file is silent or corrupted")
```

**Why this matters**: 
- Dividing by the maximum absolute value ensures all audio samples are within [-1, 1]
- Tortoise's voice matching algorithms rely on this normalized range
- Without normalization, voice characteristics are distorted

### Fix 2: Audio Quality Validation

Added checks to detect corrupted or invalid audio:

```python
# Verify audio quality
if torch.any(torch.isnan(audio)) or torch.any(torch.isinf(audio)):
    add_debug_log("⚠️ WARNING: Audio contains NaN or Inf values!", "error")
    raise ValueError("Audio file contains invalid values")
```

**Why this matters**:
- Prevents processing of corrupted audio files
- Catches issues early with clear error messages
- Avoids generating poor-quality conditioning latents

### Fix 3: Standard WAV Format

Changed from float32 PCM to standard 16-bit PCM WAV:

```python
# OLD:
torchaudio.save(output_path, segment.unsqueeze(0), sr, 
                encoding="PCM_F", bits_per_sample=32)

# NEW:
torchaudio.save(output_path, segment.unsqueeze(0), sr)
# Saves as 16-bit PCM WAV (standard format that Tortoise expects)
```

**Why this matters**:
- Standard WAV format is more compatible with Tortoise's loader
- `load_wav_to_torch()` has specific normalization logic for standard WAV files
- Reduces potential format-related issues

## Impact

### Before Fix
- Audio saved with arbitrary value ranges (0-32768, 0-1, etc.)
- Tortoise received audio outside [-1, 1] range
- Voice matching algorithms couldn't properly extract voice characteristics
- Result: Cloned voice sounded completely different

### After Fix
- All audio explicitly normalized to [-1, 1] range
- Tortoise receives audio in expected format
- Voice matching algorithms work correctly
- Result: Cloned voice should accurately match input voice

## Testing

To test the fix:

1. **Restart the web server**:
   ```powershell
   python web_ui.py
   ```

2. **Upload a voice sample** (Method 1):
   - Go to "Manage Voices" → "Upload Files"
   - Upload 70+ seconds of audio
   - Check debug console for: "Normalized audio to [-1, 1] range"

3. **OR record voice clips** (Method 2):
   - Go to "Manage Voices" → "Record Voice"
   - Record 7-10 clips of 30 seconds each
   - Check debug console for normalization messages

4. **Generate speech**:
   - Select your voice from dropdown
   - Enter test text
   - Use `fast` or `standard` preset
   - Generate audio

5. **Compare**:
   - Listen to generated audio
   - Compare with original voice
   - Should now sound much more similar!

## Debug Console Messages

Look for these messages confirming the fix is working:

```
✅ Normalized audio to [-1, 1] range (max was 32768.0000)
Processing segment 1/8...
Processing segment 2/8...
...
✅ Auto-generating conditioning latents (.pth file)...
✅ Created 8 segments - good for cloning!
```

## Troubleshooting

### If quality is still poor:

1. **Check segment count**: Need at least 7 segments (70 seconds)
   - Solution: Upload more audio or record more clips

2. **Check audio quality**: Background noise, echo, distortion
   - Solution: Use cleaner recordings in quiet environment

3. **Check debug console**: Look for error messages
   - "Audio is silent" → File is corrupted or empty
   - "invalid values" → File contains NaN/Inf
   - Low max value in normalization → Audio too quiet

4. **Try different source audio**: Some recordings work better than others
   - Use varied sentences and emotions
   - Maintain consistent volume and quality

## Technical Reference

### Files Modified

1. **web_ui.py** (lines ~185-220):
   - Added audio normalization in `process_audio_for_cloning()`
   - Added quality validation checks
   - Changed to standard WAV format
   - Added debug logging for normalization

2. **VOICE_CLONING_GUIDE.md**:
   - Updated troubleshooting section
   - Added "Voice sounds completely different" problem
   - Documented automatic fixes
   - Added quality validation info

3. **README.md**:
   - Updated Method 1 description
   - Added normalization step to feature list
   - Added quality validation mention
   - Updated format specification

### Audio Processing Pipeline (Updated)

```
Input Audio
    ↓
Load with torchaudio.load()
    ↓
Convert stereo → mono (if needed)
    ↓
Resample to 22050Hz
    ↓
⭐ NORMALIZE to [-1, 1] range ⭐ (NEW!)
    ↓
✅ Validate quality (no NaN/Inf) ✅ (NEW!)
    ↓
Split into 10-second segments
    ↓
Save as standard 16-bit PCM WAV
    ↓
Generate conditioning latents (.pth)
    ↓
Voice ready for cloning!
```

## Expected Results

With this fix:
- ✅ Voice cloning accuracy significantly improved
- ✅ Cloned voice matches input voice characteristics
- ✅ Better preservation of tone, pitch, and speaking style
- ✅ Reduced "completely different voice" issues
- ✅ More consistent quality across different audio sources

## Credits

Fix implemented by: **[dil-mange-amore]**

Issue diagnosed through investigation of Tortoise's `audio.py` utilities and understanding of the expected audio format for conditioning latent generation.

---

**Date**: 2024  
**Version**: v1.0 (Initial fix implementation)
