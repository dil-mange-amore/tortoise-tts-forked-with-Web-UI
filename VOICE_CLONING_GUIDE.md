# Voice Cloning Guide for Tortoise TTS

## Overview

The web UI now includes **automatic audio preprocessing** for optimal voice cloning results. When you upload audio files, they are automatically:

1. ✂️ **Split into 10-second segments** (optimal length for training)
2. 🎵 **Resampled to 22050Hz** (required sample rate)
3. 💾 **Converted to float32 WAV format** (best quality)
4. 📊 **Converted to mono** (if stereo)

## Quick Start

The web UI offers **two methods** for adding custom voices:

### Method 1: Upload Audio Files 📁

#### Step 1: Prepare Audio Files

Collect audio recordings of the voice you want to clone:

- **Format**: WAV, MP3, FLAC, OGG, or M4A
- **Duration**: At least 70-100 seconds total (more is better)
- **Quality**: Clear speech, minimal background noise
- **Content**: Natural speech, varied sentences

**Recommendations**:
- ✅ Provide at least 70-100 seconds of audio (7-10 segments)
- ✅ Use multiple short clips (easier to manage)
- ✅ Include varied intonations and emotions
- ✅ Clean, clear recordings without music
- ❌ Avoid heavily compressed audio
- ❌ Avoid recordings with echo or reverb
- ❌ Don't upload less than 50 seconds (quality will be poor)

#### Step 2: Upload via Web UI

1. Open http://localhost:5000
2. Click **"Manage Voices"** tab
3. Select **"📁 Upload Files"** tab
4. Enter a **Voice Name** (e.g., "my_voice")
5. Select one or more audio files
6. Click **Upload Voice Files**

The system will automatically:
- Process each file
- Split into 10-second segments
- Save as optimized WAV files at 22050Hz
- **Generate .pth file automatically**
- Show progress in the debug console

### Method 2: Record Voice 🎙️ (NEW!)

#### Step 1: Access Recording Interface

1. Open http://localhost:5000
2. Click **"Manage Voices"** tab
3. Select **"🎙️ Record Voice"** tab
4. Enter a **Voice Name** (e.g., "my_voice")

#### Step 2: Record Clips

1. **Read the paragraph** displayed on screen
2. Click **"🎙️ Start Recording (30s)"**
3. **Read clearly** into your microphone
4. Recording stops automatically after 30 seconds (or click Stop)
5. Click **"New Paragraph"** to get a different text
6. Repeat until you have **7-10 clips** (recommended)

**Tips for best quality**:
- 🎤 Use a good microphone in a quiet room
- 📖 Read naturally with varied emotions
- 🔊 Maintain consistent volume and distance
- ⏱️ Use the full 30 seconds for each clip
- 🔄 Record 7-10 clips minimum

#### Step 3: Create Voice

1. Review your recorded clips (delete bad ones if needed)
2. Click **"✅ Create Voice from Recordings"**
3. System automatically:
   - Processes all recordings
   - Splits into 10-second segments
   - Generates .pth file
   - Makes voice instantly ready!

**Note**: The .pth file generation happens automatically, so your voice is instantly ready to use!

### Step 3: Verify Segments

After upload completes, check the debug console:

```
✅ Created 8 segments - good for cloning!
```

**Critical Minimum**: 5 segments (50 seconds) - below this, quality will be poor  
**Recommended Minimum**: 7 segments (70 seconds) - acceptable quality  
**Good**: 10+ segments (100+ seconds) - good quality  
**Optimal**: 20+ segments (200+ seconds) - best quality

### Step 4: Generate Speech (Ready Immediately!)

**The .pth file is now automatically generated during upload**, so you can start generating speech right away!

1. Select your voice from the dropdown (it will load instantly thanks to the .pth file!)
2. Enter text to generate
3. Choose preset (start with `ultra_fast` for testing)
4. Click **Generate**

### Manual .pth Generation (Only if Automatic Failed)

If the automatic .pth generation failed during upload, you can manually create it:

**Option A: Single Voice**
```powershell
conda activate tortoise
python tortoise\get_conditioning_latents.py --voice my_voice --output_path tortoise\voices\my_voice
```

**Option B: All Voices (Batch)**
```powershell
.\generate_all_pth.bat
```

## Technical Details

### Audio Specifications

The preprocessing ensures compatibility with Tortoise's requirements:

- **Sample Rate**: 22050 Hz (required by model)
- **Format**: WAV with float32 encoding
- **Channels**: Mono (stereo converted automatically)
- **Segment Length**: 10 seconds (optimal for training)
- **Bit Depth**: 32-bit floating point

### File Naming Convention

Uploaded files are processed and saved as:
```
clip_00_0.wav  <- First file, segment 0
clip_00_1.wav  <- First file, segment 1
clip_01_0.wav  <- Second file, segment 0
...
```

### Why 10-Second Segments?

Tortoise's autoregressive model performs best with:
- **Segment length**: 5-15 seconds
- **Optimal**: 10 seconds
- **Multiple segments**: Better than one long file

## Troubleshooting

### Problem: Voice sounds completely different from input

**Root Cause**: Audio normalization or format issues (now fixed automatically!)

