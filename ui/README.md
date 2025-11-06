# QWAMOS Hypervisor UI

**Flutter Implementation with Neon Shaders & Motion Blur Effects**

---

## 🎨 Overview

This is the official UI implementation for the QWAMOS (Qubes+Whonix Advanced Mobile OS) Hypervisor Layer.

**Status:** Core Implementation Complete (60%)

See `IMPLEMENTATION_GUIDE.md` for complete specification.

---

## 📁 Implemented Components

### Theme System ✅
- `pubspec.yaml` - Dependencies configuration
- `lib/theme/colors.dart` - Color palette & gradients
- `lib/theme/typography.dart` - Text styles
- `lib/theme/dark_theme.dart` - Material theme
- `lib/theme/glow_effects.dart` - Visual effect utilities

### Shaders ✅
- `shaders/neon_overlay.frag` - GPU neon glow shader
- `shaders/motion_blur.frag` - Motion blur shader
- `shaders/noise_flicker.frag` - Holographic grain shader

### Widgets ✅
- `lib/widgets/security_status.dart` - Security status panel
- `lib/widgets/veracrypt_volumes.dart` - VeraCrypt volume management
- `lib/widgets/encryption_manager.dart` - Key generation interface
- `lib/widgets/network_gateway.dart` - TOR/I2P/DNS status
- `lib/widgets/airgap_controls.dart` - Airgap toggle controls
- `lib/widgets/osint_tools.dart` - OSINT tools grid
- `lib/widgets/quick_actions.dart` - VM quick actions
- `lib/widgets/vm_list.dart` - Virtual machine list

### Pages ✅
- `lib/main.dart` - App entry point
- `lib/pages/main_dashboard.dart` - Main dashboard page

---

## 🚀 Installation & Setup

### Prerequisites

1. **Install Flutter** (if not already installed):
   ```bash
   # For Termux/Android
   pkg install flutter

   # Or download from flutter.dev
   ```

2. **Verify Flutter installation**:
   ```bash
   flutter doctor
   ```

### Build Instructions

1. **Navigate to the project**:
   ```bash
   cd /data/data/com.termux/files/home/QWAMOS/ui
   ```

2. **Get dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run on connected device**:
   ```bash
   flutter run
   ```

4. **Build APK for release**:
   ```bash
   flutter build apk --release
   ```

   Output: `build/app/outputs/flutter-apk/app-release.apk`

5. **Build for web (demo)**:
   ```bash
   flutter build web
   ```

---

## 🎯 Next Steps

### Remaining Work (40%)
- [ ] HAL-GPT Module widget
- [ ] x86 Emulation widget
- [ ] Theme customization widget
- [ ] Bootloader integration widget
- [ ] Advanced dashboard page (Chimæra, Quantum Decay, Self-Destruct, etc.)
- [ ] Navigation system between pages
- [ ] State management implementation
- [ ] Backend integration
- [ ] Device testing and optimization

See `IMPLEMENTATION_GUIDE.md` for detailed specifications.

---

## 📦 Dependencies

- **flutter_animate** - Smooth animations with easeInOutCubic curves
- **animated_glow** - Pulsing glow effects
- **flutter_blurhash** - Image blur hashing
- **shimmer** - Shimmer loading effects
- **google_fonts** - Inter & Roboto Mono fonts
- **provider** - State management (for future integration)

---

## 🎨 Color Palette

| Color | Hex Code | Usage |
|-------|----------|-------|
| Neon Green | `#00FFB3` | Active states, success |
| Cyber Violet | `#B368FF` | Accents, highlights |
| Aqua Blue | `#00E5FF` | Info, secondary actions |
| Amber Warning | `#FFC400` | Warnings |
| Red Critical | `#FF3B30` | Errors, destructive actions |
| Background | `#0B0E16` | Main background |
| Surface | `#151922` | Cards, panels |

---

**Built for QWAMOS • Flutter 3.0+ • GPU-Accelerated • 60% Complete**
