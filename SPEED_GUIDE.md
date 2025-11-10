# TORTOISE TTS SPEED GUIDE

## TL;DR - It's SLOW, This is Normal!

**Tortoise TTS is 10-100x slower than Stable Diffusion.** This is by design.

## Why So Slow?

Unlike Stable Diffusion which generates images in parallel, Tortoise TTS:
1. **Generates audio token-by-token** (like GPT text generation)
2. **Runs 3 separate neural networks in sequence**
3. **Each batch processes only 4 samples at a time** (for stability)

## Real-World Timings (RTX 3060):

### Two Lines of Text (~20 words):

| Preset | Batches | Time | Quality |
|--------|---------|------|---------|
| **ultra_fast** | 4 batches | **30 seconds** ⚡ | Usable, robotic |
| **fast** | 24 batches | **8 minutes** 🐌 | Good quality |
| **standard** | 64 batches | **20 minutes** 🐢 | Great quality |
| **high_quality** | 64 batches + 400 diffusion | **40 minutes** 🦥 | Best quality |

### Each Batch Takes:
- **~18-20 seconds** on RTX 3060
- **~10-15 seconds** on RTX 4090
- **~30-40 seconds** on RTX 3050

## Speed Comparison with Stable Diffusion:

```
Stable Diffusion 1.5 (512x512, 20 steps):
├─ RTX 3060: ~5 seconds ⚡⚡⚡

Tortoise TTS "ultra_fast" (2 sentences):
├─ RTX 3060: ~30 seconds ⚡⚡

Tortoise TTS "fast" (2 sentences):
├─ RTX 3060: ~8 minutes ⚡

Tortoise TTS "standard" (2 sentences):
├─ RTX 3060: ~20 minutes 🐌
```

**Tortoise is 100x slower than Stable Diffusion for similar quality.**

## How to Speed Up:

### 1. Use Ultra Fast Preset (Most Important!)
Change from "fast" to "ultra_fast":
- **Before**: 24 batches × 20s = 8 minutes
- **After**: 4 batches × 20s = 80 seconds
- **Speedup**: 6x faster

### 2. Keep Candidates at 1
- Candidates=1: Run once
- Candidates=2: Run twice (2x slower)
- Candidates=4: Run four times (4x slower)

### 3. Use Shorter Text
- 1 sentence: ~30-60 seconds (ultra_fast)
- 2 sentences: ~60-90 seconds (ultra_fast)
- 1 paragraph: ~2-3 minutes (ultra_fast)

### 4. Increase Batch Size (If You Have VRAM)
If you have 12GB+ VRAM and it's not freezing:
```python
# In web_ui.py line 62:
tts = TextToSpeech(autoregressive_batch_size=8)  # Instead of 4
```
- **Before**: 24 batches × 20s = 8 minutes
- **After**: 12 batches × 25s = 5 minutes
- **Risk**: May cause system freezing

## Why Is Tortoise This Slow?

### Architecture Comparison:

**Stable Diffusion:**
```
1. Text → CLIP embeddings (instant)
2. Diffusion denoising (parallel, 20-50 steps)
Total: 5-30 seconds
```

**Tortoise TTS:**
```
1. Text → Token IDs (instant)
2. Autoregressive model (sequential, 96-256 samples) ← 80% OF TIME
   ├─ Each sample: Generate mel-spectrogram tokens one-by-one
   ├─ Cannot parallelize (like GPT text generation)
   └─ Batch size limited by VRAM (4-16 samples)
3. CLVP ranking (rank all 96-256 samples) ← 5% OF TIME
4. Diffusion vocoder (parallel, 30-400 steps) ← 15% OF TIME
Total: 30 seconds to 40 minutes
```

### The Bottleneck:
The **autoregressive model** is like GPT for audio:
- Generates one mel-spectrogram token at a time
- Must wait for previous token before generating next
- Cannot be parallelized like image diffusion
- Needs to run 96-256 times to get quality results

## Alternative Faster TTS Models:

If speed is critical, consider:

| Model | Speed | Quality | Notes |
|-------|-------|---------|-------|
| **Coqui XTTS** | ~1-2 sec | Good | Faster autoregressive |
| **Bark** | ~5-10 sec | Good | Transformer-based |
| **StyleTTS2** | ~1-3 sec | Great | Diffusion-only (no AR) |
| **Tortoise TTS** | 30s-40min | Excellent | Best quality, slowest |

## Your Current Situation:

You're using **"fast" preset** which is misleadingly named:
- **Actual time**: 5-10 minutes
- **Should be called**: "balanced" or "medium"

For your RTX 3060, the "fast" preset does:
- 96 samples ÷ 4 batch_size = **24 batches**
- 24 batches × 20 seconds = **8 minutes** (480 seconds)
- Plus CLVP + diffusion = **8-10 minutes total**

## Recommendation:

**Use "ultra_fast" for testing/iteration:**
- 4 batches × 20s = 80 seconds
- Quality is acceptable for most use cases
- 6x faster than "fast"

**Use "fast" for final output:**
- 24 batches × 20s = 8 minutes
- Better quality, worth the wait for final results

**Never use "standard" or "high_quality" unless:**
- You're generating final production audio
- You can leave it running overnight
- You don't mind 20-40 minute generations

## Bottom Line:

**Yes, this is normal.** Tortoise TTS is designed for **quality over speed**. If you need fast TTS, you need a different model. If you want the best quality voice cloning, Tortoise is worth the wait - but expect 5-40 minutes per generation, not 5-40 seconds like Stable Diffusion.
