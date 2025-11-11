## Changelog
#### v3.0.1-webui; 2025/11/11
- **Added comprehensive web UI for Tortoise TTS**
  - Flask-based web interface with 4-column responsive layout
  - Real-time debug console with error copying functionality
  - Text-to-speech generation with live audio playback
  - Custom voice upload with automatic preprocessing
  - Browser-based voice recording with random paragraph prompts
  - Automatic audio normalization and DC offset removal
  - Voice management (upload, delete, view)
  - Generation progress tracking with stage awareness
  - Playlist functionality with persistent storage
  - Service controls (start, stop, restart)
  - Output folder management (auto-save to Music folder)
  - Smart filename generation with incrementing counters
- **Voice cloning improvements**
  - Automatic .pth file generation for instant voice loading
  - Audio preprocessing: 22050Hz resampling, mono conversion, 10s segmentation
  - DC offset removal and [-1, 1] normalization
  - WebM format support via FFmpeg integration
  - Fixed CUDA/CPU device mismatch bug in conditioning latents
  - Proper audio quality validation and diagnostics
- **Performance optimizations**
  - Reduced batch size to 4 for system stability
  - CUDA out-of-memory error handling
  - Lazy model loading
  - Stage-based progress monitoring
- **Package compatibility fixes**
  - NumPy 1.23.5 for Python 3.11 compatibility
  - Removed incompatible numba/llvmlite, then reinstalled for librosa
  - Fixed scipy compatibility warnings
- **Documentation**
  - Added START_WEB_UI.bat launcher script
  - Comprehensive troubleshooting guides
  - Voice cloning quality recommendations

#### v3.0.0; 2023/10/18
- Added fast inference for tortoise with HiFi Decoder (inspired by xtts by [coquiTTS](https://github.com/coqui-ai/TTS) 🐸, check out their multilingual model for noncommercial uses)
#### v2.8.0; 2023/9/13
- Added custom tokenizer for non-english models
#### v2.7.0; 2023/7/26
- Bug fixes
- Added Apple Silicon Support
- Updated Transformer version
#### v2.6.0; 2023/7/26
- Bug fixes

#### v2.5.0; 2023/7/09
- Added kv_cache support 5x faster
- Added deepspeed support 10x faster
- Added half precision support
  
#### v2.4.0; 2022/5/17
- Removed CVVP model. Found that it does not, in fact, make an appreciable difference in the output.
- Add better debugging support; existing tools now spit out debug files which can be used to reproduce bad runs.

#### v2.3.0; 2022/5/12
- New CLVP-large model for further improved decoding guidance.
- Improvements to read.py and do_tts.py (new options)

#### v2.2.0; 2022/5/5
- Added several new voices from the training set.
- Automated redaction. Wrap the text you want to use to prompt the model but not be spoken in brackets.
- Bug fixes

#### v2.1.0; 2022/5/2
- Added ability to produce totally random voices.
- Added ability to download voice conditioning latent via a script, and then use a user-provided conditioning latent.
- Added ability to use your own pretrained models.
- Refactored directory structures.
- Performance improvements & bug fixes.
