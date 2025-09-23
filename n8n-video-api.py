#!/usr/bin/env python3
"""
n8n Video Processing Pipeline API
==================================

Flask API that orchestrates the video processing pipeline by:
1. Receiving JSON input from n8n with processing parameters
2. Running transcription script (if captions enabled)
3. Running rendering script for each target format
4. Returning JSON with output video file paths

Author: n8n Pipeline Integration
Version: 1.0
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/n8n_scripts/video/n8n-video-processing-pipeline/api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
SCRIPT_DIR = '/opt/n8n_scripts/video/n8n-video-processing-pipeline'
FUNCTIONS_DIR = os.path.join(SCRIPT_DIR, 'functions')
OVERLAY_FILES_DIR = os.path.join(SCRIPT_DIR, 'overlay-files')
OUTPUT_DIR = '/opt/n8n_scripts/video/_output-files'
TRANSCRIPTION_SCRIPT = os.path.join(FUNCTIONS_DIR, '01_transcribe-video-to-ass-with-super-whisper.py')
RENDERING_SCRIPT = os.path.join(FUNCTIONS_DIR, '02_render-captions-and-layout-into-video.sh')

class VideoProcessingError(Exception):
    """Custom exception for video processing errors"""
    pass

def validate_input(data):
    """Validate the input JSON data"""
    required_fields = ['input_file', 'target_formats']
    
    for item in data:
        for field in required_fields:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate input file exists
        if not os.path.exists(item['input_file']):
            raise ValueError(f"Input file not found: {item['input_file']}")
        
        # Parse target_formats if it's a string
        if isinstance(item['target_formats'], str):
            try:
                item['target_formats'] = json.loads(item['target_formats'])
            except json.JSONDecodeError:
                raise ValueError(f"Invalid target_formats JSON: {item['target_formats']}")
        
        # Validate target formats
        valid_formats = ['portrait', 'landscape', 'square']
        for fmt in item['target_formats']:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid target format: {fmt}. Must be one of: {valid_formats}")
    
    return True

def extract_caption_params(captiontemplate):
    """
    Parse captiontemplate string like 'landscape_fancy.ass -style social'
    Returns: (template, style, brand)
    """
    if not captiontemplate:
        return None, 'clean', 'codify'  # defaults
    
    parts = captiontemplate.split()
    template = None
    style = 'clean'
    brand = 'codify'
    
    # Find template file
    for i, part in enumerate(parts):
        if part.endswith('.ass'):
            template = part
            break
    
    # Find style parameter
    try:
        style_index = parts.index('-style')
        if style_index + 1 < len(parts):
            style = parts[style_index + 1]
    except ValueError:
        pass  # -style not found, use default
    
    # Find brand parameter
    try:
        brand_index = parts.index('-brand')
        if brand_index + 1 < len(parts):
            brand = parts[brand_index + 1]
    except ValueError:
        pass  # -brand not found, use default
    
    return template, style, brand

def run_transcription(input_file, captiontemplate):
    """Run the transcription script to generate ASS caption files"""
    logger.info(f"Starting transcription for: {input_file}")
    
    # Parse caption parameters
    template, style, brand = extract_caption_params(captiontemplate)
    
    # Build transcription command
    cmd = [
        'python3', TRANSCRIPTION_SCRIPT,
        '-inputfile', input_file,
        '-style', style,
        '-brand', brand
    ]
    
    # Add template if specified
    if template:
        cmd.extend(['-template', template])
    
    logger.info(f"Transcription command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            error_msg = f"Transcription failed with return code {result.returncode}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            logger.error(error_msg)
            raise VideoProcessingError(error_msg)
        
        logger.info(f"Transcription completed successfully")
        logger.info(f"Transcription output: {result.stdout}")
        return True
        
    except subprocess.TimeoutExpired:
        raise VideoProcessingError("Transcription timed out after 5 minutes")
    except Exception as e:
        raise VideoProcessingError(f"Transcription error: {str(e)}")

def run_rendering(input_file, target_format, logo_file=None, icon_file=None, socialmediahandle_file=None):
    """Run the rendering script for a specific format"""
    logger.info(f"Starting rendering for format: {target_format}")
    
    # Build rendering command
    cmd = [
        'bash', RENDERING_SCRIPT,
        '-inputvideo', input_file,
        '-version', target_format
    ]
    
    # Add optional overlay files
    if logo_file:
        logo_path = os.path.join(OVERLAY_FILES_DIR, logo_file)
        if os.path.exists(logo_path):
            cmd.extend(['-logo', logo_path])
        else:
            logger.warning(f"Logo file not found: {logo_path}")
    
    if icon_file:
        icon_path = os.path.join(OVERLAY_FILES_DIR, icon_file)
        if os.path.exists(icon_path):
            cmd.extend(['-icon', icon_path])
        else:
            logger.warning(f"Icon file not found: {icon_path}")
    
    if socialmediahandle_file:
        socialmediahandle_path = os.path.join(OVERLAY_FILES_DIR, socialmediahandle_file)
        if os.path.exists(socialmediahandle_path):
            cmd.extend(['-socialmediahandle', socialmediahandle_path])
        else:
            logger.warning(f"Social media handle file not found: {socialmediahandle_path}")
    
    logger.info(f"Rendering command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=SCRIPT_DIR, capture_output=True, text=True, timeout=600)
        
        if result.returncode != 0:
            error_msg = f"Rendering failed for {target_format} with return code {result.returncode}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
            logger.error(error_msg)
            raise VideoProcessingError(error_msg)
        
        logger.info(f"Rendering completed successfully for {target_format}")
        logger.info(f"Rendering output: {result.stdout}")
        
        # Extract output file path from the rendering script output
        output_file = extract_output_path(result.stdout, input_file, target_format)
        return output_file
        
    except subprocess.TimeoutExpired:
        raise VideoProcessingError(f"Rendering timed out after 10 minutes for {target_format}")
    except Exception as e:
        raise VideoProcessingError(f"Rendering error for {target_format}: {str(e)}")

def extract_output_path(stdout_output, input_file, target_format):
    """Extract the output file path from rendering script output"""
    # Try to find output file path in stdout
    lines = stdout_output.split('\n')
    for line in lines:
        if 'output file:' in line.lower() or 'generated:' in line.lower():
            # Extract file path from line
            parts = line.split()
            for part in parts:
                if part.endswith('.mp4') and OUTPUT_DIR in part:
                    return part
    
    # Fallback: construct expected path
    input_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_filename = f"{input_filename}_{target_format}.mp4"
    return os.path.join(OUTPUT_DIR, output_filename)

def process_video_item(item):
    """Process a single video item from the input JSON"""
    input_file = item['input_file']
    target_formats = item['target_formats']
    enable_captions = item.get('enable_captions', False)
    captiontemplate = item.get('captiontemplate', '')
    
    logger.info(f"Processing video: {input_file}")
    logger.info(f"Target formats: {target_formats}")
    logger.info(f"Captions enabled: {enable_captions}")
    
    results = {}
    errors = []
    
    try:
        # Step 1: Generate captions if enabled
        if enable_captions:
            run_transcription(input_file, captiontemplate)
        
        # Step 2: Render each target format
        for target_format in target_formats:
            try:
                output_file = run_rendering(
                    input_file,
                    target_format,
                    item.get('logo_file'),
                    item.get('icon_file'),
                    item.get('socialmediahandle_file')
                )
                
                # Store result with capitalized format name
                result_key = f"VideoURL_{target_format.capitalize()}"
                results[result_key] = output_file
                
            except VideoProcessingError as e:
                error_msg = f"Failed to render {target_format}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
    
    except VideoProcessingError as e:
        error_msg = f"Transcription failed: {str(e)}"
        errors.append(error_msg)
        logger.error(error_msg)
        # If transcription fails, we can still try rendering without captions
        logger.warning("Attempting to render without captions...")
        
        for target_format in target_formats:
            try:
                output_file = run_rendering(
                    input_file,
                    target_format,
                    item.get('logo_file'),
                    item.get('icon_file'),
                    item.get('socialmediahandle_file')
                )
                
                result_key = f"VideoURL_{target_format.capitalize()}"
                results[result_key] = output_file
                
            except VideoProcessingError as e:
                error_msg = f"Failed to render {target_format}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
    
    return results, errors

@app.route('/process', methods=['POST'])
def process_videos():
    """Main endpoint for processing videos"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({'error': 'Request must contain JSON data'}), 400
        
        data = request.get_json()
        
        if not isinstance(data, list) or len(data) == 0:
            return jsonify({'error': 'Input must be a non-empty array of video processing requests'}), 400
        
        logger.info(f"Received processing request for {len(data)} video(s)")
        
        # Validate input
        validate_input(data)
        
        # Process each video item
        all_results = {}
        all_errors = []
        
        for i, item in enumerate(data):
            logger.info(f"Processing item {i+1}/{len(data)}")
            results, errors = process_video_item(item)
            
            # Merge results (in case of multiple videos, we might need to adjust this)
            all_results.update(results)
            all_errors.extend(errors)
        
        # Prepare response
        response = all_results.copy()
        
        # Add error information if any
        if all_errors:
            response['errors'] = all_errors
            response['success'] = len(all_results) > 0  # Partial success if some formats worked
        else:
            response['success'] = True
        
        # Add processing summary
        response['processed_formats'] = len(all_results)
        response['total_errors'] = len(all_errors)
        
        logger.info(f"Processing completed. Results: {len(all_results)} videos, {len(all_errors)} errors")
        
        return jsonify(response)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'error': f'Validation error: {str(e)}', 'success': False}), 400
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': f'Internal server error: {str(e)}', 'success': False}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'transcription_script_exists': os.path.exists(TRANSCRIPTION_SCRIPT),
        'rendering_script_exists': os.path.exists(RENDERING_SCRIPT),
        'overlay_files_dir_exists': os.path.exists(OVERLAY_FILES_DIR),
        'output_dir_exists': os.path.exists(OUTPUT_DIR)
    })

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint with configuration info"""
    return jsonify({
        'service': 'n8n Video Processing Pipeline API',
        'version': '1.0',
        'script_dir': SCRIPT_DIR,
        'functions_dir': FUNCTIONS_DIR,
        'overlay_files_dir': OVERLAY_FILES_DIR,
        'output_dir': OUTPUT_DIR,
        'supported_formats': ['portrait', 'landscape', 'square'],
        'endpoints': ['/process', '/health', '/status']
    })

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Log startup
    logger.info("Starting n8n Video Processing Pipeline API")
    logger.info(f"Script directory: {SCRIPT_DIR}")
    logger.info(f"Functions directory: {FUNCTIONS_DIR}")
    logger.info(f"Overlay files directory: {OVERLAY_FILES_DIR}")
    logger.info(f"Output directory: {OUTPUT_DIR}")
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)