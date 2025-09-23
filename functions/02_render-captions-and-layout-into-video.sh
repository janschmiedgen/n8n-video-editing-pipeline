#!/bin/bash

# 02_render-captions-and-layout-into-video.sh
# Video rendering script for n8n pipeline
# Uses ASS caption files and applies brand overlays for different video formats
# Usage: ./02_render-captions-and-layout-into-video.sh -inputvideo video.mp4 -logo logo.png -icon icon.png -socialmediahandle handle.png -captions true -version portrait

set -euo pipefail

# Script directory for config files
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
CONFIG_DIR="$SCRIPT_DIR/../config-videolayouts"
OVERLAY_DIR="$SCRIPT_DIR/../overlay-files"
OUTPUT_DIR="/opt/n8n_scripts/video/_output-files"

# Default values
INPUT_VIDEO=""
LOGO_FILE=""
ICON_FILE=""
SOCIALMEDIA_FILE=""
CAPTIONS_ENABLED="true"
VERSION=""

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a render.log
}

# Error handling
error_exit() {
    log "ERROR: $1"
    echo "ERROR"
    exit 1
}

# Success function
success_exit() {
    log "SUCCESS: Video rendering completed"
    echo "SUCCESS"
    exit 0
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -inputvideo)
                INPUT_VIDEO="$2"
                shift 2
                ;;
            -logo)
                LOGO_FILE="$2"
                shift 2
                ;;
            -icon)
                ICON_FILE="$2"
                shift 2
                ;;
            -socialmediahandle)
                SOCIALMEDIA_FILE="$2"
                shift 2
                ;;
            -captions)
                CAPTIONS_ENABLED="$2"
                shift 2
                ;;
            -version)
                VERSION="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 -inputvideo VIDEO -logo LOGO -icon ICON -socialmediahandle HANDLE -captions true/false -version portrait/landscape/square"
                exit 0
                ;;
            *)
                error_exit "Unknown parameter: $1"
                ;;
        esac
    done
}

# Validate arguments
validate_arguments() {
    [[ -z "$INPUT_VIDEO" ]] && error_exit "Missing required parameter: -inputvideo"
    [[ -z "$VERSION" ]] && error_exit "Missing required parameter: -version"
    [[ ! -f "$INPUT_VIDEO" ]] && error_exit "Input video file not found: $INPUT_VIDEO"
    
    if [[ "$VERSION" != "portrait" && "$VERSION" != "landscape" && "$VERSION" != "square" ]]; then
        error_exit "Invalid version. Must be: portrait, landscape, or square"
    fi
    
    if [[ "$CAPTIONS_ENABLED" != "true" && "$CAPTIONS_ENABLED" != "false" ]]; then
        error_exit "Invalid captions value. Must be: true or false"
    fi
}

# Load configuration for the specified version
load_config() {
    local config_file="$CONFIG_DIR/${VERSION}_config.conf"
    
    if [[ ! -f "$config_file" ]]; then
        log "WARNING: Config file not found: $config_file, using defaults"
        return
    fi
    
    log "Loading configuration from: $config_file"
    source "$config_file"
    
    log "Configuration loaded - Target: ${OUTPUT_WIDTH}x${OUTPUT_HEIGHT}"
}

# Find caption files
find_caption_files() {
    local input_dir=$(dirname "$INPUT_VIDEO")
    local base_name=$(basename "$INPUT_VIDEO" | sed 's/\.[^.]*$//')
    
    # Select format-specific ASS file based on output version
    case "$VERSION" in
        "portrait")
            ASS_FILE="$input_dir/${base_name}_captions_portrait.ass"
            ;;
        "landscape")
            ASS_FILE="$input_dir/${base_name}_captions_landscape.ass"
            ;;
        "square")
            ASS_FILE="$input_dir/${base_name}_captions_square.ass"
            ;;
    esac
    
    # Fallback to generic ASS file if format-specific doesn't exist
    if [[ "$CAPTIONS_ENABLED" == "true" ]]; then
        if [[ ! -f "$ASS_FILE" ]]; then
            log "WARNING: Format-specific ASS file not found: $ASS_FILE"
            # Try fallback to generic file
            FALLBACK_ASS="$input_dir/${base_name}_captions.ass"
            if [[ -f "$FALLBACK_ASS" ]]; then
                ASS_FILE="$FALLBACK_ASS"
                log "Using fallback ASS file: $ASS_FILE"
            else
                log "WARNING: No ASS files found, disabling captions"
                CAPTIONS_ENABLED="false"
            fi
        else
            log "Found format-specific ASS file: $ASS_FILE"
        fi
    fi
    
    FILTER_FILE="$input_dir/${base_name}_filters.txt"
}