**Automatic Fixes** (built-in):
- ✅ Audio is normalized to [-1, 1] range (critical for voice matching)
- ✅ Saved as standard 16-bit PCM WAV format (Tortoise-compatible)
- ✅ Quality validation (checks for silent/corrupted audio)
- ✅ NaN/Infinity detection (prevents invalid data)

**If still having issues**:
1. Check debug console for "Normalized audio to [-1, 1] range" messages
2. Look for errors: "Audio is silent" or "invalid values"
3. Try different source audio files
4. Ensure microphone/recording quality is good

### Problem: "Only X segments created" (where X < 7)

**Cause**: Not enough audio provided  
**Solution**: Upload more audio files or longer recordings  
**Target**: Aim for at least 70-100 seconds total (7-10 segments)

### Problem: Poor cloning quality (robotic/unclear)

**Possible causes**:
1. **Too few segments** (< 7) - Upload more audio (aim for 70-100+ seconds)
2. **Poor audio quality** - Use cleaner recordings
3. **Background noise** - Remove or reduce noise
4. **Varied speakers** - Use audio from only one person
5. **Mixed content** - Avoid audio with music or sound effects
6. **Clipping/distortion** - Don't speak too loud into microphone

**Solutions**:
- Upload at least 70-100 seconds of clean speech (7-10+ segments)
- Use audio from a single speaker
- Prefer studio-quality or clear phone recordings
- Include varied sentences and emotions
- Maintain consistent volume and distance from microphone
- If you have less than 5 segments, quality will be very poor - get more audio!

### Problem: Generation doesn't sound like the voice

**Try**:
1. Verify .pth file was generated (check debug console)
2. Use `fast` or `standard` preset (not `ultra_fast`)
3. Increase candidates to 3-5 (generates multiple attempts)
4. Upload more varied audio samples (10-15 segments)
5. Ensure audio is truly representative of the voice
6. Record in quiet environment without background noise

## Best Practices

### ✅ Do

- Upload 70-120 seconds of audio total (aim for 7-12+ segments)
- Use clear, clean recordings
- Include natural speech patterns
- Upload multiple short clips
- Test with `ultra_fast` preset first
- `.pth` file is automatically generated
- Use `fast` or `standard` for final output
- Verify you have at least 7 segments after upload

### ❌ Don't

- Upload less than 70 seconds (poor quality below 7 segments)
- Use heavily compressed MP3s
- Include background music
- Mix multiple speakers
- Use audio with echo/reverb
- Expect perfect results on first try
- Ignore warnings about segment count

## Example Workflow

```powershell
# 1. Start web UI
python web_ui.py

# 2. Upload voice files via browser
#    - Name: "john_doe"
#    - Files: 5 audio clips (15-20s each)
#    Result: 8-10 segments created + .pth file automatically generated!

# 3. Test generation (voice loads instantly!)
#    - Select "john_doe" from dropdown
#    - Text: "Hello, this is a test."
#    - Preset: ultra_fast
#    - Click Generate
#    Voice loads instantly thanks to .pth file!

# 4. Final generation
#    - Preset: fast or standard
#    - Candidates: 3
```

## Advanced Tips

### Multiple Takes

Upload the same sentence multiple times with different emotions:
- Neutral tone
- Happy/excited
- Sad/serious
- Question intonation

This helps the model capture voice range.

### Segment Verification

After upload, check the voice folder:
```powershell
ls tortoise\voices\my_voice\
```

Should see: `clip_00_0.wav`, `clip_00_1.wav`, etc.

### Manual Audio Preparation (Alternative)

If you prefer to prepare audio manually:

```python
import torchaudio

# Load audio
audio, sr = torchaudio.load("input.wav")

# Resample to 22050Hz
resampler = torchaudio.transforms.Resample(sr, 22050)
audio = resampler(audio)

# Convert to mono
if audio.shape[0] > 1:
    audio = audio.mean(dim=0, keepdim=True)

# Save as float32 WAV
torchaudio.save("output.wav", audio, 22050, encoding="PCM_F", bits_per_sample=32)
```

## Comparison with Manual Methods

| Method | Segments | Resampling | Format | Convenience |
|--------|----------|------------|--------|-------------|
| **Web UI (Auto)** | ✅ Automatic | ✅ Auto 22050Hz | ✅ Float32 WAV | ⭐⭐⭐⭐⭐ |
| Manual Upload | ❌ Manual split | ❌ Manual | ❌ Any format | ⭐⭐ |
| Script/Python | ✅ Script-based | ✅ Configurable | ✅ Configurable | ⭐⭐⭐ |

## Resources

- Main README: `README.md`
- Web UI Guide: `WEB_UI_README.md`
- Voice Customization: `voice_customization_guide.md`
- Speed Guide: `SPEED_GUIDE.md`

## Support

If you encounter issues:
1. Check debug console for error messages
2. Verify audio files are valid
3. Ensure at least 50 seconds of audio
4. Try different audio sources
5. Review troubleshooting section above

---

**Note**: Voice cloning quality depends heavily on:
- Audio quality and length
- Voice uniqueness and clarity
- Tortoise model's training data
- Generation preset and candidates

Experiment with different settings for best results!
