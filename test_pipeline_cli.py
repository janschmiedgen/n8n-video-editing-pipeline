#!/usr/bin/env python3
"""
CLI Test Script for n8n Video Processing Pipeline
================================================

Tests the core pipeline functionality directly without the Flask API.
This allows testing the transcription and rendering scripts independently.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

# Configuration
SCRIPT_DIR = '/opt/n8n_scripts/video/n8n-video-processing-pipeline'
FUNCTIONS_DIR = os.path.join(SCRIPT_DIR, 'functions')
OVERLAY_FILES_DIR = os.path.join(SCRIPT_DIR, 'overlay-files')
OUTPUT_DIR = '/opt/n8n_scripts/video/_output-files'
INPUT_DIR = '/opt/n8n_scripts/video/_input-files'
TRANSCRIPTION_SCRIPT = os.path.join(FUNCTIONS_DIR, '01_transcribe-video-to-ass-with-super-whisper.py')
RENDERING_SCRIPT = os.path.join(FUNCTIONS_DIR, '02_render-captions-and-layout-into-video.sh')

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🎬 {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step}: {description}")
    print("-" * 40)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def check_prerequisites():
    """Check if all required files and directories exist"""
    print_step(1, "Checking Prerequisites")
    
    checks = [
        (TRANSCRIPTION_SCRIPT, "Transcription script"),
        (RENDERING_SCRIPT, "Rendering script"),
        (OVERLAY_FILES_DIR, "Overlay files directory"),
        (INPUT_DIR, "Input files directory")
    ]
    
    all_good = True
    for path, description in checks:
        if os.path.exists(path):
            print_success(f"{description}: {path}")
        else:
            print_error(f"{description} not found: {path}")
            all_good = False
    
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print_success(f"Created output directory: {OUTPUT_DIR}")
    else:
        print_success(f"Output directory exists: {OUTPUT_DIR}")
    
    return all_good

def find_test_video():
    """Find a test video file"""
    print_step(2, "Looking for Test Video")
    
    # Common video extensions
    extensions = ['.mp4', '.MOV', '.mov', '.avi', '.mkv']
    
    if os.path.exists(INPUT_DIR):
        for file in os.listdir(INPUT_DIR):
            if any(file.endswith(ext) for ext in extensions):
                video_path = os.path.join(INPUT_DIR, file)
                print_success(f"Found test video: {video_path}")
                return video_path
    
    print_warning("No test video found in input directory")
    print(f"Available files in {INPUT_DIR}:")
    if os.path.exists(INPUT_DIR):
        for file in os.listdir(INPUT_DIR):
            print(f"  - {file}")
    else:
        print("  (directory doesn't exist)")
    
    return None

def test_transcription(video_path, style="clean", brand="codify"):
    """Test the transcription script"""
    print_step(3, "Testing Transcription")
    
    cmd = [
        'python3', TRANSCRIPTION_SCRIPT,
        '-inputfile', video_path,
        '-style', style,
        '-brand', brand
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print("Starting transcription (this may take 30-60 seconds)...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=SCRIPT_DIR, 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Transcription took {duration:.1f} seconds")
        
        if result.returncode == 0:
            print_success("Transcription completed successfully!")
            print("Output:")
            print(result.stdout)
            
            # Check for generated ASS files
            video_basename = os.path.splitext(os.path.basename(video_path))[0]
            ass_files = [
                f"{video_basename}_captions_portrait.ass",
                f"{video_basename}_captions_landscape.ass",
                f"{video_basename}_captions_square.ass"
            ]
            
            for ass_file in ass_files:
                ass_path = os.path.join(SCRIPT_DIR, ass_file)
                if os.path.exists(ass_path):
                    print_success(f"Generated: {ass_file}")
                else:
                    print_warning(f"Missing: {ass_file}")
            
            return True
        else:
            print_error("Transcription failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Transcription timed out after 5 minutes")
        return False
    except Exception as e:
        print_error(f"Transcription error: {str(e)}")
        return False

def test_rendering(video_path, target_format="landscape"):
    """Test the rendering script for a specific format"""
    print_step(4, f"Testing Rendering ({target_format})")
    
    # Find available overlay files
    overlay_files = {}
    if os.path.exists(OVERLAY_FILES_DIR):
        for file in os.listdir(OVERLAY_FILES_DIR):
            if file.endswith('.png'):
                if 'logo' in file.lower():
                    overlay_files['logo'] = os.path.join(OVERLAY_FILES_DIR, file)
                elif 'icon' in file.lower():
                    overlay_files['icon'] = os.path.join(OVERLAY_FILES_DIR, file)
                elif any(x in file.lower() for x in ['handle', 'hashtag', 'sm']):
                    overlay_files['socialmediahandle'] = os.path.join(OVERLAY_FILES_DIR, file)
    
    cmd = [
        'bash', RENDERING_SCRIPT,
        '-inputvideo', video_path,
        '-version', target_format
    ]
    
    # Add overlay files if found
    if 'logo' in overlay_files:
        cmd.extend(['-logo', overlay_files['logo']])
        print_success(f"Using logo: {overlay_files['logo']}")
    
    if 'icon' in overlay_files:
        cmd.extend(['-icon', overlay_files['icon']])
        print_success(f"Using icon: {overlay_files['icon']}")
    
    if 'socialmediahandle' in overlay_files:
        cmd.extend(['-socialmediahandle', overlay_files['socialmediahandle']])
        print_success(f"Using social media handle: {overlay_files['socialmediahandle']}")
    
    print(f"Command: {' '.join(cmd)}")
    print("Starting rendering (this may take 1-2 minutes)...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=600
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Rendering took {duration:.1f} seconds")
        
        if result.returncode == 0:
            print_success(f"Rendering completed successfully for {target_format}!")
            print("Output:")
            print(result.stdout)
            
            # Try to find the output file
            video_basename = os.path.splitext(os.path.basename(video_path))[0]
            expected_output = os.path.join(OUTPUT_DIR, f"{video_basename}_{target_format}.mp4")
            
            # Check for the expected output first
            if os.path.exists(expected_output):
                file_size = os.path.getsize(expected_output) / (1024 * 1024)  # MB
                print_success(f"Generated video: {expected_output} ({file_size:.1f} MB)")
                return expected_output
            
            # Look for any output file with the video basename and format in the name
            if os.path.exists(OUTPUT_DIR):
                for file in os.listdir(OUTPUT_DIR):
                    if video_basename in file and target_format in file and file.endswith('.mp4'):
                        actual_output = os.path.join(OUTPUT_DIR, file)
                        file_size = os.path.getsize(actual_output) / (1024 * 1024)  # MB
                        print_success(f"Generated video: {actual_output} ({file_size:.1f} MB)")
                        return actual_output
            
            print_warning(f"No output file found for {target_format} format")
            return None
        else:
            print_error(f"Rendering failed for {target_format}!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return None
            
    except subprocess.TimeoutExpired:
        print_error("Rendering timed out after 10 minutes")
        return None
    except Exception as e:
        print_error(f"Rendering error: {str(e)}")
        return None

def run_full_test():
    """Run the complete pipeline test"""
    print_header("n8n Video Processing Pipeline - CLI Test")
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please fix issues above.")
        return False
    
    # Step 2: Find test video
    video_path = find_test_video()
    if not video_path:
        print_error("No test video found. Please add a video file to:")
        print(f"  {INPUT_DIR}")
        return False
    
    # Step 3: Test transcription
    transcription_success = test_transcription(video_path, style="clean", brand="codify")
    
    # Step 4: Test rendering (try multiple formats)
    formats_to_test = ["landscape", "portrait"]  # Test 2 formats for speed
    rendering_results = {}
    
    for format_name in formats_to_test:
        output_path = test_rendering(video_path, format_name)
        rendering_results[format_name] = output_path
    
    # Summary
    print_header("Test Results Summary")
    print(f"📁 Test video: {video_path}")
    print(f"🎯 Transcription: {'✅ SUCCESS' if transcription_success else '❌ FAILED'}")
    
    for format_name, output_path in rendering_results.items():
        status = '✅ SUCCESS' if output_path else '❌ FAILED'
        print(f"🎬 Rendering ({format_name}): {status}")
        if output_path:
            print(f"   → {output_path}")
    
    # Overall success
    overall_success = transcription_success and all(rendering_results.values())
    
    if overall_success:
        print_success("\n🎉 All tests passed! Your pipeline is working correctly.")
        print("\nNext steps:")
        print("1. Start the Flask API: ./start_api.sh start")
        print("2. Test the API: ./start_api.sh test")
        print("3. Integrate with n8n using the /process endpoint")
    else:
        print_error("\n💥 Some tests failed. Check the logs above for details.")
        if transcription_success:
            print("✅ Transcription is working")
        if any(rendering_results.values()):
            print("✅ Some rendering formats are working")
    
    return overall_success

def test_transcription_only():
    """Test only transcription"""
    print_header("Transcription Only Test")
    
    if not check_prerequisites():
        return False
    
    video_path = find_test_video()
    if not video_path:
        return False
    
    return test_transcription(video_path)

def test_rendering_only():
    """Test only rendering"""
    print_header("Rendering Only Test")
    
    if not check_prerequisites():
        return False
    
    video_path = find_test_video()
    if not video_path:
        return False
    
    # Test landscape format
    output_path = test_rendering(video_path, "landscape")
    return output_path is not None

def show_usage():
    """Show usage information"""
    print("Usage: python3 test_pipeline_cli.py [option]")
    print()
    print("Options:")
    print("  full         - Run complete pipeline test (default)")
    print("  transcribe   - Test transcription only")
    print("  render       - Test rendering only")
    print("  check        - Check prerequisites only")
    print()
    print("Examples:")
    print("  python3 test_pipeline_cli.py")
    print("  python3 test_pipeline_cli.py transcribe")
    print("  python3 test_pipeline_cli.py render")

if __name__ == "__main__":
    # Change to script directory
    os.chdir(SCRIPT_DIR)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "full"
    
    if command == "full":
        success = run_full_test()
    elif command == "transcribe":
        success = test_transcription_only()
    elif command == "render":
        success = test_rendering_only()
    elif command == "check":
        success = check_prerequisites()
    elif command in ["help", "--help", "-h"]:
        show_usage()
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        show_usage()
        sys.exit(1)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)