# Video Transcription Script Usage Guide

## 01_transcribe-video-to-ass-with-super-whisper.py

Advanced transcription script for the n8n pipeline that generates format-specific ASS caption files using faster-whisper with support for multiple styles and brands.

---

## Basic Syntax

```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py [PARAMETERS]
```

---

## All Available Parameters

| Parameter | Required | Type | Description | Example Values |
|-----------|----------|------|-------------|----------------|
| `-inputfile` | **✅ Required** | File path | Path to input video file | `/path/to/video.mp4`, `video.MOV` |
| `-style` | **✅ Required** | String | Caption style from template | `clean`, `social`, `karaoke`, `highlight` |
| `-template` | Optional | Filename | Specific ASS template file | `landscape_fancy.ass`, `portrait_codify.ass` |
| `-brand` | Optional | String | Brand theme for auto-selection | `codify` (default), `fancy` |
| `-h` or `--help` | Optional | Flag | Show help message | N/A |

---

## Usage Examples

### 1. Auto-Select Template with Default Brand (Codify)
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "video.mp4" \
  -style clean
```

### 2. Auto-Select with Specific Brand
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "/opt/n8n_scripts/video/_input-files/my-video.MOV" \
  -style karaoke \
  -brand fancy
```

### 3. Manual Template Selection
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "video.mp4" \
  -template "landscape_fancy.ass" \
  -style social
```

### 4. iPhone Portrait Video with Karaoke Style
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "/opt/n8n_scripts/video/_input-files/testvideo-portrait.MOV" \
  -style karaoke \
  -brand codify
```

---

## Available Caption Styles

| Style | Description | Features | Best For |
|-------|-------------|----------|----------|
| `clean` | Readable, minimalist | Simple text, good contrast | Professional videos, tutorials |
| `social` | Bold, attention-grabbing | Strong shadows, high impact | Social media content |
| `karaoke` | Word-by-word highlighting | Dynamic color changes, timing effects | Engagement, sing-alongs |
| `highlight` | Maximum emphasis | Extra bold, bright colors | Key moments, announcements |

---

## Available Brands

| Brand | Description | Style Theme | Template Files |
|-------|-------------|-------------|----------------|
| `codify` | Professional, clean | Business-focused styling | `portrait_codify.ass`, `landscape_codify.ass`, `square_codify.ass` |
| `fancy` | Creative, vibrant | Social media focused | `portrait_fancy.ass`, `landscape_fancy.ass`, `square_fancy.ass` |

---

## Template Auto-Selection

The script automatically selects the appropriate template based on:

1. **Video aspect ratio detection** (with rotation support)
2. **Brand selection** 
3. **Format-specific templates**

### Detection Logic:
- **Portrait** (aspect ratio < 0.8): Uses portrait templates
- **Landscape** (aspect ratio > 1.3): Uses landscape templates  
- **Square** (aspect ratio 0.8-1.3): Uses square templates

### iPhone Rotation Support:
- ✅ Automatically detects -90° rotation metadata
- ✅ Correctly interprets effective dimensions
- ✅ Selects appropriate template based on viewed orientation

---

## Output Files Generated

### Multi-Format ASS Files (NEW!)
**The script now generates 3 ASS files automatically:**

```
{video_name}_captions_portrait.ass   → 1080x1920 resolution
{video_name}_captions_landscape.ass  → 1920x1080 resolution
{video_name}_captions_square.ass     → 1080x1080 resolution
```

### Additional Files:
```
{video_name}_filters.txt             → FFmpeg filter file (backward compatibility)
```

---

## Template File Locations

### ASS Templates Directory:
```
/opt/n8n_scripts/video/n8n-video-processing-pipeline/ass-config-templates/
```

### Available Templates:
**Codify Brand:**
- `portrait_codify.ass`
- `landscape_codify.ass` 
- `square_codify.ass`

**Fancy Brand:**
- `portrait_fancy.ass`
- `landscape_fancy.ass`
- `square_fancy.ass`

---

## Working Examples from Your Setup

### 1. Process iPhone Portrait Video
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "/opt/n8n_scripts/video/_input-files/testvideo-portrait.MOV" \
  -style karaoke \
  -brand codify
```

**Output:**
- ✅ Detects -90° rotation → Portrait orientation
- ✅ Generates 3 ASS files for all formats
- ✅ Uses codify brand templates
- ✅ Applies karaoke word-highlighting

### 2. Process Landscape Video
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "/opt/n8n_scripts/video/_input-files/testvideo-landscape.MOV" \
  -style clean \
  -brand codify
```

### 3. Process Square Video
```bash
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "/opt/n8n_scripts/video/_input-files/testvideo-square.mov" \
  -style social \
  -brand fancy
```

---

## Technical Features

### 🤖 AI Transcription
- **Engine:** faster-whisper (small model)
- **Performance:** CPU optimized with int8 quantization
- **Languages:** Automatic language detection
- **Accuracy:** High-quality transcription with confidence scoring

