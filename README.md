# n8n Video Processing Pipeline

A comprehensive video processing pipeline that integrates with n8n for automated video transcription, caption generation, and multi-format rendering with overlay graphics.

## 🎯 Overview

This pipeline takes raw video files and produces multiple output formats (portrait, landscape, square) with:
- ✅ **AI-powered transcription** using faster-whisper
- ✅ **Multi-format ASS captions** optimized for each aspect ratio
- ✅ **Professional overlays** (logos, icons, social handles)
- ✅ **Format-specific layouts** for maximum engagement
- ✅ **REST API integration** for seamless n8n workflow automation

## 🏗️ Architecture

```
Input Video → Transcription → Caption Generation → Multi-Format Rendering → Output Videos
     │              │                   │                      │                    │
     │         (faster-whisper)    (ASS files)        (FFmpeg rendering)       (.mp4 files)
     │              │                   │                      │                    │
     └─── n8n API ──┴─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
n8n-video-processing-pipeline/
├── README.md                          # This file
├── n8n-video-api.py                   # Flask API orchestrator
├── start_api.sh                       # API startup script
├── test_api.py                        # API testing script
├── 
├── functions/                         # Core processing scripts
│   ├── 01_transcribe-video-to-ass-with-super-whisper.py
│   ├── 01_transcribe-video-to-ass-with-super-whisper_USAGE.md
│   ├── 02_render-captions-and-layout-into-video.sh
│   └── 02_render-captions-and-layout-into-video_USAGE.md
├── 
├── ass-config-templates/              # ASS caption templates
│   ├── portrait_codify.ass
│   ├── landscape_codify.ass
│   ├── square_codify.ass
│   ├── portrait_fancy.ass
│   ├── landscape_fancy.ass
│   └── square_fancy.ass
├── 
├── overlay-files/                     # Brand assets and overlays
│   ├── codify-logo-blur.png
│   ├── codify-icon.png
│   ├── codify-sm-handle.png
│   └── [your brand assets here]
└── 
└── logs/                              # Processing logs
    └── api.log                        # API server logs
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Python dependencies
pip3 install flask faster-whisper requests

# System dependencies (if needed)
brew install ffmpeg  # macOS
# apt install ffmpeg  # Ubuntu/Debian
```

### 2. Start the API Server

```bash
# Start the API
./start_api.sh start

# Check status
./start_api.sh status

# View logs
./start_api.sh logs
```

### 3. Test the API

```bash
# Run basic tests
./start_api.sh test

# Or test manually
curl http://localhost:5000/health
```

## 📡 API Usage

### Endpoint: `POST /process`

**Input JSON:**
```json
[
  {
    "input_file": "/mnt/n8n_host_scripts/video/_input-files/my-video.mp4",
    "target_formats": ["portrait", "landscape", "square"],
    "logo_file": "codify-logo-blur.png",
    "icon_file": "codify-icon.png", 
    "socialmediahandle_file": "codify-sm-handle.png",
    "enable_captions": true,
    "captiontemplate": "portrait_codify.ass -style karaoke -brand codify"
  }
]
```

**Output JSON:**
```json
{
  "VideoURL_Portrait": "/opt/n8n_scripts/video/_output-files/my-video_portrait.mp4",
  "VideoURL_Landscape": "/opt/n8n_scripts/video/_output-files/my-video_landscape.mp4",
  "VideoURL_Square": "/opt/n8n_scripts/video/_output-files/my-video_square.mp4",
  "success": true,
  "processed_formats": 3,
  "total_errors": 0
}
```

### Other Endpoints

- `GET /health` - Health check
- `GET /status` - Service status and configuration

## 🎨 Caption Styles

| Style | Description | Best For |
|-------|-------------|----------|
| `clean` | Minimalist, readable | Professional content, tutorials |
| `social` | Bold, high-impact | Social media posts |
| `karaoke` | Word-by-word highlighting | Engagement, sing-alongs |
| `highlight` | Maximum emphasis | Key announcements |

## 🏷️ Brands

| Brand | Theme | Templates |
|-------|-------|-----------|
| `codify` | Professional, clean | `*_codify.ass` |
| `fancy` | Creative, vibrant | `*_fancy.ass` |

## 🔧 Configuration

### Path Structure (Coolify Integration)

```bash
# n8n container paths (input)
/mnt/n8n_host_scripts/video/_input-files/

# Host system paths (processing & output)  
/opt/n8n_scripts/video/_input-files/          # Input files
/opt/n8n_scripts/video/_output-files/         # Rendered videos
/opt/n8n_scripts/video/n8n-video-processing-pipeline/  # Pipeline scripts
```

### Template Configuration

ASS templates are located in `ass-config-templates/` and define:
- Resolution (PlayResX/PlayResY)
- Font sizes and positioning
- Color schemes and effects
- Karaoke timing configurations

