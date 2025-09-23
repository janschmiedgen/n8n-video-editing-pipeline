# Changelog

All notable changes to the n8n Video Editing Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-09-23

### Added
- Initial release of n8n Video Editing Pipeline
- Flask REST API for video processing automation (`n8n-video-api.py`)
- AI-powered transcription using faster-whisper
- Multi-format video rendering (portrait, landscape, square)
- Brand overlay integration (logos, icons, social media handles)
- Format-specific ASS caption generation with configurable styles
- CLI testing suite (`test_pipeline_cli.py`)
- API management scripts (`start_api.sh`)
- Comprehensive documentation and usage guides
- Professional video layout configurations for different formats
- Caption templates with multiple styles (clean, social, karaoke, highlight)
- Error handling and graceful fallbacks
- Logging and monitoring capabilities
- GitHub repository setup with badges and professional documentation

### Features
- **Transcription Engine**: faster-whisper with automatic language detection
- **Multi-format Support**: Automatic generation of portrait (9:16), landscape (16:9), and square (1:1) outputs
- **Brand Integration**: Logo, icon, and social media handle overlays with configurable opacity
- **Caption Styles**: Four distinct caption styles for different use cases
- **API Integration**: RESTful API designed for n8n workflow automation
- **Testing Tools**: Complete CLI testing suite for development and debugging
- **Production Ready**: Management scripts, logging, and health monitoring

### Technical Specifications
- Python 3.7+ compatibility
- Flask web framework for API
- FFmpeg for video processing
- ASS subtitle format for advanced caption styling
- Configurable overlay positioning and opacity
- Automatic video rotation detection and handling
- Format-specific template system

### Documentation
- Complete README with usage examples
- Individual script documentation with detailed parameters
- API endpoint documentation with JSON examples
- Troubleshooting guides and performance optimization tips
- Migration guide for server deployment