# Calculate overlay positions based on config
calculate_positions() {
    # Logo position calculation
    if [[ -n "$LOGO_FILE" && -f "$OVERLAY_DIR/$LOGO_FILE" ]]; then
        case "$LOGO_POSITION" in
            "tl") LOGO_X="$LOGO_MARGIN_X"; LOGO_Y="$LOGO_MARGIN_Y" ;;
            "tr") LOGO_X="W-w-$LOGO_MARGIN_X"; LOGO_Y="$LOGO_MARGIN_Y" ;;
            "bl") LOGO_X="$LOGO_MARGIN_X"; LOGO_Y="H-h-$LOGO_MARGIN_Y" ;;
            "br") LOGO_X="W-w-$LOGO_MARGIN_X"; LOGO_Y="H-h-$LOGO_MARGIN_Y" ;;
            *) LOGO_X="$LOGO_MARGIN_X"; LOGO_Y="$LOGO_MARGIN_Y" ;;
        esac
        LOGO_POS="$LOGO_X:$LOGO_Y"
        log "Logo position: $LOGO_POS (size: $LOGO_SIZE)"
    fi
    
    # Icon position calculation
    if [[ -n "$ICON_FILE" && -f "$OVERLAY_DIR/$ICON_FILE" ]]; then
        case "$ICON_POSITION" in
            "tl") ICON_X="$ICON_MARGIN_X"; ICON_Y="$ICON_MARGIN_Y" ;;
            "tr") ICON_X="W-w-$ICON_MARGIN_X"; ICON_Y="$ICON_MARGIN_Y" ;;
            "bl") ICON_X="$ICON_MARGIN_X"; ICON_Y="H-h-$ICON_MARGIN_Y" ;;
            "br") ICON_X="W-w-$ICON_MARGIN_X"; ICON_Y="H-h-$ICON_MARGIN_Y" ;;
            *) ICON_X="$ICON_MARGIN_X"; ICON_Y="$ICON_MARGIN_Y" ;;
        esac
        ICON_POS="$ICON_X:$ICON_Y"
        log "Icon position: $ICON_POS (size: $ICON_SIZE)"
    fi
    
    # Social media handle position calculation  
    if [[ -n "$SOCIALMEDIA_FILE" && -f "$OVERLAY_DIR/$SOCIALMEDIA_FILE" ]]; then
        case "$HASHTAG_POSITION" in
            "tl") HASHTAG_X="$HASHTAG_MARGIN_X"; HASHTAG_Y="$HASHTAG_MARGIN_Y" ;;
            "tr") HASHTAG_X="W-w-$HASHTAG_MARGIN_X"; HASHTAG_Y="$HASHTAG_MARGIN_Y" ;;
            "bl") HASHTAG_X="$HASHTAG_MARGIN_X"; HASHTAG_Y="H-h-$HASHTAG_MARGIN_Y" ;;
            "br") HASHTAG_X="W-w-$HASHTAG_MARGIN_X"; HASHTAG_Y="H-h-$HASHTAG_MARGIN_Y" ;;
            *) HASHTAG_X="$HASHTAG_MARGIN_X"; HASHTAG_Y="H-h-$HASHTAG_MARGIN_Y" ;;
        esac
        HASHTAG_POS="$HASHTAG_X:$HASHTAG_Y"
        log "Social media handle position: $HASHTAG_POS (size: $HASHTAG_SIZE)"
    fi
}

