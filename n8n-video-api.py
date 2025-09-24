#!/usr/bin/env python3
"""
n8n Video Processing Pipeline API
==================================

Command-line script that orchestrates the video processing pipeline by:
1. Receiving JSON parameters via command-line arguments
2. Running transcription script (01_transcribe-video-to-ass-with-super-whisper.py)
3. Running rendering script (02_render-captions-and-layout-into-video.sh) for each requested format
4. Returning clean JSON with output video file paths (n8n compatible paths)

Key Features:
- Path conversion: /mnt/n8n_host_scripts/ ↔ /opt/n8n_scripts/
- Target formats: Only generate requested formats, return empty for others
- Clean JSON output: No logging contamination
- Partial results: Failed formats return empty strings

Usage:
    python3 n8n-video-api.py \
        --input_file "/mnt/n8n_host_scripts/video/_input-files/test.mp4" \
        --target_formats "portrait,landscape" \
        --enable_captions true \
        --style "karaoke" \
        --brand "fancy" \
        --logo_file "codify-logo.png" \
        --icon_file "codify-icon.png" \
        --socialmediahandle "codify-sm-handle.png"
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path


def setup_logging():
    """Configure logging to FILE ONLY - no stdout contamination"""
    log_dir = Path("/opt/n8n_scripts/video/logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "n8n-video-api.log"),
            # NO StreamHandler to avoid stdout contamination!
        ]
    )
    return logging.getLogger(__name__)


def convert_path_to_host(path):
    """Convert n8n container path to host path: /mnt/n8n_host_scripts/ → /opt/n8n_scripts/"""
    if not path:
        return path
    return str(path).replace('/mnt/n8n_host_scripts/', '/opt/n8n_scripts/')


def convert_path_to_container(path):
    """Convert host path to n8n container path: /opt/n8n_scripts/ → /mnt/n8n_host_scripts/"""
    if not path:
        return path
    return str(path).replace('/opt/n8n_scripts/', '/mnt/n8n_host_scripts/')


def parse_args():
    """Parse command line arguments matching n8n parameter names"""
    parser = argparse.ArgumentParser(description='n8n Video Processing Pipeline')
    
    parser.add_argument('--input_file', required=True, help='Input video file path')
    parser.add_argument('--target_formats', required=True, help='Comma-separated target formats: portrait,landscape,square')
    parser.add_argument('--enable_captions', type=str, choices=['true', 'false'], default='false', help='Enable captions')
    parser.add_argument('--style', default='clean', help='Caption style (default: clean)')
    parser.add_argument('--brand', default='codify', help='Brand template (default: codify)')
    parser.add_argument('--logo_file', help='Logo overlay filename (from overlay-files/)')
    parser.add_argument('--icon_file', help='Icon overlay filename (from overlay-files/)')
    parser.add_argument('--socialmediahandle', help='Social media handle filename (from overlay-files/)')
    
    return parser.parse_args()


def run_transcription(logger, input_video_path, style, brand):
    """Run transcription script to generate ASS caption files"""
    logger.info(f"Starting transcription: input={input_video_path}, style={style}, brand={brand}")
    
    transcription_script = "/opt/n8n_scripts/video/n8n-video-processing-pipeline/functions/01_transcribe-video-to-ass-with-super-whisper.py"
    cmd = [
        "python3", transcription_script,
        "-inputfile", input_video_path,
        "-style", style,
        "-brand", brand
    ]
    
    logger.info(f"Running transcription command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            logger.info("Transcription completed successfully")
            logger.info(f"Transcription stdout: {result.stdout}")
            return True
        else:
            logger.error(f"Transcription failed with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Transcription timed out after 10 minutes")
        return False
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return False


def run_rendering(logger, input_video_path, target_format, logo_file, icon_file, socialmediahandle, enable_captions):
    """Run rendering script for a specific target format"""
    logger.info(f"Starting rendering: format={target_format}")
    
    rendering_script = "/opt/n8n_scripts/video/n8n-video-processing-pipeline/functions/02_render-captions-and-layout-into-video.sh"
    cmd = [
        rendering_script,
        "-inputvideo", input_video_path,
        "-version", target_format
    ]
    
    # Add optional parameters (only if not empty)
    if logo_file:
        cmd.extend(["-logo", logo_file])
    if icon_file:
        cmd.extend(["-icon", icon_file])
    if socialmediahandle:
        cmd.extend(["-socialmediahandle", socialmediahandle])
    if enable_captions:
        cmd.extend(["-captions", enable_captions])
    
    logger.info(f"Running rendering command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, cwd="/opt/n8n_scripts/video/n8n-video-processing-pipeline")
        
        if result.returncode == 0:
            logger.info(f"Rendering completed successfully for {target_format}")
            logger.info(f"Rendering stdout: {result.stdout}")
            
            # Generate expected output path based on naming pattern: {input_name}_{version}_{ratio}.mp4
            input_filename = Path(input_video_path).stem
            
            # Map format to ratio
            format_ratios = {
                'portrait': '9x16',
                'landscape': '16x9', 
                'square': '1x1'
            }
            ratio = format_ratios.get(target_format, '16x9')
            
            output_filename = f"{input_filename}_{target_format}_{ratio}.mp4"
            output_path = f"/opt/n8n_scripts/video/_output-files/{output_filename}"
            
            # Verify the file exists
            if os.path.exists(output_path):
                logger.info(f"Found output file: {output_path}")
                return output_path
            else:
                logger.warning(f"Expected output file not found: {output_path}")
                # Also check if there are any .mp4 files in output directory
                output_dir = Path("/opt/n8n_scripts/video/_output-files/")
                if output_dir.exists():
                    mp4_files = list(output_dir.glob("*.mp4"))
                    logger.info(f"Available .mp4 files in output directory: {[f.name for f in mp4_files]}")
                return ""
            
        else:
            logger.error(f"Rendering failed for {target_format} with return code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            logger.error(f"Stdout: {result.stdout}")
            return ""
            
    except subprocess.TimeoutExpired:
        logger.error(f"Rendering timed out after 30 minutes for {target_format}")
        return ""
    except Exception as e:
        logger.error(f"Rendering error for {target_format}: {str(e)}")
        return ""


def main():
    """Main pipeline orchestration"""
    logger = setup_logging()
    args = parse_args()
    
    logger.info(f"Starting video processing pipeline with args: {vars(args)}")
    
    # Convert input paths from container to host
    input_video_path = convert_path_to_host(args.input_file)
    
    # Parse target formats
    requested_formats = [fmt.strip() for fmt in args.target_formats.split(',')]
    all_formats = ['portrait', 'landscape', 'square']
    
    logger.info(f"Requested formats: {requested_formats}")
    logger.info(f"Converted input video path: {input_video_path}")
    
    # Step 1: Run transcription if captions enabled
    if args.enable_captions.lower() == 'true':
        transcription_success = run_transcription(logger, input_video_path, args.style, args.brand)
        if not transcription_success:
            logger.warning("Transcription failed, continuing without captions")
    else:
        logger.info("Captions disabled, skipping transcription")
    
    # Step 2: Run rendering for each requested format
    results = {}
    
    for format_name in all_formats:
        if format_name in requested_formats:
            logger.info(f"Processing requested format: {format_name}")
            output_path = run_rendering(
                logger, 
                input_video_path, 
                format_name, 
                args.logo_file, 
                args.icon_file, 
                args.socialmediahandle, 
                args.enable_captions
            )
            
            # Convert output path back to container path for n8n
            if output_path:
                container_path = convert_path_to_container(output_path)
                results[f"{format_name}_video"] = container_path
                logger.info(f"Successfully generated {format_name}: {container_path}")
            else:
                results[f"{format_name}_video"] = ""
                logger.warning(f"Failed to generate {format_name}")
        else:
            results[f"{format_name}_video"] = ""
            logger.info(f"Format {format_name} not requested, returning empty")
    
    # Step 3: Return clean JSON results (no logging to stdout!)
    final_result = {
        "success": True,
        "portrait_video": results["portrait_video"],
        "landscape_video": results["landscape_video"], 
        "square_video": results["square_video"]
    }
    
    logger.info(f"Pipeline completed. Results: {final_result}")
    
    # CRITICAL: Only clean JSON to stdout for n8n
    print(json.dumps(final_result, indent=2))


if __name__ == "__main__":
    main()
