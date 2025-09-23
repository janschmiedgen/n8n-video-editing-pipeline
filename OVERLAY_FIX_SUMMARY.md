# 🔧 Overlay Visibility & Naming Fix

## 🎯 **Issues Identified & Resolved**

### 1. **Overlay Visibility Issue** ✅ FIXED
**Problem**: Overlays (logo, icon, social media handle) were being applied but were very subtle or hard to see.

**Root Cause**: Logo opacity was set to 40% (`LOGO_OPACITY="0.4"`) making it barely visible.

**Solution**: 
- Increased logo opacity from 40% to 80% in both landscape and portrait configurations
- This makes overlays much more visible while still maintaining professional appearance

**Files Modified**:
- `config-videolayouts/landscape_config.conf`: `LOGO_OPACITY="0.4"` → `LOGO_OPACITY="0.8"`
- `config-videolayouts/portrait_config.conf`: `LOGO_OPACITY="0.4"` → `LOGO_OPACITY="0.8"`

### 2. **Naming Inconsistency Issue** ✅ FIXED
**Problem**: Inconsistent parameter naming between "hashtag_file" and "socialmediahandle_file" throughout the codebase.

**Solution**: Standardized on `socialmediahandle_file` everywhere (more descriptive and matches script parameter).

**Files Updated**:
- `n8n-video-api.py`: Fixed function parameters and variable names
- `README.md`: Updated API examples
- `test_api.py`: Updated test data
- `TASK_4_COMPLETED.md`: Updated examples

---

## 🎬 **Overlay Processing Confirmed Working**

The pipeline correctly processes all three overlay types:

### **Logo Overlay** ✅
- **Position**: Top-right (landscape) / Top-left (portrait)  
- **Size**: ~8.2% of frame width (landscape) / ~16.5% (portrait)
- **Opacity**: 80% (improved from 40%)
- **FFmpeg**: `colorchannelmixer=aa=0.8[logo]`

### **Icon Overlay** ✅  
- **Position**: Top-left (landscape) / Top-right (portrait)
- **Size**: ~5% of frame width (landscape) / ~5.6% (portrait)
- **Opacity**: 100%
- **FFmpeg**: Applied without opacity filter

### **Social Media Handle Overlay** ✅
- **Position**: Bottom-left (above captions)
- **Size**: ~16% of frame width (landscape) / ~28.6% (portrait) 
- **Opacity**: 100%
- **FFmpeg**: Applied at bottom position

---

## 🧪 **Verification Results**

### **FFmpeg Filter Chain Verified**:
```
[1:v]scale=158:-1:flags=lanczos,format=rgba,colorchannelmixer=aa=0.8[logo];
[base][logo]overlay=W-w-45:35[with_logo];
[2:v]scale=96:-1:flags=lanczos[icon];
[with_logo][icon]overlay=44:50[with_icon];
[3:v]scale=309:-1:flags=lanczos[hashtag];
[with_icon][hashtag]overlay=0:H-h-0[with_hashtag]
```

### **Processing Log Confirmed**:
```
Added logo overlay: codify-logo.png (opacity: 0.8)
Added icon overlay: codify-icon.png (opacity: 1)  
Added social media handle overlay: codify-sm-handle.png (opacity: 1)
```

---

## 📋 **Updated API Parameters**

### **Correct JSON Input** (Fixed):
```json
[
  {
    "input_file": "/mnt/n8n_host_scripts/video/_input-files/video.mp4",
    "target_formats": ["portrait", "landscape"],
    "logo_file": "codify-logo.png",
    "icon_file": "codify-icon.png",
    "socialmediahandle_file": "codify-sm-handle.png",  ← FIXED NAMING
    "enable_captions": true,
    "captiontemplate": "-style social -brand codify"
  }
]
```

### **Render Script Parameters** (Confirmed):
```bash
bash functions/02_render-captions-and-layout-into-video.sh \
  -inputvideo video.mp4 \
  -version landscape \
  -logo codify-logo.png \
  -icon codify-icon.png \
  -socialmediahandle codify-sm-handle.png  ← CORRECT PARAMETER
```

---

## 🎯 **Testing Instructions**

To verify overlays are now visible:

1. **Run CLI Test**:
   ```bash
   python3 test_pipeline_cli.py render
   ```

2. **Check Output Video**:
   - Should show logo in top-right (landscape) with 80% opacity
   - Should show icon in top-left (landscape) with full opacity  
   - Should show social media handle at bottom-left with full opacity
   - All overlays should be clearly visible now

3. **API Test** (when ready):
   ```bash
   ./start_api.sh start
   ./start_api.sh test
   ```

---

## ⚙️ **Configuration Flexibility**

You can adjust overlay visibility by modifying the config files:

### **Landscape**: `config-videolayouts/landscape_config.conf`
### **Portrait**: `config-videolayouts/portrait_config.conf`

**Opacity Values**:
- `1.0` = 100% (fully opaque)
- `0.8` = 80% (current setting - good visibility)
- `0.4` = 40% (previous setting - too subtle)
- `0.0` = 0% (invisible)

**Position Settings**:
- `LOGO_POSITION`, `ICON_POSITION`, `HASHTAG_POSITION`
- Values: `tl` (top-left), `tr` (top-right), `bl` (bottom-left), `br` (bottom-right)

---

## 🎉 **Summary**

✅ **Overlay visibility**: Fixed by increasing opacity from 40% to 80%  
✅ **Naming consistency**: All parameters now use `socialmediahandle_file`  
✅ **Processing verified**: FFmpeg filter chains show correct overlay application  
✅ **Documentation updated**: All examples use correct parameter names  

**The overlays should now be clearly visible in your rendered videos!** 🚀

---

*Fixed: September 23, 2025*  
*Next test should show visible overlays with improved opacity*