# Build FFmpeg filter chain
build_filter_chain() {
    # Get input video dimensions and rotation
    local input_info=$(ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$INPUT_VIDEO")
    local raw_width=$(echo $input_info | cut -d',' -f1)
    local raw_height=$(echo $input_info | cut -d',' -f2)
    
    # Check for rotation metadata
    local rotation=$(ffprobe -v quiet -select_streams v:0 -show_entries stream_side_data=rotation -of default=noprint_wrappers=1:nokey=1 "$INPUT_VIDEO" 2>/dev/null || echo "0")
    
    # Apply rotation to get effective dimensions
    local input_width=$raw_width
    local input_height=$raw_height
    if [[ "$rotation" == "-90" || "$rotation" == "90" || "$rotation" == "270" ]]; then
        # Swap width and height for 90° rotations
        input_width=$raw_height
        input_height=$raw_width
        log "Detected rotation: ${rotation}° - Effective dimensions: ${input_width}x${input_height} (from raw ${raw_width}x${raw_height})"
    else
        log "No rotation detected - Using raw dimensions: ${input_width}x${input_height}"
    fi
    
    # Calculate aspect ratios using effective dimensions
    local input_aspect=$(awk "BEGIN {printf \"%.4f\", $input_width / $input_height}")
    local output_aspect=$(awk "BEGIN {printf \"%.4f\", $OUTPUT_WIDTH / $OUTPUT_HEIGHT}")
    
    log "Input: ${input_width}x${input_height} (aspect: $input_aspect), Output: ${OUTPUT_WIDTH}x${OUTPUT_HEIGHT} (aspect: $output_aspect)"
    
    # Build base layer with blurred background for aspect ratio mismatches
    local filter_chain
    if (( $(awk "BEGIN {print (($input_aspect - $output_aspect) > 0.01 || ($output_aspect - $input_aspect) > 0.01)}") )); then
        # Different aspect ratios - use blurred background
        log "Aspect ratio mismatch detected - using blurred background"
        filter_chain="[0:v]scale=${OUTPUT_WIDTH}:${OUTPUT_HEIGHT}:force_original_aspect_ratio=increase,crop=${OUTPUT_WIDTH}:${OUTPUT_HEIGHT},gblur=sigma=20,eq=brightness=-0.3[bg];"
        filter_chain="${filter_chain}[0:v]scale=${OUTPUT_WIDTH}:${OUTPUT_HEIGHT}:force_original_aspect_ratio=decrease[fg];"
        filter_chain="${filter_chain}[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
    else
        # Same aspect ratios - simple scale
        log "Matching aspect ratios - using simple scale"
        filter_chain="[0:v]scale=${OUTPUT_WIDTH}:${OUTPUT_HEIGHT}[base]"
    fi
    
    local input_index=1
    local overlay_inputs=""
    local current_output="[base]"
    
    # Add logo overlay if specified
    if [[ -n "$LOGO_FILE" && -f "$OVERLAY_DIR/$LOGO_FILE" ]]; then
        overlay_inputs="$overlay_inputs -i '$OVERLAY_DIR/$LOGO_FILE'"
        local logo_scale=$(awk "BEGIN {printf \"%.0f\", $OUTPUT_WIDTH * $LOGO_SIZE}")
        # Apply opacity if less than 1.0
        if (( $(awk "BEGIN {print ($LOGO_OPACITY < 1.0)}") )); then
            filter_chain="$filter_chain;[$input_index:v]scale=$logo_scale:-1:flags=lanczos,format=rgba,colorchannelmixer=aa=$LOGO_OPACITY[logo];${current_output}[logo]overlay=$LOGO_POS[with_logo]"
        else
            filter_chain="$filter_chain;[$input_index:v]scale=$logo_scale:-1:flags=lanczos[logo];${current_output}[logo]overlay=$LOGO_POS[with_logo]"
        fi
        current_output="[with_logo]"
        ((input_index++))
        log "Added logo overlay: $LOGO_FILE (opacity: $LOGO_OPACITY)"
    fi
    
    # Add icon overlay if specified
    if [[ -n "$ICON_FILE" && -f "$OVERLAY_DIR/$ICON_FILE" ]]; then
        overlay_inputs="$overlay_inputs -i '$OVERLAY_DIR/$ICON_FILE'"
        local icon_scale=$(awk "BEGIN {printf \"%.0f\", $OUTPUT_WIDTH * $ICON_SIZE}")
        # Apply opacity if less than 1.0
        if (( $(awk "BEGIN {print ($ICON_OPACITY < 1.0)}") )); then
            filter_chain="$filter_chain;[$input_index:v]scale=$icon_scale:-1:flags=lanczos,format=rgba,colorchannelmixer=aa=$ICON_OPACITY[icon];${current_output}[icon]overlay=$ICON_POS[with_icon]"
        else
            filter_chain="$filter_chain;[$input_index:v]scale=$icon_scale:-1:flags=lanczos[icon];${current_output}[icon]overlay=$ICON_POS[with_icon]"
        fi
        current_output="[with_icon]"
        ((input_index++))
        log "Added icon overlay: $ICON_FILE (opacity: $ICON_OPACITY)"
    fi
    
    # Add social media handle overlay if specified
    if [[ -n "$SOCIALMEDIA_FILE" && -f "$OVERLAY_DIR/$SOCIALMEDIA_FILE" ]]; then
        overlay_inputs="$overlay_inputs -i '$OVERLAY_DIR/$SOCIALMEDIA_FILE'"
        local hashtag_scale=$(awk "BEGIN {printf \"%.0f\", $OUTPUT_WIDTH * $HASHTAG_SIZE}")
        # Apply opacity if less than 1.0
        if (( $(awk "BEGIN {print ($HASHTAG_OPACITY < 1.0)}") )); then
            filter_chain="$filter_chain;[$input_index:v]scale=$hashtag_scale:-1:flags=lanczos,format=rgba,colorchannelmixer=aa=$HASHTAG_OPACITY[hashtag];${current_output}[hashtag]overlay=$HASHTAG_POS[with_hashtag]"
        else
            filter_chain="$filter_chain;[$input_index:v]scale=$hashtag_scale:-1:flags=lanczos[hashtag];${current_output}[hashtag]overlay=$HASHTAG_POS[with_hashtag]"
        fi
        current_output="[with_hashtag]"
        ((input_index++))
        log "Added social media handle overlay: $SOCIALMEDIA_FILE (opacity: $HASHTAG_OPACITY)"
    fi
    
    # Add ASS subtitles if enabled
    if [[ "$CAPTIONS_ENABLED" == "true" && -f "$ASS_FILE" ]]; then
        filter_chain="$filter_chain;${current_output}ass='$ASS_FILE'[final]"
        log "Added ASS subtitles: $ASS_FILE"
    else
        # Rename current output to final
        filter_chain="${filter_chain};${current_output}copy[final]"
    fi
    
    # Export variables for FFmpeg command
    OVERLAY_INPUTS="$overlay_inputs"
    FILTER_CHAIN="$filter_chain"
}

# Generate output filename with hardcoded suffixes
generate_output_filename() {
    local base_name=$(basename "$INPUT_VIDEO" | sed 's/\.[^.]*$//')
    
    case "$VERSION" in
        "portrait")
            OUTPUT_FILE="$OUTPUT_DIR/${base_name}_portrait_9x16.mp4"
            ;;
        "landscape") 
            OUTPUT_FILE="$OUTPUT_DIR/${base_name}_landscape_16x9.mp4"
            ;;
        "square")
            OUTPUT_FILE="$OUTPUT_DIR/${base_name}_square_1x1.mp4"
            ;;
    esac
    
    log "Output file: $OUTPUT_FILE"
}

