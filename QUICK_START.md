# 🐢 Tortoise TTS Web UI - Quick Reference

## Starting the Service

### Easy Way (Recommended)
Double-click one of these files:
- `start_webui.bat` (Command Prompt)
- `start_webui.ps1` (PowerShell)

### Manual Way
```bash
conda activate tortoise
python web_ui.py
```

Then open: **http://localhost:5000**

## Main Features

### 🎙️ Text-to-Speech Generation
1. **Enter text** in the text area
2. **Select voice** from dropdown (or "Random")
3. **Choose quality**:
   - Ultra Fast: Quick test (lower quality)
   - Fast: Good for most uses ⭐
   - Standard: Better quality
   - High Quality: Best (slowest)
4. **Set candidates**: Higher = better quality but slower
5. Click **"Generate Speech"**
6. **Cancel** button appears if you want to stop

### 📁 Output Files
- **Location**: `%USERPROFILE%\Music\Tortoise Output`
- **File names**: `VoiceName-Preset-Candidates-###.wav`
- **Examples**:
  ```
  random-fast-1x-001.wav
  emma-standard-3x-002.wav
  tom-high_quality-4x-015.wav
  ```

### 🎵 Custom Voices
1. Go to **"Manage Voices"** tab
2. Enter a custom voice name
3. Upload 2-5 audio files (WAV, MP3, FLAC)
   - Each clip: 10-30 seconds
   - Clear speech, same person
   - No background noise
4. Click **"Upload Voice Files"**
5. Your voice now appears in the voice selector!

## Header Buttons

| Button | Function |
|--------|----------|
| 📁 Open Output Folder | Opens `Music\Tortoise Output` in Explorer |
| 🔄 Restart Service | Restarts the web server |
| ⏹️ Stop Service | Stops the server (need manual restart) |

## Debug Console (🐛)

**Located**: Bottom-right corner floating button

**Features**:
- 📊 Real-time server logs
- 🎨 Color-coded messages (info, success, warning, error)
- 🔄 Auto-updates every second
- 📌 Auto-scroll toggle
- 🗑️ Clear logs button
- ✖ Close/minimize console

**When to use**:
- ❓ Something not working? Check the debug console!
- 🐞 See exactly what the server is doing
- ⚠️ View error messages and stack traces
- 📝 Monitor generation progress

## Tips & Tricks

### For Fastest Results
- Use **"fast"** preset
- Set candidates to **1**
- Use a named voice (not random)

### For Best Quality
- Use **"high_quality"** preset
- Set candidates to **3 or 4**
- Use a custom voice with good samples

### Cancelling Generation
- Click **"✖ Cancel"** during generation
- May take a few seconds to stop
- Server remains running

### Managing Files
1. Click **"📁 Open Output Folder"**
2. Files are automatically organized
3. Numbered sequentially (001, 002, 003...)
4. Delete unwanted files from folder

## Keyboard Shortcuts

While on the page:
- **Ctrl + Enter** in text area: Generate speech (if implemented)
- **Ctrl + C** in terminal: Stop service

## Common Issues

### Generation Too Slow
- ✅ Use "fast" preset
- ✅ Reduce candidates to 1
- ✅ Click Cancel if needed
- ✅ First generation loads models (slow once)

### Can't Find Output Files
- ✅ Click "Open Output Folder" button
- ✅ Default: `C:\Users\YourName\Music\Tortoise Output`

### Service Won't Start
- ✅ Check conda environment is activated
- ✅ Use provided startup scripts
- ✅ Check port 5000 isn't in use
- ✅ Check debug console for error messages

### Something Not Working?
- ✅ **Open Debug Console** (🐛 button)
- ✅ Look for red error messages
- ✅ Check what step failed
- ✅ Copy error message for troubleshooting

### Custom Voice Not Working
- ✅ Upload 2-5 clips (not just 1)
- ✅ Each clip 10-30 seconds
- ✅ Use WAV format for best results
- ✅ Ensure same person in all clips

## File Naming Convention

Format: `{Voice}-{Preset}-{Candidates}x-{Number}.wav`

Examples:
```
random-fast-1x-001.wav          # First file with random voice
emma-fast-1x-002.wav            # Second file with emma voice
tom-standard-3x-003.wav         # Third file, 3 candidates
myvoice-high_quality-4x-004.wav # Custom voice, best quality
```

## Quality vs Speed Guide

| Preset | Speed | Quality | Best For |
|--------|-------|---------|----------|
| Ultra Fast | ⚡⚡⚡⚡ | ⭐ | Quick tests |
| Fast | ⚡⚡⚡ | ⭐⭐⭐ | General use ⭐ |
| Standard | ⚡⚡ | ⭐⭐⭐⭐ | Good quality |
| High Quality | ⚡ | ⭐⭐⭐⭐⭐ | Best results |

## Candidates Explained

- **1 candidate**: Generate once, use result (fastest)
- **2-4 candidates**: Generate multiple, pick best (CLVP scores)
- Higher candidates = better quality but slower

## Need Help?

1. Check the full **WEB_UI_README.md** for detailed instructions
2. Check terminal output for error messages
3. Try restarting the service
4. Check that models are downloaded (first run takes time)

---

**Happy voice generating! 🎤🐢**
