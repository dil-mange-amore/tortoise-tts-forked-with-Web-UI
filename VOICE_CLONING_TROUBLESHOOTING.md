# Voice Cloning Troubleshooting Guide

## Why Your Voice Cloning Might Not Match YouTube Tutorials

### Issue 1: Preset Selection ⚙️
**YouTube tutorials use `fast` or `standard`, NOT `ultra_fast`**

- `ultra_fast`: 16 samples - **TOO FEW for good voice cloning**
- `fast`: 96 samples - **MINIMUM for decent cloning** (5-8 min)
- `standard`: 256 samples - **GOOD quality** (15-20 min)
- `high_quality`: 256 samples - **BEST quality** (30+ min)

### Issue 2: Candidates Matter 🎯
**More candidates = better results**

- 1 candidate: Takes whatever it generates
- **3 candidates**: Generates 3, picks best (RECOMMENDED)
- 5 candidates: Even better, but slower

### Issue 3: Audio Duration 📊
**You need MORE audio than you think**

- Your current: 9 segments (90 seconds)
- Tutorials often use: **2-5 MINUTES** (120-300 seconds)
- More audio = better voice matching

### Issue 4: Audio Quality 🎤
**Clean, clear recordings are CRITICAL**

- No background noise
- Consistent volume
- Good microphone
- Varied sentences (not monotone)

### Issue 5: The .pth File Problem 🔄
**If audio was processed before the DC offset fix was applied**

Your `.pth` file contains OLD data. You MUST regenerate it!

## ✅ SOLUTION: Complete Reset & Proper Settings

### Step 1: Delete Old .pth File
```powershell
# For your newly uploaded voice
del "tortoise\voices\Aniket_K\Aniket_K.pth"

# For recorded voice
del "tortoise\voices\Amol\Amol.pth"
```

### Step 2: Regenerate .pth with Fixed Code
```powershell
# Restart web server to ensure new code is active
# Stop current server (Ctrl+C)
python web_ui.py
```

Then in web UI:
1. Go to "Manage Voices"
2. Delete the voice
3. Re-upload or re-record with **MORE audio** (2-3 minutes minimum)

### Step 3: Generate with PROPER Settings
**CRITICAL - Use these exact settings:**

1. **Voice**: Your custom voice
2. **Preset**: **`fast`** (NOT ultra_fast!)
3. **Candidates**: **3**
4. **Text**: Use the SAME text as YouTube tutorial for comparison

### Step 4: Wait Patiently
- `fast` preset with 3 candidates takes **5-8 minutes**
- This is NORMAL and NECESSARY for good quality
- Don't use ultra_fast expecting good cloning

## 🎯 Expected Results

### With Proper Settings:
✅ Voice should sound similar to input
✅ Prosody (rhythm/intonation) should match
✅ Tone and pitch should be recognizable

### Still Not Perfect? Try:
1. **Record MORE audio** (2-5 minutes total)
2. **Use `standard` preset** instead of `fast`
3. **Increase candidates to 5**
4. **Ensure clean, varied audio samples**

## 🚫 Common Mistakes

❌ Using `ultra_fast` preset (only 16 samples - too few!)
❌ Only 1 candidate (no selection, takes first result)
❌ Less than 2 minutes of audio
❌ Monotone or similar-sounding clips
❌ Background noise or poor audio quality
❌ Not regenerating .pth after code fix
❌ Comparing ultra_fast results to tutorial's fast/standard results

## 📺 YouTube Tutorial Settings (Typical)

Most YouTube tutorials use:
- **3-5 minutes of audio** (not 90 seconds!)
- **`fast` or `standard` preset** (not ultra_fast!)
- **3-5 candidates**
- **High-quality studio mic** or **clean phone recording**
- **Varied emotional content** (questions, statements, emphasis)

## 🔧 Action Plan

1. **Delete all .pth files for your custom voices**
2. **Record/upload 2-3 MINUTES of audio** (not 90 seconds)
3. **Use `fast` preset with 3 candidates**
4. **Wait 5-8 minutes for generation**
5. **Compare results**

If still not matching:
- Try `standard` preset (15-20 min)
- Use 5 candidates instead of 3
- Record even more audio (5 minutes)

---

**The key insight**: YouTube tutorials are using MUCH longer generation times (fast/standard preset) with MORE audio. You can't get the same quality with ultra_fast + 90 seconds of audio!
