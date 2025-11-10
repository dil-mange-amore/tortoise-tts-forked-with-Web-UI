# HOW TO MONITOR GENERATION PROGRESS

## The Problem
When using the web UI, generation appears to "freeze" at 0% because progress bars don't show in the browser.

## The Solution
**Generation IS working** - you just need to look in the right place!

## Where to See Progress:

### 1. Terminal Window (Best for Progress)
- Open the PowerShell/CMD window where you ran `start_webui.bat`
- You'll see real-time progress bars like:
  ```
  Generating autoregressive samples..
  100%|████████████| 24/24 [00:12<00:00,  1.95it/s]
  
  Computing best candidates using CLVP
  100%|████████████| 24/24 [00:01<00:00, 15.23it/s]
  
  Transforming autoregressive outputs into audio..
  100%|████████████| 80/80 [00:02<00:00, 35.67it/s]
  ```

### 2. Browser Debug Console (Heartbeat)
- Click the 🐛 button in the web UI
- You'll see messages every 5 seconds:
  ```
  17:06:39 [INFO] Starting generation now...
  17:06:44 [INFO] ⏳ Still working... 5s elapsed (heartbeat #1)
  17:06:49 [INFO] ⏳ Still working... 10s elapsed (heartbeat #2)
  17:06:54 [INFO] ⏳ Still working... 15s elapsed (heartbeat #3)
  17:07:02 [SUCCESS] ✅ Generation complete! Took 23.4 seconds
  ```

### 3. Music Folder (Final Result)
- Generation saves immediately upon completion
- Check: `C:\Users\YourName\Music\Tortoise Output`
- Files appear as: `angie-fast-1x-001.wav`

## Expected Times:

### Ultra Fast Preset
- **Time**: 10-30 seconds
- **Batches**: 4 (with batch_size=4)
- **Use for**: Testing, quick results

### Fast Preset (Recommended)
- **Time**: 30-90 seconds  
- **Batches**: 24 (with batch_size=4)
- **Use for**: Good quality, reasonable speed

### Standard Preset
- **Time**: 2-5 minutes
- **Batches**: 64 (with batch_size=4)
- **Use for**: Better quality

### High Quality Preset
- **Time**: 5-15 minutes
- **Batches**: 64 (with batch_size=4)  
- **Diffusion**: 400 steps instead of 80-200
- **Use for**: Best possible output

## Tips:

1. **First generation is slowest** - Models need to warm up (add 2-5 min)
2. **Keep terminal window visible** - That's where progress shows
3. **Watch for heartbeats** - Proves generation isn't frozen
4. **Be patient with "fast" preset** - 60-90 seconds is normal
5. **Check Music folder** - File appears when done

## If It Really IS Stuck:

Signs of actual freezing (not just slow progress):
- ❌ No heartbeat messages for 60+ seconds
- ❌ No terminal output for 60+ seconds  
- ❌ Task Manager shows 0% GPU usage
- ❌ Python process not responding

If truly stuck:
1. Click "Cancel" button
2. Try "Ultra Fast" preset with 1 candidate
3. Use shorter text (1-2 sentences)
4. Restart the web service
