#!/usr/bin/env python3
"""
Advanced transcription script for n8n video pipeline
Generates ASS caption files using ASS templates with multiple styles
Supports auto-detection of aspect ratio and template selection
Usage: python3 01_transcribe-video-to-ass-with-super-whisper.py -inputfile video.mp4 -style clean
Usage: python3 01_transcribe-video-to-ass-with-super-whisper.py -inputfile video.mp4 -template landscape_fancy.ass -style karaoke
"""

import sys
import os
import argparse
import logging
import subprocess
import json
import re
from pathlib import Path
from faster_whisper import WhisperModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transcription.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def format_ass_timestamp(seconds):
    """Format seconds to ASS timestamp format (H:MM:SS.cc)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centisecs = int((seconds % 1) * 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

def detect_aspect_ratio(video_path):
    """Detect video aspect ratio using ffprobe, accounting for rotation metadata"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-select_streams', 'v:0',
            str(video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        if 'streams' in data and len(data['streams']) > 0:
            stream = data['streams'][0]
            width = int(stream.get('width', 0))
            height = int(stream.get('height', 0))
            
            if width == 0 or height == 0:
                logger.warning("Could not determine video dimensions")
                return "landscape"  # Default fallback
            
            # Check for rotation metadata
            rotation = 0
            if 'side_data_list' in stream:
                for side_data in stream['side_data_list']:
                    if side_data.get('side_data_type') == 'Display Matrix':
                        rotation = abs(int(side_data.get('rotation', 0)))
                        break
            
            # If rotated by 90 or 270 degrees, swap width and height
            if rotation in [90, 270]:
                width, height = height, width
                logger.info(f"Video has {rotation}° rotation, effective dimensions: {width}x{height}")
            
            aspect_ratio = width / height
            logger.info(f"Original dimensions: {stream.get('width')}x{stream.get('height')}, effective aspect ratio: {aspect_ratio:.2f}")
            
            if aspect_ratio > 1.3:  # Landscape (wider than 4:3)
                return "landscape"
            elif aspect_ratio < 0.8:  # Portrait (taller than 5:4)
                return "portrait"
            else:  # Square-ish (between 5:4 and 4:3)
                return "square"
        else:
            logger.warning("No video stream found")
            return "landscape"  # Default fallback
            
    except Exception as e:
        logger.error(f"Error detecting aspect ratio: {e}")
        return "landscape"  # Default fallback

def auto_select_template(aspect_ratio, brand='codify'):
    """Auto-select template based on aspect ratio and brand"""
    template_name = f"{aspect_ratio}_{brand}.ass"
    template_dir = Path(__file__).parent.parent / "ass-config-templates"
    template_path = template_dir / template_name
    
    if template_path.exists():
        logger.info(f"Auto-selected template: {template_name}")
        return template_path
    else:
        logger.error(f"Auto-selection failed: template not found: {template_path}")
        return None

def load_template_file(template_path):
    """Load and parse ASS template file"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        logger.info(f"Loaded template: {template_path}")
        return template_content
    except Exception as e:
        logger.error(f"Failed to load template {template_path}: {e}")
        return None

def parse_template_styles(template_content):
    """Extract available styles from ASS template"""
    styles = []
    lines = template_content.split('\n')
    
    for line in lines:
        if line.startswith('Style: '):
            # Parse style name (first field after "Style: ")
            parts = line.split(',', 2)
            if len(parts) >= 2:
                style_name = parts[0].replace('Style: ', '').strip()
                styles.append(style_name)
    
    logger.info(f"Found styles in template: {styles}")
    return styles

def validate_style_in_template(template_content, requested_style):
    """Validate that requested style exists in template"""
    available_styles = parse_template_styles(template_content)
    
    if requested_style in available_styles:
        return requested_style
    elif available_styles:
        fallback_style = available_styles[0]
        logger.warning(f"Requested style '{requested_style}' not found, using fallback: '{fallback_style}'")
        return fallback_style
    else:
        logger.error("No valid styles found in template")
        return None

def wrap_text_to_lines(text, max_lines=2, wrap_mode='word'):
    """Wrap text to specified number of lines"""
    if not text.strip():
        return text
    
    words = text.strip().split()
    if len(words) <= 3:  # Very short text, keep on one line
        return text
    
    if max_lines == 2:
        # Split into two roughly equal lines
        mid_point = len(words) // 2
        
        # Try to find a good breaking point near the middle
        # Look for natural breaks (punctuation) within +/-2 words of midpoint
        best_break = mid_point
        for i in range(max(1, mid_point - 2), min(len(words), mid_point + 3)):
            if i < len(words) and words[i-1].rstrip().endswith((',', '.', '!', '?', ';', ':')):
                best_break = i
                break
        
        line1 = ' '.join(words[:best_break])
        line2 = ' '.join(words[best_break:])
        
        return line1 + '\\N' + line2  # \\N is ASS line break
    
    return text

def generate_word_timings(text, start_time, end_time, word_duration):
    """Generate word-level timings for karaoke effect, handling line breaks"""
    # Handle line breaks - split by \\N and process each line separately
    if '\\N' in text:
        lines = text.split('\\N')
        karaoke_lines = []
        total_duration = end_time - start_time
        duration_per_line = total_duration / len(lines)
        
        for line_idx, line in enumerate(lines):
            line_start = start_time + (line_idx * duration_per_line)
            line_end = line_start + duration_per_line
            karaoke_line = generate_word_timings(line.strip(), line_start, line_end, word_duration)
            karaoke_lines.append(karaoke_line)
        
        return '\\N'.join(karaoke_lines)
    
    # Single line processing
    words = text.strip().split()
    if not words:
        return text
    
    # Calculate duration per word
    total_duration = end_time - start_time
    if word_duration > 0:
        # Use fixed word duration from config (in centiseconds)
        duration_per_word = word_duration / 100.0  # Convert centiseconds to seconds
    else:
        # Distribute time evenly across words
        duration_per_word = total_duration / len(words)
    
    # Generate karaoke timing tags
    karaoke_text = ""
    current_time = 0
    
    for i, word in enumerate(words):
        # Calculate timing in centiseconds for ASS karaoke
        timing_cs = int(duration_per_word * 100)
        karaoke_text += f"{{\\k{timing_cs}}}{word}"
        if i < len(words) - 1:  # Add space between words (except last)
            karaoke_text += " "
        current_time += duration_per_word
    
    return karaoke_text

def generate_from_template(segments, output_path, template_content, style_name):
    """Generate ASS file from template with transcription segments"""
    
    # Determine karaoke settings based on style name
    karaoke_enabled = style_name == 'karaoke'
    word_duration = 50  # Default timing for karaoke
    
    logger.info(f"Using style '{style_name}', Karaoke enabled: {karaoke_enabled}")
    
    # Split template into sections
    sections = template_content.split('[Events]')
    if len(sections) != 2:
        logger.error("Template format error: [Events] section not found or multiple sections")
        return False
    
    template_header = sections[0].rstrip()
    events_format = sections[1].split('\n')[1] if '\n' in sections[1] else "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    
    # Write the complete ASS file
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write template header (Script Info + V4+ Styles sections)
        f.write(template_header)
        f.write('\n')
        
        # Write Events section
        f.write('[Events]\n')
        f.write(f"{events_format}\n")
        
        # Generate dialogue lines from transcription segments
        for segment in segments:
            start_time = format_ass_timestamp(segment['start'])
            end_time = format_ass_timestamp(segment['end'])
            text = segment['text'].strip()
            
            # Apply text wrapping to 2 lines
            text = wrap_text_to_lines(text, 2, 'word')
            
            # Apply karaoke timing if karaoke style is selected
            if karaoke_enabled:
                text = generate_word_timings(text, segment['start'], segment['end'], word_duration)
                # Add karaoke effect prefix for better highlighting
                text = f"{{\\1c&H0000FFFF&}}" + text
            
            # Write dialogue line using the requested style
            f.write(f"Dialogue: 0,{start_time},{end_time},{style_name},,0,0,0,,{text}\n")
    
    return True

def create_filter_file(input_file, ass_file, output_path):
    """Create FFmpeg filter file for video processing"""
    
    input_name = Path(input_file).stem
    ass_name = Path(ass_file).name
    
    # Basic filter for adding ASS subtitles
    filter_content = f"[0:v]subtitles='{ass_name}':force_style='Fontname=Roboto Medium,Fontsize=48'[v]\n"
    
    with open(output_path, 'w') as f:
        f.write(filter_content)

def transcribe_video(input_file, template_path=None, style_name='clean', brand='codify'):
    """Main transcription function using ASS templates - generates 3 ASS files for all output formats"""
    
    try:
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error(f"Input file not found: {input_file}")
            return False
        
        # Output files in same directory as input
        output_dir = input_path.parent
        base_name = input_path.stem
        
        logger.info(f"Starting transcription: {input_file}")
        logger.info(f"Style: {style_name}")
        logger.info(f"Brand: {brand}")
        
        # Detect video aspect ratio for primary template selection
        detected_aspect = detect_aspect_ratio(input_path)
        logger.info(f"Detected input aspect ratio: {detected_aspect}")
        
        # Load faster-whisper model (do this once)
        logger.info("Loading Whisper model (small)...")
        model = WhisperModel("small", device="cpu", compute_type="int8")
        
        # Transcribe video (do this once)
        logger.info("Transcribing audio...")
        segments, info = model.transcribe(str(input_path), beam_size=5)
        
        # Collect segments
        transcript_segments = []
        for segment in segments:
            transcript_segments.append({
                'start': segment.start,
                'end': segment.end,
                'text': segment.text.strip()
            })
        
        if not transcript_segments:
            logger.error("No transcription segments generated")
            return False
        
        logger.info(f"Transcription completed: {len(transcript_segments)} segments")
        logger.info(f"Language: {info.language} (confidence: {info.language_probability:.2f})")
        logger.info(f"Duration: {info.duration:.1f} seconds")
        
        # Generate ASS files for all three output formats
        formats = ['portrait', 'landscape', 'square']
        generated_files = []
        
        for output_format in formats:
            logger.info(f"\n--- Generating ASS for {output_format} format ---")
            
            # Determine template path for this format
            if template_path is None:
                # Auto-select template for this format
                format_template_path = auto_select_template(output_format, brand)
                if format_template_path is None:
                    logger.warning(f"Template auto-selection failed for {output_format}_{brand}.ass - skipping format")
                    continue
            else:
                # Use manually specified template (apply to all formats)
                template_dir = Path(__file__).parent.parent / "ass-config-templates"
                format_template_path = template_dir / template_path
                logger.info(f"Using specified template for all formats: {format_template_path}")
                
                if not format_template_path.exists():
                    logger.warning(f"Specified template not found: {format_template_path} - skipping format")
                    continue
            
            # Load template content
            template_content = load_template_file(format_template_path)
            if template_content is None:
                logger.warning(f"Failed to load template content for {output_format} - skipping")
                continue
            
            # Validate style exists in template
            validated_style = validate_style_in_template(template_content, style_name)
            if validated_style is None:
                logger.warning(f"No valid styles found in template for {output_format} - skipping")
                continue
            
            # Generate format-specific ASS file
            ass_file = output_dir / f"{base_name}_captions_{output_format}.ass"
            logger.info(f"Output ASS: {ass_file}")
            
            success = generate_from_template(transcript_segments, ass_file, template_content, validated_style)
            if success:
                logger.info(f"✅ Generated {output_format} ASS file: {ass_file.name}")
                generated_files.append(ass_file)
            else:
                logger.warning(f"❌ Failed to generate {output_format} ASS file")
        
        # Create filter file (for backward compatibility - uses detected format)
        if generated_files:
            # Use the ASS file matching the detected aspect ratio, or first available
            primary_ass = None
            for generated_file in generated_files:
                if detected_aspect in generated_file.name:
                    primary_ass = generated_file
                    break
            if primary_ass is None:
                primary_ass = generated_files[0]
            
            filter_file = output_dir / f"{base_name}_filters.txt"
            logger.info(f"Creating filter file: {filter_file} (using {primary_ass.name})")
            create_filter_file(input_file, primary_ass, filter_file)
        
        # Log final success
        logger.info(f"\n🎉 SUCCESS: Multi-format transcription completed")
        logger.info(f"Generated {len(generated_files)} ASS files:")
        for ass_file in generated_files:
            logger.info(f"  - {ass_file.name}")
        
        return len(generated_files) > 0
        
    except Exception as e:
        logger.error(f"ERROR: Transcription failed - {str(e)}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Transcribe video to ASS captions using ASS templates with multiple styles',
        epilog='''
Examples:
  # Auto-select template with default brand (codify)
  python3 %(prog)s -inputfile video.mp4 -style clean
  
  # Manual template selection
  python3 %(prog)s -inputfile video.mp4 -template landscape_fancy.ass -style karaoke
  
  # Auto-select with specific brand
  python3 %(prog)s -inputfile video.mp4 -style social -brand fancy
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-inputfile', required=True, 
                       help='Input video file (e.g., video.mp4)')
    parser.add_argument('-style', required=True, 
                       choices=['clean', 'social', 'karaoke', 'highlight'],
                       help='Caption style from template (clean, social, karaoke, highlight)')
    parser.add_argument('-template', 
                       help='Specific ASS template file (e.g., landscape_fancy.ass). If not provided, auto-selects based on aspect ratio and brand')
    parser.add_argument('-brand', 
                       choices=['codify', 'fancy'], 
                       default='codify',
                       help='Brand theme for auto-selection (default: codify)')
    
    args = parser.parse_args()
    
    # Perform transcription
    success = transcribe_video(
        input_file=args.inputfile,
        template_path=args.template, 
        style_name=args.style,
        brand=args.brand
    )
    
    if success:
        print("SUCCESS")
        sys.exit(0)
    else:
        print("ERROR")
        sys.exit(1)

if __name__ == "__main__":
    main()