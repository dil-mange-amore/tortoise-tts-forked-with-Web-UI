"""
Simple Web UI for Tortoise TTS
"""
import os
import sys
import io
import base64
import subprocess
import threading
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import torch
import torchaudio
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voices
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'tortoise/voices'

# Output to Windows Music folder
MUSIC_FOLDER = Path.home() / "Music" / "Tortoise Output"
MUSIC_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['OUTPUT_FOLDER'] = str(MUSIC_FOLDER)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize TTS (lazy loading)
tts = None
current_generation_thread = None
generation_cancelled = False

# Debug log buffer for web display
debug_logs = []
MAX_DEBUG_LOGS = 100

def add_debug_log(message, level="info"):
    """Add a debug message to the log buffer"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    log_entry = {
        'timestamp': timestamp,
        'level': level,
        'message': str(message)
    }
    debug_logs.append(log_entry)
    # Keep only last MAX_DEBUG_LOGS entries
    if len(debug_logs) > MAX_DEBUG_LOGS:
        debug_logs.pop(0)
    print(f"[{level.upper()}] {message}", flush=True)
    sys.stdout.flush()

def get_tts():
    global tts
    if tts is None:
        add_debug_log("Loading Tortoise TTS models...", "info")
        try:
            # Initialize with smaller batch size to prevent system overload
            # batch_size=4 means 96//4=24 batches for 'fast' preset (safer for low-end systems)
            tts = TextToSpeech(autoregressive_batch_size=4)
            add_debug_log("Models loaded successfully!", "success")
            add_debug_log(f"Using batch size: 4 (optimized for stability)", "info")
            add_debug_log(f"CUDA available: {torch.cuda.is_available()}", "info")
            if torch.cuda.is_available():
                add_debug_log(f"GPU: {torch.cuda.get_device_name(0)}", "info")
        except Exception as e:
            add_debug_log(f"Failed to load models: {str(e)}", "error")
            raise
    return tts

def generate_conditioning_latents(voice_name):
    """
    Generate conditioning latents (.pth) for a voice.
    This pre-computes voice embeddings for instant loading.
    
    Returns: True if successful, False otherwise
    """
    try:
        add_debug_log(f"Generating .pth file for voice '{voice_name}'...", "info")
        
        # Get TTS instance (will use existing if already loaded)
        tts_instance = get_tts()
        
        # Get voice directory
        voice_dir = os.path.join(app.config['UPLOAD_FOLDER'], voice_name)
        
        # Find all audio files in the voice directory
        audio_files = []
        for file in os.listdir(voice_dir):
            if file.endswith(('.wav', '.mp3', '.flac')):
                audio_files.append(os.path.join(voice_dir, file))
        
        if not audio_files:
            add_debug_log(f"No audio files found for voice '{voice_name}'", "error")
            return False
        
        add_debug_log(f"Loading {len(audio_files)} audio samples...", "info")
        
        # Load all audio samples
        conds = []
        for audio_path in audio_files:
            try:
                c = load_audio(audio_path, 22050)
                conds.append(c)
                # Log audio stats for debugging
                device_str = f", device={c.device}" if torch.is_tensor(c) else ""
                add_debug_log(f"  ✓ {os.path.basename(audio_path)}: min={c.min():.3f}, max={c.max():.3f}, mean={c.mean():.3f}{device_str}", "info")
            except Exception as e:
                add_debug_log(f"Failed to load {os.path.basename(audio_path)}: {str(e)}", "warning")
        
        if not conds:
            add_debug_log("No valid audio samples loaded", "error")
            return False
        
        add_debug_log(f"Computing conditioning latents from {len(conds)} samples...", "info")
        
        # Generate conditioning latents
        conditioning_latents = tts_instance.get_conditioning_latents(conds)
        
        # CRITICAL FIX: Move conditioning latents to CPU before saving
        # This prevents "cuda:0 and cpu device mismatch" errors during generation
        if isinstance(conditioning_latents, tuple):
            conditioning_latents = tuple(c.cpu() if torch.is_tensor(c) else c for c in conditioning_latents)
        elif torch.is_tensor(conditioning_latents):
            conditioning_latents = conditioning_latents.cpu()
        
        add_debug_log("Moved conditioning latents to CPU for saving", "info")
        
        # Save to voice directory
        output_path = os.path.join(voice_dir, f'{voice_name}.pth')
        torch.save(conditioning_latents, output_path)
        
        add_debug_log(f"✅ Saved conditioning latents to {voice_name}.pth", "success")
        add_debug_log("Voice will now load instantly!", "success")
        
        return True
        
    except Exception as e:
        add_debug_log(f"Error generating .pth: {str(e)}", "error")
        import traceback
        add_debug_log(traceback.format_exc(), "error")
        return False

def process_audio_for_cloning(audio_path, output_dir, base_name):
    """
    Process audio file for voice cloning:
    - Split into 10-second segments
    - Convert to 22050Hz sample rate
    - Save as WAV with float32 format
    
    Returns: list of processed filenames
    """
    add_debug_log(f"Processing audio: {audio_path}", "info")
    
    try:
        # Check if file is WebM and convert to WAV first
        if audio_path.lower().endswith('.webm'):
            add_debug_log("Converting WebM to WAV...", "info")
            try:
                import subprocess
                # Create temp WAV file
                temp_wav = audio_path.rsplit('.', 1)[0] + '_temp.wav'
                
                # Use ffmpeg to convert WebM to WAV
                result = subprocess.run(
                    ['ffmpeg', '-y', '-i', audio_path, '-ar', '22050', '-ac', '1', temp_wav],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    add_debug_log(f"FFmpeg error: {result.stderr}", "error")
                    raise Exception("FFmpeg conversion failed")
                
                # Use the converted WAV file
                audio_path = temp_wav
                add_debug_log("WebM converted to WAV successfully", "success")
                
            except FileNotFoundError:
                add_debug_log("FFmpeg not found! Installing ffmpeg...", "warning")
                # Try to install ffmpeg-python
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'ffmpeg-python'], 
                             capture_output=True)
                add_debug_log("Please install FFmpeg: https://ffmpeg.org/download.html", "error")
                raise Exception("FFmpeg not installed. Please install FFmpeg and add it to PATH.")
            except subprocess.TimeoutExpired:
                add_debug_log("WebM conversion timed out", "error")
                raise Exception("WebM conversion took too long")
        
        # Load audio using torchaudio
        audio, orig_sr = torchaudio.load(audio_path)
        add_debug_log(f"Loaded audio: {audio.shape} at {orig_sr}Hz", "info")
        
        # Convert to mono if stereo
        if audio.shape[0] > 1:
            audio = torch.mean(audio, dim=0, keepdim=True)
            add_debug_log("Converted stereo to mono", "info")
        
        # Resample to 22050Hz if needed
        if orig_sr != 22050:
            resampler = torchaudio.transforms.Resample(orig_sr, 22050)
            audio = resampler(audio)
            add_debug_log(f"Resampled from {orig_sr}Hz to 22050Hz", "info")
        
        sr = 22050
        audio = audio.squeeze(0)  # Remove channel dimension: (1, samples) -> (samples)
        
        # Remove DC offset (center audio around zero) - CRITICAL for voice cloning
        audio = audio - audio.mean()
        add_debug_log(f"Removed DC offset (mean was {audio.mean():.6f})", "info")
        
        # Normalize audio to [-1, 1] range (CRITICAL for Tortoise)
        max_val = torch.max(torch.abs(audio))
        if max_val > 0:
            audio = audio / max_val
            add_debug_log(f"Normalized audio to [-1, 1] range (max was {max_val:.4f})", "info")
        else:
            add_debug_log("⚠️ WARNING: Audio is silent (all zeros)!", "error")
            raise ValueError("Audio file is silent or corrupted")
        
        # Verify audio has both positive and negative values (Tortoise expects this)
        if not (torch.any(audio > 0) and torch.any(audio < 0)):
            add_debug_log("⚠️ WARNING: Audio doesn't have both positive and negative values!", "warning")
            add_debug_log(f"Min: {audio.min():.6f}, Max: {audio.max():.6f}", "warning")
        
        # Verify audio quality
        if torch.any(torch.isnan(audio)) or torch.any(torch.isinf(audio)):
            add_debug_log("⚠️ WARNING: Audio contains NaN or Inf values!", "error")
            raise ValueError("Audio file contains invalid values")
        
        # Calculate segment length (10 seconds)
        segment_length = 10 * sr  # 10 seconds * sample_rate
        total_duration = audio.shape[0] / sr
        
        # If audio is shorter than 10 seconds, keep as is
        if total_duration < 10:
            add_debug_log(f"Audio is {total_duration:.1f}s - saving as single segment", "warning")
            output_path = os.path.join(output_dir, f"{base_name}_0.wav")
            # Save as 16-bit PCM (standard WAV format that Tortoise expects)
            torchaudio.save(output_path, audio.unsqueeze(0), sr)
            return [f"{base_name}_0.wav"]
        
        # Split into 10-second segments
        processed_files = []
        segment_count = int(torch.ceil(torch.tensor(audio.shape[0] / segment_length)).item())
        
        add_debug_log(f"Splitting {total_duration:.1f}s audio into {segment_count} segments", "info")
        
        for i in range(segment_count):
            start_idx = i * segment_length
            end_idx = min((i + 1) * segment_length, audio.shape[0])
            segment = audio[start_idx:end_idx]
            
            # Only save if segment is at least 1 second
            if segment.shape[0] >= sr:
                output_filename = f"{base_name}_{i}.wav"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save as 16-bit PCM WAV (standard format that Tortoise expects)
                # Audio is already normalized to [-1, 1] range above
                torchaudio.save(output_path, segment.unsqueeze(0), sr)
                processed_files.append(output_filename)
                add_debug_log(f"Saved segment {i+1}/{segment_count}: {segment.shape[0]/sr:.1f}s", "info")
        
        add_debug_log(f"Successfully processed {len(processed_files)} segments", "success")
        
        # Clean up temp WAV file if it was created from WebM
        if audio_path.endswith('_temp.wav') and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                add_debug_log("Cleaned up temporary WAV file", "info")
            except:
                pass  # Ignore cleanup errors
        
        return processed_files
        
    except Exception as e:
        add_debug_log(f"Error processing audio: {str(e)}", "error")
        import traceback
        add_debug_log(traceback.format_exc(), "error")
        
        # Clean up temp WAV file on error too
        if 'audio_path' in locals() and audio_path.endswith('_temp.wav') and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass
        
        raise

def get_available_voices():
    """Get list of available voices from the voices directory"""
    voices_dir = 'tortoise/voices'
    voices = []
    
    if os.path.exists(voices_dir):
        for item in os.listdir(voices_dir):
            item_path = os.path.join(voices_dir, item)
            if os.path.isdir(item_path):
                # Check if directory contains audio files OR conditioning latent files
                files = os.listdir(item_path)
                audio_files = [f for f in files if f.endswith(('.wav', '.mp3', '.flac'))]
                latent_files = [f for f in files if f.endswith('.pth')]
                
                # Voice is ready if it has either audio files OR latent files
                if audio_files or latent_files:
                    voices.append(item)
    
    return sorted(voices)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/voices', methods=['GET'])
def api_voices():
    """Get list of available voices"""
    voices = get_available_voices()
    return jsonify({'voices': voices})

def get_next_filename(voice, preset, candidates):
    """Generate filename with incrementing number"""
    base_name = f"{voice}-{preset}-{candidates}x"
    counter = 1
    while True:
        filename = f"{base_name}-{counter:03d}.wav"
        filepath = MUSIC_FOLDER / filename
        if not filepath.exists():
            return filename, str(filepath)
        counter += 1

@app.route('/api/generate', methods=['POST'])
def api_generate():
    """Generate speech from text"""
    global generation_cancelled, current_generation_thread
    
    try:
        generation_cancelled = False
        data = request.json
        text = data.get('text', '').strip()
        voice = data.get('voice', 'random')
        preset = data.get('preset', 'fast')
        candidates = int(data.get('candidates', 1))
        
        add_debug_log(f"New generation request: voice={voice}, preset={preset}, candidates={candidates}", "info")
        
        if not text:
            add_debug_log("Error: No text provided", "error")
            return jsonify({'error': 'No text provided'}), 400
        
        add_debug_log(f"Text to generate: {text[:100]}...", "info")
        
        # Get TTS instance
        add_debug_log("Initializing TTS engine...", "info")
        tts_instance = get_tts()
        
        # Load voice samples (load_voices handles 'random' properly)
        add_debug_log(f"Loading voice samples for: {voice}", "info")
        voice_samples, conditioning_latents = load_voices([voice])
        
        add_debug_log(f"Starting speech generation (this may take a while)...", "info")
        
        # Check if cancelled before generation
        if generation_cancelled:
            add_debug_log("Generation cancelled by user", "warning")
            return jsonify({'error': 'Generation cancelled'}), 400
        
        # Generate speech with timeout protection
        # Note: k parameter controls how many final outputs to return (best candidates)
        # num_autoregressive_samples is controlled by the preset
        add_debug_log("Starting speech generation...", "info")
        add_debug_log(f"Text length: {len(text)} characters", "info")
        
        # Show expected parameters based on preset
        preset_info = {
            'ultra_fast': ('16 samples', '30 diffusion steps'),
            'fast': ('96 samples', '80 diffusion steps'),
            'standard': ('256 samples', '200 diffusion steps'),
            'high_quality': ('256 samples', '400 diffusion steps')
        }
        if preset in preset_info:
            samples, steps = preset_info[preset]
            num_batches = int(samples.split()[0])//4
            estimated_mins = (num_batches * 20) // 60
            add_debug_log(f"Preset: {preset} → {num_batches} batches (~{estimated_mins}min)", "info")
            
            if preset == 'fast' and estimated_mins > 3:
                add_debug_log("⚠️ TIP: Use 'ultra_fast' for 30sec instead of ~8min", "warning")
        
        add_debug_log("🚀 Generation starting... (check terminal for progress bars)", "info")
        
        # Progress tracker with stage awareness
        import time as time_module
        start_time = time_module.time()
        progress_running = {'active': True, 'stage': 'starting', 'progress': 0}
        
        def progress_updater():
            last_stage = None
            while progress_running['active']:
                time_module.sleep(5)  # Check every 5 seconds
                if not progress_running['active']:
                    break
                    
                elapsed = int(time_module.time() - start_time)
                stage = progress_running['stage']
                
                # Log stage changes
                if stage != last_stage:
                    if stage == 'autoregressive':
                        add_debug_log(f"🎯 Stage 1/2: Generating autoregressive samples... ({elapsed}s)", "info")
                    elif stage == 'diffusion':
                        add_debug_log(f"🎨 Stage 2/2: Diffusion processing... ({elapsed}s)", "info")
                    last_stage = stage
                
                # Periodic updates
                if elapsed % 15 == 0 and elapsed > 0:
                    if stage == 'autoregressive':
                        add_debug_log(f"⏳ Autoregressive: {elapsed}s elapsed...", "info")
                    elif stage == 'diffusion':
                        add_debug_log(f"⏳ Diffusion: {elapsed}s elapsed...", "info")
                    else:
                        add_debug_log(f"⏳ {elapsed}s elapsed...", "info")
                
                # Check if generation was cancelled
                if generation_cancelled:
                    progress_running['active'] = False
                    break
        
        progress_thread = threading.Thread(target=progress_updater, daemon=True)
        progress_thread.start()
        
        try:
            # Check for cancellation before starting
            if generation_cancelled:
                progress_running['active'] = False
                add_debug_log("Generation cancelled before starting", "warning")
                return jsonify({'error': 'Generation cancelled'}), 400
            
            # Stage 1: Autoregressive generation (70% of total time typically)
            progress_running['stage'] = 'autoregressive'
            add_debug_log("Starting autoregressive generation...", "info")
            
            # Run generation with verbose=True for terminal progress bars
            gen = tts_instance.tts_with_preset(
                text, 
                voice_samples=voice_samples, 
                conditioning_latents=conditioning_latents,
                preset=preset,
                k=candidates,
                verbose=True  # Shows progress bars in terminal window
            )
            
            # Stage 2: Diffusion is part of tts_with_preset, but we mark it here
            progress_running['stage'] = 'complete'
            
            # Check if cancelled after generation
            if generation_cancelled:
                progress_running['active'] = False
                add_debug_log("Generation cancelled after completion", "warning")
                return jsonify({'error': 'Generation cancelled'}), 400
            
            progress_running['active'] = False
            elapsed = int(time_module.time() - start_time)
            add_debug_log(f"✅ Done in {elapsed//60}m {elapsed%60}s!", "success")
        except KeyboardInterrupt:
            add_debug_log("Generation interrupted", "warning")
            raise
        except RuntimeError as e:
            if "out of memory" in str(e).lower():
                add_debug_log("CUDA Out of Memory! Try:", "error")
                add_debug_log("1. Use 'fast' or 'ultra_fast' preset", "warning")
                add_debug_log("2. Reduce candidates to 1", "warning")
                add_debug_log("3. Close other GPU applications", "warning")
                add_debug_log("4. Restart the service", "warning")
            raise
        
        # Check if cancelled after generation
        if generation_cancelled:
            add_debug_log("Generation cancelled by user", "warning")
            return jsonify({'error': 'Generation cancelled'}), 400
        
        add_debug_log("Speech generation completed!", "success")
        add_debug_log(f"Output tensor shape: {gen.shape}", "info")
        
        # Handle different tensor shapes
        # Shape can be (k, 1, samples) for multiple candidates or (1, samples) for single
        if len(gen.shape) == 3:
            # Multiple candidates: (k, 1, samples) - take first (best)
            gen = gen[0]
        
        # Ensure we have (channels, samples) shape for torchaudio.save
        # gen is now either (1, samples) or could be (samples,)
        if len(gen.shape) == 1:
            gen = gen.unsqueeze(0)  # Add channel dimension: (samples,) -> (1, samples)
        
        add_debug_log(f"Final tensor shape for saving: {gen.shape}", "info")
        
        # Generate filename and save to Music folder
        filename, filepath = get_next_filename(voice, preset, candidates)
        add_debug_log(f"Saving audio to: {filename}", "info")
        torchaudio.save(filepath, gen.cpu(), 24000)
        add_debug_log(f"File saved successfully: {filepath}", "success")
        
        # Also convert to base64 for immediate playback
        audio_buffer = io.BytesIO()
        torchaudio.save(audio_buffer, gen.cpu(), 24000, format='wav')
        audio_buffer.seek(0)
        audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'audio': audio_base64,
            'filename': filename,
            'filepath': filepath,
            'message': f'Audio generated and saved to {filename}'
        })
        
    except Exception as e:
        if generation_cancelled:
            add_debug_log("Generation cancelled by user", "warning")
            return jsonify({'error': 'Generation cancelled by user'}), 400
        
        error_msg = str(e)
        add_debug_log(f"ERROR generating speech: {error_msg}", "error")
        
        import traceback
        tb = traceback.format_exc()
        add_debug_log(f"Traceback:\n{tb}", "error")
        
        return jsonify({'error': error_msg}), 500
    finally:
        current_generation_thread = None

@app.route('/api/upload_voice', methods=['POST'])
def api_upload_voice():
    """Upload custom voice samples with automatic preprocessing for cloning"""
    try:
        voice_name = request.form.get('voice_name', '').strip()
        
        add_debug_log(f"Voice upload request: {voice_name}", "info")
        
        if not voice_name:
            add_debug_log("Error: Voice name is required", "error")
            return jsonify({'error': 'Voice name is required'}), 400
        
        # Sanitize voice name
        voice_name = secure_filename(voice_name)
        voice_dir = os.path.join(app.config['UPLOAD_FOLDER'], voice_name)
        
        # Create directory if it doesn't exist
        os.makedirs(voice_dir, exist_ok=True)
        add_debug_log(f"Created voice directory: {voice_dir}", "info")
        
        # Save uploaded files
        files = request.files.getlist('audio_files')
        
        if not files or len(files) == 0:
            add_debug_log("Error: No audio files provided", "error")
            return jsonify({'error': 'No audio files provided'}), 400
        
        # Create temp directory for original uploads
        temp_dir = os.path.join(voice_dir, '_temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        all_processed_files = []
        file_counter = 0
        
        add_debug_log("🎙️ Starting audio preprocessing for voice cloning...", "info")
        add_debug_log("Converting to: 22050Hz, float32 WAV, 10s segments", "info")
        
        for file in files:
            if file and file.filename:
                original_filename = secure_filename(file.filename)
                if original_filename.endswith(('.wav', '.mp3', '.flac', '.ogg', '.m4a')):
                    # Save to temp location first
                    temp_filepath = os.path.join(temp_dir, original_filename)
                    file.save(temp_filepath)
                    add_debug_log(f"Processing: {original_filename}", "info")
                    
                    try:
                        # Process audio: split, resample, convert to float32 WAV
                        base_name = f"clip_{file_counter:02d}"
                        processed = process_audio_for_cloning(temp_filepath, voice_dir, base_name)
                        all_processed_files.extend(processed)
                        file_counter += 1
                    except Exception as e:
                        add_debug_log(f"Failed to process {original_filename}: {str(e)}", "error")
                        continue
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir)
        
        if not all_processed_files:
            add_debug_log("Error: No valid audio files could be processed", "error")
            return jsonify({'error': 'No valid audio files could be processed'}), 400
        
        segment_count = len(all_processed_files)
        
        # Check if we have at least 7 segments (recommended minimum)
        if segment_count < 7:
            add_debug_log(f"⚠️ Warning: Only {segment_count} segments created", "warning")
            add_debug_log("Recommendation: Provide more audio (at least 70 seconds total)", "warning")
            if segment_count < 5:
                add_debug_log("⚠️ CRITICAL: Less than 5 segments - cloning quality will be poor!", "error")
        else:
            add_debug_log(f"✅ Created {segment_count} segments - good for cloning!", "success")
        
        add_debug_log(f"Voice '{voice_name}' ready for cloning", "success")
        
        # Automatically generate .pth file for instant loading
        add_debug_log("", "info")  # Blank line for readability
        add_debug_log("🔄 Automatically generating .pth file...", "info")
        add_debug_log("💡 NOTE: If voice quality is poor, delete the .pth file and try without it", "warning")
        add_debug_log("   Tortoise will load audio files directly (slower but may work better)", "warning")
        
        pth_success = generate_conditioning_latents(voice_name)
        
        if pth_success:
            pth_message = "Voice ready! .pth file created for instant loading."
        else:
            pth_message = "Voice segments created. .pth generation failed (see logs)."
            add_debug_log("💡 You can manually generate .pth later if needed", "warning")
        
        # Determine recommendation message
        if segment_count < 5:
            recommendation = 'Critical: Need at least 5 segments (50+ seconds)'
        elif segment_count < 7:
            recommendation = 'Warning: Recommended 7+ segments (70+ seconds)'
        else:
            recommendation = 'Good for cloning!'
        
        return jsonify({
            'success': True,
            'message': f'Processed {segment_count} audio segments for voice "{voice_name}"',
            'files': all_processed_files,
            'segment_count': segment_count,
            'pth_generated': pth_success,
            'recommendation': recommendation,
            'status': pth_message
        })
        
    except Exception as e:
        error_msg = str(e)
        add_debug_log(f"Error uploading voice: {error_msg}", "error")
        
        import traceback
        tb = traceback.format_exc()
        add_debug_log(f"Traceback:\n{tb}", "error")
        
        return jsonify({'error': error_msg}), 500

@app.route('/api/delete_voice/<voice_name>', methods=['DELETE'])
def api_delete_voice(voice_name):
    """Delete a custom voice"""
    try:
        voice_name = secure_filename(voice_name)
        voice_dir = os.path.join(app.config['UPLOAD_FOLDER'], voice_name)
        
        # Don't allow deletion of built-in voices (basic protection)
        built_in_voices = ['angie', 'daniel', 'deniro', 'emma', 'freeman', 
                          'geralt', 'halle', 'jlaw', 'lj', 'mol', 'tom', 'william']
        
        if voice_name in built_in_voices:
            return jsonify({'error': 'Cannot delete built-in voices'}), 403
        
        if os.path.exists(voice_dir):
            import shutil
            shutil.rmtree(voice_dir)
            return jsonify({'success': True, 'message': f'Voice "{voice_name}" deleted'})
        else:
            return jsonify({'error': 'Voice not found'}), 404
            
    except Exception as e:
        print(f"Error deleting voice: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recording/paragraph', methods=['GET'])
def api_get_recording_paragraph():
    """Get a random paragraph for voice recording"""
    import random
    
    paragraphs = [
        "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet and is commonly used for testing fonts and keyboards.",
        "In the heart of the city, where neon lights dance against the night sky, stories unfold with every passing moment. Each corner holds a memory, each street a tale waiting to be told.",
        "Technology has transformed the way we communicate, bringing distant voices closer and making the world feel smaller. Yet the warmth of human connection remains irreplaceable.",
        "Nature's beauty lies not just in grand mountains and vast oceans, but in the delicate patterns of a single leaf and the gentle rustling of trees in the breeze.",
        "Every journey begins with a single step, they say. But it's the courage to take that step, despite uncertainty, that defines our adventures and shapes our destinies.",
        "Music transcends language barriers, speaking directly to the soul. A melody can evoke memories long forgotten, emotions deeply buried, and dreams yet to be realized.",
        "The art of cooking is more than following recipes. It's about understanding flavors, embracing creativity, and sharing love through every dish we prepare for others.",
        "Books are gateways to infinite worlds, allowing us to live countless lives, explore distant lands, and understand perspectives vastly different from our own.",
        "Laughter is universal, cutting through tension and bringing people together. A genuine smile can brighten someone's day and create connections that last a lifetime.",
        "Time flows like a river, constant yet ever-changing. We cannot step into the same moment twice, which makes each present instant both precious and fleeting.",
        "Dreams fuel innovation and inspire progress. What seems impossible today becomes tomorrow's reality through determination, creativity, and unwavering belief.",
        "The ocean's depths remain largely unexplored, holding mysteries and wonders beyond our imagination. Each dive reveals creatures and ecosystems more alien than science fiction.",
        "Friendship is a garden that requires care and attention. Trust must be nurtured, communication maintained, and support offered freely to help each other grow.",
        "Morning coffee rituals ground us in routine while offering quiet moments of reflection. That first sip awakens not just the body but the mind's readiness for the day ahead.",
        "Photography freezes time, capturing emotions and moments that would otherwise fade. Through a lens, ordinary scenes become extraordinary stories worth preserving forever."
    ]
    
    paragraph = random.choice(paragraphs)
    return jsonify({'paragraph': paragraph})

@app.route('/api/recording/upload', methods=['POST'])
def api_recording_upload():
    """Upload recorded audio clips"""
    try:
        voice_name = request.form.get('voice_name', '').strip()
        
        if not voice_name:
            return jsonify({'error': 'Voice name is required'}), 400
        
        # Sanitize voice name
        voice_name = secure_filename(voice_name)
        voice_dir = os.path.join(app.config['UPLOAD_FOLDER'], voice_name)
        os.makedirs(voice_dir, exist_ok=True)
        
        # Create temp directory
        temp_dir = os.path.join(voice_dir, '_temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Get all recorded audio blobs
        recorded_files = request.files.getlist('recordings')
        
        if not recorded_files:
            return jsonify({'error': 'No recordings provided'}), 400
        
        add_debug_log(f"🎙️ Processing {len(recorded_files)} recorded clips for voice '{voice_name}'...", "info")
        add_debug_log("Converting to: 22050Hz, float32 WAV, 10s segments", "info")
        
        all_processed_files = []
        
        for idx, audio_file in enumerate(recorded_files):
            if audio_file and audio_file.filename:
                # Save recording to temp
                temp_filepath = os.path.join(temp_dir, f'recording_{idx}.webm')
                audio_file.save(temp_filepath)
                
                try:
                    # Process the recording
                    base_name = f"rec_{idx:02d}"
                    processed = process_audio_for_cloning(temp_filepath, voice_dir, base_name)
                    all_processed_files.extend(processed)
                    add_debug_log(f"Processed recording {idx + 1}/{len(recorded_files)}", "info")
                except Exception as e:
                    add_debug_log(f"Failed to process recording {idx + 1}: {str(e)}", "error")
                    continue
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(temp_dir)
        
        if not all_processed_files:
            return jsonify({'error': 'No valid recordings could be processed'}), 400
        
        segment_count = len(all_processed_files)
        
        # Check segment count
        if segment_count < 7:
            add_debug_log(f"⚠️ Warning: Only {segment_count} segments from recordings", "warning")
            add_debug_log("Recommendation: Record more clips (at least 7 total)", "warning")
            if segment_count < 5:
                add_debug_log("⚠️ CRITICAL: Less than 5 segments - cloning quality will be poor!", "error")
        else:
            add_debug_log(f"✅ Created {segment_count} segments from recordings - good for cloning!", "success")
        
        # Automatically generate .pth file
        add_debug_log("", "info")
        add_debug_log("🔄 Automatically generating .pth file...", "info")
        
        pth_success = generate_conditioning_latents(voice_name)
        
        if pth_success:
            pth_message = "Voice ready! .pth file created for instant loading."
        else:
            pth_message = "Voice segments created. .pth generation failed (see logs)."
        
        # Determine recommendation
        if segment_count < 5:
            recommendation = 'Critical: Need at least 5 segments (record more clips)'
        elif segment_count < 7:
            recommendation = 'Warning: Recommended 7+ segments (record more clips)'
        else:
            recommendation = 'Good for cloning!'
        
        return jsonify({
            'success': True,
            'message': f'Processed {segment_count} segments from {len(recorded_files)} recordings',
            'files': all_processed_files,
            'segment_count': segment_count,
            'pth_generated': pth_success,
            'recommendation': recommendation,
            'status': pth_message
        })
        
    except Exception as e:
        add_debug_log(f"Error processing recordings: {str(e)}", "error")
        import traceback
        add_debug_log(traceback.format_exc(), "error")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cancel', methods=['POST'])
def api_cancel():
    """Cancel ongoing generation"""
    global generation_cancelled
    generation_cancelled = True
    add_debug_log("Generation cancellation requested by user", "warning")
    return jsonify({'success': True, 'message': 'Generation cancellation requested'})

@app.route('/api/debug/logs', methods=['GET'])
def api_get_debug_logs():
    """Get debug logs"""
    return jsonify({'logs': debug_logs})

@app.route('/api/debug/clear', methods=['POST'])
def api_clear_debug_logs():
    """Clear debug logs"""
    global debug_logs
    debug_logs = []
    add_debug_log("Debug logs cleared", "info")
    return jsonify({'success': True, 'message': 'Logs cleared'})

@app.route('/api/debug/test', methods=['POST'])
def api_test_debug():
    """Test debug logging"""
    add_debug_log("🧪 Test message: Debug system is working!", "success")
    add_debug_log("This is an info message", "info")
    add_debug_log("This is a warning message", "warning")
    add_debug_log("This is an error message", "error")
    return jsonify({'success': True, 'message': 'Test logs added'})

@app.route('/api/open_output_folder', methods=['POST'])
def api_open_output_folder():
    """Open output folder in Windows Explorer"""
    try:
        subprocess.Popen(f'explorer "{MUSIC_FOLDER}"')
        return jsonify({'success': True, 'message': 'Opening output folder'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/service/status', methods=['GET'])
def api_service_status():
    """Get service status"""
    import psutil
    
    # Get system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        gpu_info = "N/A"
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            gpu_memory_allocated = torch.cuda.memory_allocated(0) / (1024**3)
            gpu_memory_cached = torch.cuda.memory_reserved(0) / (1024**3)
            gpu_info = {
                'total_gb': round(gpu_memory, 2),
                'allocated_gb': round(gpu_memory_allocated, 2),
                'cached_gb': round(gpu_memory_cached, 2),
                'free_gb': round(gpu_memory - gpu_memory_cached, 2)
            }
    except:
        cpu_percent = 0
        memory_percent = 0
        memory_available_gb = 0
        gpu_info = "N/A"
    
    return jsonify({
        'running': True,
        'output_folder': str(MUSIC_FOLDER),
        'system': {
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_available_gb': round(memory_available_gb, 2),
            'gpu_info': gpu_info
        }
    })

@app.route('/api/service/stop', methods=['POST'])
def api_service_stop():
    """Stop the service"""
    def shutdown():
        time.sleep(1)
        os._exit(0)
    
    threading.Thread(target=shutdown).start()
    return jsonify({'success': True, 'message': 'Service stopping...'})

@app.route('/api/service/restart', methods=['POST'])
def api_service_restart():
    """Restart the service"""
    def restart():
        time.sleep(1)
        python = sys.executable
        os.execl(python, python, *sys.argv)
    
    threading.Thread(target=restart).start()
    return jsonify({'success': True, 'message': 'Service restarting...'})

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    add_debug_log("Starting Tortoise TTS Web UI...", "info")
    add_debug_log(f"Output folder: {MUSIC_FOLDER}", "info")
    add_debug_log("Server starting on http://localhost:5000", "info")
    add_debug_log("Note: First generation will take time as models load", "info")
    
    print("Starting Tortoise TTS Web UI...")
    print("Open http://localhost:5000 in your browser")
    print(f"Output folder: {MUSIC_FOLDER}")
    print("\nNote: First generation will take time as models load...")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
