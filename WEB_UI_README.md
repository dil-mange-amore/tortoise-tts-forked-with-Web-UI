# Tortoise TTS Web UI

A simple and user-friendly web interface for Tortoise TTS.

## Features

- 🎙️ **Text-to-Speech Generation**: Convert text to speech with various voices
- 🎭 **Voice Selection**: Choose from built-in voices or use custom voices
- 📁 **Custom Voice Upload**: Upload your own voice samples (2-5 WAV files)
- ⚙️ **Configurable Options**:
  - Quality presets (ultra_fast, fast, standard, high_quality)
  - Number of candidates for better quality
- 💾 **Auto-Save to Music Folder**: Generated audio automatically saved to `Music\Tortoise Output`
- 📂 **Smart File Naming**: Files named as `VoiceName-Preset-Candidates-###.wav`
- 🎵 **Download & Play**: Play audio immediately or download it
- 🗑️ **Voice Management**: Delete custom voices
- ✖️ **Cancel Generation**: Stop ongoing generation process
- 🔄 **Service Controls**: Start, stop, and restart the service from web UI
- 📁 **Quick Access**: Open output folder directly in Windows Explorer
- 🐛 **Debug Console**: Real-time debug output with color-coded log levels

## Installation

Make sure you have already installed Tortoise TTS following the main README.

Install Flask (if not already installed):
```bash
conda activate tortoise
pip install flask
```

## Quick Start

### Method 1: Using Startup Script (Recommended)

**Windows Command Prompt:**
```bash
start_webui.bat
```

**PowerShell:**
```powershell
.\start_webui.ps1
```

These scripts will automatically:
- Activate the conda environment
- Start the web server
- Open at http://localhost:5000

### Method 2: Manual Start

1. **Activate the environment:**
   ```bash
   conda activate tortoise
   ```

2. **Start the web server:**
   ```bash
   python web_ui.py
   ```

3. **Open your browser:**
   Navigate to `http://localhost:5000`

## How to Use

### Generate Speech

1. Go to the "Generate Speech" tab
2. Enter your text in the text area
3. Select a voice (or use "Random")
4. Choose quality preset and number of candidates
5. Click "Generate Speech"
6. Wait for generation (first time will be slower as models load)
   - Click "Cancel" button if you want to abort
7. Audio will be:
   - Automatically saved to `%USERPROFILE%\Music\Tortoise Output`
   - Named as `VoiceName-Preset-Candidates-###.wav`
   - Playable immediately in the browser
   - Downloadable via the download button

### Output Files

Generated files are automatically saved with descriptive names:
- **Format**: `VoiceName-Preset-Candidates-###.wav`
- **Examples**:
  - `random-fast-1x-001.wav`
  - `emma-standard-3x-002.wav`
  - `tom-high_quality-4x-003.wav`

**Open Output Folder**: Click the "📁 Open Output Folder" button in the header to open the location in Windows Explorer.

### Custom Voices

1. Go to the "Manage Voices" tab
2. Enter a name for your custom voice
3. Click the upload area or drag audio files
4. Upload 2-5 audio clips (10-30 seconds each) of the same person speaking
5. Click "Upload Voice Files"
6. Your custom voice will now appear in the voice selection dropdown

**Tips for custom voices:**
- Use clear, high-quality recordings
- Each clip should be 10-30 seconds long
- All clips should be from the same person
- Avoid background noise
- Use WAV format for best results

### Delete Custom Voices

1. Go to the "Manage Voices" tab
2. Find your custom voice in the list
3. Click the "Delete" button
4. Confirm deletion

## Options Explained

- **Ultra Fast**: Fastest generation, lower quality (good for testing)
- **Fast**: Quick generation with decent quality (recommended for most use)
- **Standard**: Balanced quality and speed
- **High Quality**: Best quality, slower generation

- **Candidates**: Number of samples to generate and pick the best from
  - 1 = Fastest
  - 3-4 = Better quality but slower

## Service Controls

The web UI includes service management buttons in the header:

- **📁 Open Output Folder**: Opens `Music\Tortoise Output` in Windows Explorer
- **🔄 Restart Service**: Restarts the web service (useful after errors)
- **⏹️ Stop Service**: Stops the web service completely

### Cancel Generation

If a generation is taking too long or you want to stop it:
1. Click the "✖ Cancel" button that appears during generation
2. The system will attempt to cancel the ongoing process
3. Note: Cancellation may take a few seconds

## Troubleshooting

**Server won't start:**
- Make sure the conda environment is activated
- Check if port 5000 is already in use
- Use the provided startup scripts (`start_webui.bat` or `start_webui.ps1`)

**Generation is slow:**
- First generation loads models (takes time)
- Use "fast" preset for quicker results
- Reduce number of candidates
- Use the Cancel button if needed

**Custom voice doesn't work well:**
- Try uploading more/better quality samples
- Ensure all samples are from the same person
- Use clear speech without music or background noise

**Output folder location:**
- Default: `%USERPROFILE%\Music\Tortoise Output`
- Example: `C:\Users\YourName\Music\Tortoise Output`
- Click "Open Output Folder" button to view location

**Service management:**
- Use "Restart Service" if the service becomes unresponsive
- Use "Stop Service" to cleanly shut down the server
- Restart manually by running the startup script again

**Debug Console:**
- Click the 🐛 button (bottom-right corner) to open debug console
- View real-time server logs and error messages
- Color-coded log levels:
  - 🟢 Green: Success messages
  - 🔵 Cyan: Info messages
  - 🟡 Yellow: Warning messages
  - 🔴 Red: Error messages
- Auto-scroll keeps latest logs visible
- Clear logs to start fresh
- Updates automatically every second

## Notes

- First generation will take longer as models are loaded into memory
- Models require significant GPU memory (6GB+ recommended)
- Generated audio is 24kHz WAV format
- Built-in voices cannot be deleted

## Built-in Voices

The following voices come pre-installed:
- angie, daniel, deniro, emma, freeman, geralt, halle, jlaw, lj, mol, tom, william

## API Endpoints

If you want to integrate with other applications:

- `GET /api/voices` - Get list of available voices
- `POST /api/generate` - Generate speech from text
- `POST /api/upload_voice` - Upload custom voice
- `DELETE /api/delete_voice/<name>` - Delete custom voice

Enjoy using Tortoise TTS! 🐢