## 📊 Processing Flow

### 1. Input Validation
- ✅ File existence check
- ✅ Format validation
- ✅ Parameter parsing

### 2. Transcription (if enabled)
- 🤖 **faster-whisper** model loading
- 🎯 **Automatic language detection** 
- 📝 **Multi-format ASS generation** (portrait/landscape/square)
- ⚡ **Karaoke timing** with word-level precision

### 3. Rendering (per format)
- 🎬 **Video analysis** (resolution, rotation, duration)
- 🖼️ **Overlay composition** (logos, icons, handles)
- 📐 **Layout adaptation** (format-specific positioning)
- 🎭 **Caption rendering** (format-matched ASS files)
- 📹 **Video encoding** (optimized settings)

### 4. Output Generation
- 📁 **File organization** in `_output-files/`
- 📋 **Path reporting** back to n8n
- 📈 **Success/error tracking**

## 🔍 Monitoring & Debugging

### Log Files
```bash
# API server logs
tail -f api.log

# Processing logs  
tail -f transcription.log
```

### Status Monitoring
```bash
# Check API status
./start_api.sh status

# Test endpoints
./start_api.sh test

# View recent activity
./start_api.sh logs
```

### Common Issues & Solutions

#### "Template not found"
```bash
# Check available templates
ls -la ass-config-templates/

# Verify template name in request
```

#### "Input file not found"
```bash
# Verify path mapping between n8n container and host
# n8n: /mnt/n8n_host_scripts/video/_input-files/
# Host: /opt/n8n_scripts/video/_input-files/
```

#### "FFmpeg not found"
```bash
# Install FFmpeg
brew install ffmpeg  # macOS
sudo apt install ffmpeg  # Ubuntu/Debian
```

## ⚡ Performance

### Processing Times (typical)
- **Transcription:** 30-60 seconds (varies by length)
- **Rendering per format:** 60-120 seconds
- **Total for 3 formats:** 4-6 minutes

### Resource Usage
- **CPU:** High during transcription and rendering
- **Memory:** 2-4GB peak (model loading)
- **Disk:** ~100MB per output video (1080p)

## 🔧 Advanced Usage

### Custom Templates
1. Copy existing template from `ass-config-templates/`
2. Modify resolution, fonts, colors
3. Save with descriptive name
4. Reference in API calls

### Batch Processing
```bash
# Process multiple videos
for video in /path/to/videos/*.mp4; do
  curl -X POST http://localhost:5000/process \
    -H "Content-Type: application/json" \
    -d "[{\"input_file\":\"$video\",\"target_formats\":[\"landscape\"]}]"
done
```

### n8n Integration Example
```javascript
// n8n HTTP Request Node
{
  "method": "POST",
  "url": "http://localhost:5000/process",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": [
    {
      "input_file": "{{$node[\"File_Upload\"].json[\"file_path\"]}}",
      "target_formats": ["portrait", "landscape"],
      "logo_file": "{{$node[\"Set_Brand\"].json[\"logo\"]}}",
      "enable_captions": true,
      "captiontemplate": "-style social -brand codify"
    }
  ]
}
```

## 🔒 Security Considerations

- ✅ **Input validation** prevents path traversal
- ✅ **File existence checks** prevent errors
- ✅ **Timeout handling** prevents resource exhaustion
- ✅ **Error containment** prevents cascade failures
- ✅ **Logging** for audit trails

## 🛠️ Maintenance

### Regular Tasks
- Monitor log file sizes
- Clean up old output files
- Update faster-whisper models
- Backup custom templates

### Updating
```bash
# Stop API
./start_api.sh stop

# Update code (git pull, etc.)

# Restart API  
./start_api.sh start
```

## 📞 Troubleshooting

### API Won't Start
1. Check dependencies: `pip3 list | grep -E "(flask|faster-whisper)"`
2. Check port availability: `lsof -i :5000`
3. Check permissions: `ls -la n8n-video-api.py`
4. Check logs: `cat api.log`

### Processing Fails
1. Check input file exists and is readable
2. Check overlay files in `overlay-files/`
3. Check template files in `ass-config-templates/`
4. Review processing logs for specific errors

### Performance Issues
1. Monitor system resources during processing
2. Consider reducing video resolution for faster processing
3. Use SSD storage for better I/O performance
4. Ensure adequate RAM (4GB+ recommended)

---

## 📋 API Management Commands

```bash
# Start/stop/restart
./start_api.sh start
./start_api.sh stop  
./start_api.sh restart

# Monitor
./start_api.sh status
./start_api.sh logs

# Test
./start_api.sh test
```

---

*Pipeline created for seamless n8n integration with professional video processing capabilities.*