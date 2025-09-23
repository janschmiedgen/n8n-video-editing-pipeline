# Video Rendering Script Usage Guide

## 02_render-captions-and-layout-into-video.sh

Professional video rendering script for the n8n pipeline that applies brand overlays, captions, and format conversions with blurred backgrounds.

---

## Basic Syntax

```bash
./functions/02_render-captions-and-layout-into-video.sh [PARAMETERS]
```

---

## All Available Parameters

| Parameter | Required | Type | Description | Example Values |
|-----------|----------|------|-------------|----------------|
| `-inputvideo` | **✅ Required** | File path | Path to input video file | `/path/to/video.mp4`, `video.MOV` |
| `-version` | **✅ Required** | String | Output video format | `portrait`, `landscape`, `square` |
| `-logo` | Optional | Filename | Logo overlay file (from overlay-files/) | `codify-logo.png`, `my-logo.jpg` |
| `-icon` | Optional | Filename | Icon overlay file (from overlay-files/) | `codify-icon.png`, `my-icon.svg` |
| `-socialmediahandle` | Optional | Filename | Social media handle image (from overlay-files/) | `codify-sm-handle.png`, `@handle.png` |
| `-captions` | Optional | Boolean | Enable/disable captions | `true` (default), `false` |
| `-h` or `--help` | Optional | Flag | Show help message | N/A |

---

## Usage Examples

### 1. Full Example with All Overlays
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "/opt/n8n_scripts/video/_input-files/my-video.mp4" \
  -logo "codify-logo.png" \
  -icon "codify-icon.png" \
  -socialmediahandle "codify-sm-handle.png" \
  -captions true \
  -version landscape
```

### 2. Minimal Example (Required Parameters Only)
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "my-video.mp4" \
  -version portrait
```

### 3. Video with Logo Only
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "video.MOV" \
  -logo "my-logo.png" \
  -captions true \
  -version square
```

### 4. Video without Captions
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "video.mp4" \
  -logo "logo.png" \
  -icon "icon.png" \
  -captions false \
  -version landscape
```

---

## Available Output Formats

| Format | Resolution | Aspect Ratio | Use Case |
|--------|------------|--------------|----------|
| `portrait` | 1080x1920 | 9:16 | Instagram Stories, TikTok, YouTube Shorts |
| `landscape` | 1920x1080 | 16:9 | YouTube, LinkedIn, desktop viewing |
| `square` | 1080x1080 | 1:1 | Instagram posts, Facebook |

---

## File Locations

### Overlay Files Location
All overlay files must be placed in:
```
/opt/n8n_scripts/video/n8n-video-processing-pipeline/overlay-files/
```

**Current available overlay files:**
- `codify-logo.png`
- `codify-icon.png` 
- `codify-sm-handle.png`

### Input Files Location
```
/opt/n8n_scripts/video/_input-files/
```

### Output Files Location
Generated videos are saved to:
```
/opt/n8n_scripts/video/_output-files/
```

**Naming pattern:** `{input_name}_{version}_{ratio}.mp4`

---

## Auto-Features

### 🔄 Rotation Detection
- Automatically handles iPhone -90° rotation metadata
- Correctly interprets portrait videos recorded on iPhone

### 🎨 Blurred Backgrounds
- Creates professional backgrounds for aspect ratio mismatches
- No more ugly black bars - uses blurred video background instead

### 📝 Format-Specific ASS Captions
- Automatically selects the right caption file based on output format:
  - Portrait output → `{video}_captions_portrait.ass`
  - Landscape output → `{video}_captions_landscape.ass` 
  - Square output → `{video}_captions_square.ass`

### 🎭 Opacity Control
- Applies transparency settings from config files
- Different opacity values per format for optimal visibility

---

## Overlay Size Configuration

Current overlay sizes (optimized):

| Format | Logo Size | Icon Size | Notes |
|--------|-----------|-----------|--------|
| **Portrait** | 0.164583 | 0.0564 | Logo 1/4 smaller, Icon 1/5 bigger |
| **Landscape** | 0.082291 | 0.05 | Logo 1/3 smaller |
| **Square** | 0.131666 | 0.0564 | Logo 2/5 smaller, Icon 1/5 bigger |

---

## Working Examples

### iPhone Portrait Video → Landscape Output
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "/opt/n8n_scripts/video/_input-files/testvideo-portrait.MOV" \
  -logo "codify-logo.png" \
  -icon "codify-icon.png" \
  -socialmediahandle "codify-sm-handle.png" \
  -captions true \
  -version landscape
```

### Square Video → Portrait Output (Logo Only)
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "/opt/n8n_scripts/video/_input-files/testvideo-square.mov" \
  -logo "codify-logo.png" \
  -captions true \
  -version portrait
```

### Landscape Video → Square Output (All Overlays)
```bash
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "/opt/n8n_scripts/video/_input-files/testvideo-landscape.MOV" \
  -logo "codify-logo.png" \
  -icon "codify-icon.png" \
  -socialmediahandle "codify-sm-handle.png" \
  -captions true \
  -version square
```

---

## Prerequisites

### Required ASS Caption Files
Before rendering, generate format-specific ASS files using:
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "your-video.mp4" \
  -style karaoke \
  -brand codify
```

This generates 3 ASS files automatically:
- `{video}_captions_portrait.ass`
- `{video}_captions_landscape.ass`
- `{video}_captions_square.ass`

### Required Overlay Files
Ensure your overlay files are in PNG format with transparent backgrounds for best results.

---

## Error Handling

The script includes comprehensive error handling:
- ✅ Validates all required parameters
- ✅ Checks file existence before processing
- ✅ Provides fallback for missing format-specific ASS files
- ✅ Logs all operations for debugging
- ✅ Returns clear SUCCESS/ERROR status codes

---

## Output Quality

- **Video codec:** H.264 (libx264)
- **Quality:** CRF 22 (high quality)
- **Audio:** AAC 160kbps, 48kHz
- **Encoding preset:** Medium (balanced speed/quality)
- **Optimization:** Fast start enabled for web playback

---

## Performance

- **Typical processing time:** 30-60 seconds per video
- **CPU usage:** Moderate (uses medium preset)
- **Memory usage:** Low to moderate
- **Disk space:** ~2-8MB per output video (varies by content)

---

*Last updated: September 2025*
*Part of the n8n video processing pipeline*