# Premium Design System - Complete Color Replacement Map

This document outlines all the hardcoded color values found in the codebase and their corresponding design system token replacements.

## Color Mapping

### Backgrounds
- `'#000000'` → `Colors.background`
- `'#000'` → `Colors.background`
- `'#0A0C10'` → `Colors.background`
- `'#0F1116'` → `Colors.background`
- `'#020617'` → `Colors.background`
- `'#1C1C1E'` → `Colors.surface`
- `'#151515'` → `Colors.surface`
- `'#1A1D23'` → `Colors.surface`
- `'#111419'` → `Colors.surface`
- `'#1E293B'` → `Colors.surface`
- `'#1a1a1a'` → `Colors.surface`
- `'#2C2C2E'` → `Colors.surfaceElevated`

### Brand/Accent Colors
- `'#FACC15'` → `Colors.brand.primary`
- `'#FFD700'` → `Colors.brand.primary`

### Text Colors
- `'#FFFFFF'` → `Colors.text.primary`
- `'#fff'` → `Colors.text.primary`
- `'#F5F5F7'` → `Colors.text.primary`
- `'#E2E8F0'` → `Colors.text.primary`
- `'#E5E5E5'` → `Colors.text.primary`
- `'#A1A1AA'` → `Colors.text.secondary`
- `'#94A3B8'` → `Colors.text.secondary`
- `'#A8A8AD'` → `Colors.text.secondary`
- `'#71717A'` → `Colors.text.tertiary`
- `'#8E8E93'` → `Colors.text.tertiary`
- `'#64748B'` → `Colors.text.tertiary`
- `'#52525B'` → `Colors.text.muted`
- `'#C7C7CC'` → `Colors.text.muted`

### Borders
- `'#27272A'` → `Colors.border`
- `'#2C2C2E'` → `Colors.border`
- `'#333'` → `Colors.border`
- `'rgba(255,255,255,0.05)'` → `Colors.border`
- `'#3F3F46'` → `Colors.borderLight`
- `'#3A3A3C'` → `Colors.borderLight`
- `'#334155'` → `Colors.borderLight`
- `'rgba(255,255,255,0.15)'` → `Colors.borderLight`

### Semantic Colors
- `'#FF3B30'` → `Colors.error`
- `'#3b82f6'` → `Colors.info`
- `'#007AFF'` → `Colors.info`

## Typography Replacements

### Font Families
- `Platform.OS === 'ios' ? 'PlayfairDisplay_700Bold' : 'serif'` → `Typography.fonts.primary`
- `Platform.OS === 'ios' ? 'PlayfairDisplay_400Regular' : 'serif'` → `Typography.fonts.primary`

### Preset Usage
- Large headlines (40-48px) → `...Typography.presets.display`
- Primary headlines (28-32px) → `...Typography.presets.h1`
- Secondary headlines (22-24px) → `...Typography.presets.h2`
- Tertiary headlines (18-20px) → `...Typography.presets.h3`
- Body text (15-17px) → `...Typography.presets.body` or `...Typography.presets.bodyLarge`
- Small text (13px) → `...Typography.presets.bodySmall`
- Captions (12px) → `...Typography.presets.caption`
- Labels (11px) → `...Typography.presets.label`
