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
    """Upload custom voice samples"""
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
        
        saved_files = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                if filename.endswith(('.wav', '.mp3', '.flac', '.ogg')):
                    filepath = os.path.join(voice_dir, filename)
                    file.save(filepath)
                    saved_files.append(filename)
                    add_debug_log(f"Saved file: {filename}", "info")
        
        if not saved_files:
            add_debug_log("Error: No valid audio files uploaded", "error")
            return jsonify({'error': 'No valid audio files uploaded'}), 400
        
        add_debug_log(f"Successfully uploaded {len(saved_files)} files for voice '{voice_name}'", "success")
        
        return jsonify({
            'success': True,
            'message': f'Uploaded {len(saved_files)} files for voice "{voice_name}"',
            'files': saved_files
        })
        
    except Exception as e:
        error_msg = str(e)
        add_debug_log(f"Error uploading voice: {error_msg}", "error")
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