### 📐 Smart Resolution Matching
- **Portrait ASS:** 1080x1920 (perfect for 9:16 outputs)
- **Landscape ASS:** 1920x1080 (perfect for 16:9 outputs)
- **Square ASS:** 1080x1080 (perfect for 1:1 outputs)

### 🎨 Advanced Styling
- **Karaoke effects:** Word-level timing with color transitions
- **Text wrapping:** Intelligent 2-line layout
- **Font optimization:** Size and positioning per format
- **Opacity control:** Template-based transparency settings

### 📱 Device Compatibility
- **iPhone rotation:** Automatic -90° metadata handling
- **Video formats:** MP4, MOV, AVI support
- **Cross-platform:** Works on macOS, Linux, Windows

---

## Performance & Output

### Processing Time:
- **Transcription:** 30-60 seconds (depends on video length)
- **ASS generation:** 2-4 seconds (generates 3 files)
- **Total overhead:** ~3-6 seconds vs single file generation

### File Sizes:
- **Each ASS file:** ~1-3KB (text-based, very small)
- **Storage impact:** Negligible compared to video files

### Quality Benefits:
- ✅ **No caption pixelation** - Each format uses native resolution
- ✅ **Perfect text scaling** - Optimal readability on all devices
- ✅ **Professional appearance** - No more stretched or tiny captions

---

## Error Handling & Validation

### Automatic Fallbacks:
- ✅ **Missing templates:** Warnings with graceful degradation
- ✅ **Style validation:** Falls back to first available style
- ✅ **File access:** Clear error messages for missing files
- ✅ **Format detection:** Default to landscape if detection fails

### Logging:
- ✅ **Detailed logs:** All operations logged to `transcription.log`
- ✅ **Progress tracking:** Real-time status updates
- ✅ **Success confirmation:** File generation verification
- ✅ **Error reporting:** Clear error messages and debugging info

---

## Integration with Rendering Pipeline

### Seamless Workflow:
```bash
# Step 1: Generate ASS files (all 3 formats)
python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
  -inputfile "video.mp4" \
  -style karaoke \
  -brand codify

# Step 2: Render videos (automatically uses correct ASS file)
./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "video.mp4" \
  -logo "codify-logo.png" \
  -version portrait  # Uses portrait ASS automatically

./functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo "video.mp4" \
  -logo "codify-logo.png" \
  -version landscape  # Uses landscape ASS automatically
```

---

## Prerequisites

### Required Dependencies:
```bash
pip install faster-whisper
```

### System Requirements:
- **Python:** 3.7+
- **FFmpeg:** For video analysis
- **CPU:** Multi-core recommended for faster processing
- **Memory:** 2GB+ RAM for model loading

### File Structure:
```
/opt/n8n_scripts/video/n8n-video-processing-pipeline/
├── functions/
│   └── 01_transcribe-video-to-ass-with-super-whisper.py
├── ass-config-templates/
│   ├── portrait_codify.ass
│   ├── landscape_codify.ass
│   └── square_codify.ass
└── _input-files/
    └── your-videos-here
```

---

## Troubleshooting

### Common Issues:

#### "Template not found" Error
```bash
# Check available templates
ls -la ass-config-templates/

# Use manual template specification
-template "portrait_codify.ass"
```

#### "No video stream found" Error
```bash
# Verify video file integrity
ffprobe -v quiet -show_entries stream=codec_type your-video.mp4
```

#### Language Detection Issues
```bash
# Check supported languages in logs
# faster-whisper supports 99+ languages automatically
```

---

## Advanced Usage

### Custom Template Development:
Templates are standard ASS files with configurable styles. You can create custom templates by:
1. Copying existing template
2. Modifying resolution (`PlayResX`/`PlayResY`)
3. Adjusting font sizes and positions
4. Adding to `ass-config-templates/` directory

### Batch Processing:
```bash
# Process multiple videos
for video in /path/to/videos/*.mp4; do
  python3 functions/01_transcribe-video-to-ass-with-super-whisper.py \
    -inputfile "$video" \
    -style karaoke \
    -brand codify
done
```

---

## Output Examples

### Success Output:
```
🎉 SUCCESS: Multi-format transcription completed
Generated 3 ASS files:
  - testvideo-portrait_captions_portrait.ass
  - testvideo-portrait_captions_landscape.ass
  - testvideo-portrait_captions_square.ass
Language: de (confidence: 0.99)
Duration: 7.3 seconds
```

### Log Details:
```
[INFO] Detected rotation: -90° - Effective dimensions: 1080x1920
[INFO] Auto-selected template: portrait_codify.ass
[INFO] Using style 'karaoke', Karaoke enabled: True
[INFO] ✅ Generated portrait ASS file: video_captions_portrait.ass
```

---

*Last updated: September 2025*
*Part of the n8n video processing pipeline*