# Execute FFmpeg rendering
render_video() {
    mkdir -p "$OUTPUT_DIR"
    
    log "Starting FFmpeg rendering..."
    log "Filter chain: $FILTER_CHAIN"
    
    # Build FFmpeg command
    local ffmpeg_cmd="ffmpeg -i '$INPUT_VIDEO' $OVERLAY_INPUTS -filter_complex '$FILTER_CHAIN' -map '[final]'"
    
    # Add audio if present
    if ffprobe -v quiet -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$INPUT_VIDEO" 2>/dev/null | grep -q audio; then
        ffmpeg_cmd="$ffmpeg_cmd -map 0:a -c:a aac -b:a 160k -ar 48000"
        log "Audio stream detected, copying audio"
    else
        log "No audio stream detected"
    fi
    
    # Add video encoding settings
    ffmpeg_cmd="$ffmpeg_cmd -c:v libx264 -crf 22 -preset medium -movflags +faststart -y '$OUTPUT_FILE'"
    
    log "Executing FFmpeg command..."
    
    # Execute with error handling
    if eval $ffmpeg_cmd 2>> render.log; then
        if [[ -f "$OUTPUT_FILE" ]]; then
            local file_size=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
            log "Video rendered successfully: $(basename "$OUTPUT_FILE") ($file_size)"
            return 0
        else
            error_exit "FFmpeg completed but output file not found"
        fi
    else
        error_exit "FFmpeg rendering failed - check render.log for details"
    fi
}

# Main execution
main() {
    log "Starting video rendering process"
    
    parse_arguments "$@"
    log "Parameters: inputvideo=$INPUT_VIDEO, logo=$LOGO_FILE, icon=$ICON_FILE, socialmedia=$SOCIALMEDIA_FILE, captions=$CAPTIONS_ENABLED, version=$VERSION"
    validate_arguments
    load_config
    find_caption_files
    calculate_positions
    build_filter_chain
    generate_output_filename
    render_video
    
    success_exit
}

# Execute main function with all arguments
main "$@"