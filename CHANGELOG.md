# icon-gen-ai – Changelog

## 0.6.0 (2026-04-11)

### Feature
- **Generator: Radial gradient direction** - Passing `direction="radial"` or `bg_direction="radial"` renders a center-out radial gradient instead of a linear one. Color 1 appears at the center and color 2 at the edges
  - For SVG output, uses a native `<radialGradient>` element (`cx="50%" cy="50%" r="50%"`) — zero rasterisation, fully scalable
  - For PNG/WebP icon-colour gradients, uses a per-pixel distance computation: `ratio = distance(pixel, center) / distance(corner, center)`, giving a smooth center-to-edge blend that matches the SVG rendering exactly
  - Works for both icon colour (`color=(c1, c2)` + `direction="radial"`) and background colour (`bg_color=(c1, c2)` + `bg_direction="radial"`)
  - Compatible with all existing features: solid/gradient backgrounds, transparent cutout, outline, border radius, animation, and batch generation
- **Example: `examples/generate_gradient_icons.py`** - Updated to showcase all four gradient directions (horizontal, vertical, diagonal, radial) for both icon colour and background colour

## 0.5.0 (2026-04-11)

### Feature
- **Generator: Transparent cutout icon color** - Passing `color="transparent"` together with a background now punches the icon silhouette as a transparent hole through the background. The area covered by the icon becomes see-through while the rest of the background is preserved, enabling negative-space / sticker-style badge designs
  - Works for SVG output via an SVG `<mask>` with icon fills forced to black (compatible with all SVG renderers)
  - Works for PNG/WebP output via PIL compositing: background and icon are rasterized separately, then `new_alpha = bg_alpha × (1 − icon_alpha)` is applied — bypasses `cairosvg`'s lack of `<mask>` support entirely
  - Gradient, solid, and rounded/circle backgrounds all supported
  - Outline (`outline_width` / `outline_color`) works alongside cutout
  - `parse_color` no longer raises for `"transparent"` / `"none"` inputs
- **Example: `examples/generate_transparent_icon.py`** - Demonstrates all cutout variants: solid background, gradient background, circular badge with outline, and single-icon PNG export

## 0.4.11 (2026-04-11)

### Frontend

### Fixed
- **Output panel: Color fields no longer jump to `#ffffff` while typing** - Text inputs now pass values through directly on each keystroke; CSS color name normalisation (e.g. `red` → `#ff0000`) is deferred to `onBlur` so partial or deleted input is never overwritten mid-edit
- **Output panel: `transparent` is now a valid color value** - Typing `transparent` in any color field (icon or background) is preserved as-is and passed correctly to the backend; the color picker falls back to white for display only

### Backend / Generator

### Fixed
- **Generator: `transparent` icon color = background cutout** - When `color="transparent"` is used together with a background, the icon shape now punches a transparent hole through the background (the background is visible everywhere *except* in the icon shape, where the canvas behind shows through). Implemented via an SVG `<mask>` + `feColorMatrix` filter that maps all icon pixel colours to black so the mask works regardless of the icon's original fills. The icon is fetched with its original colours preserved; the cutout is applied at the compositing stage only. `parse_color` no longer raises on `"transparent"`/`"none"` inputs; the raster recolor path also handles transparent correctly (erases all visible pixels)

## 0.4.10

### Fixed
- **CLI: Consistent error messaging** - `search` command now shows the same installation instructions as `providers` command when AI extras are not installed

### Changed
- **CLI: Removed emoji from error messages** - Removed red cross emoji (❌) for better terminal compatibility

## 0.4.9

### Fixed
- **AI: Fixed provider detection** - Now correctly checks if third-party packages (`anthropic`, `openai`, `huggingface-hub`) are actually installed, not just if provider modules exist. This fixes the issue where `icon-gen-ai providers` incorrectly showed providers as available when AI extras weren't installed

## 0.4.8

### Fixed
- **CLI: Clarified installation steps in messages** - Commands now clearly separate "install extras" from "configure API keys" steps. Messages emphasize installing `pip install "icon-gen-ai[ai]"` first, then configuring API keys
- **CLI: Improved `providers` command output** - Now shows "✓ AI extras installed" status line before listing available providers

### Changed
- **CLI: Updated error message formatting** - `search` command error now explicitly states "AI extras installed but no API key configured" when extras are present but unconfigured

## 0.4.7

### Added
- **Tests: Comprehensive mocked unit tests for AI providers** - Added 29 new tests covering OpenAI (8), Anthropic (12), and HuggingFace (9) providers with mocked API calls. No real API keys required for testing
- **Tests: Improved coverage for AI modules** - Provider coverage: Anthropic 21%→87% (+66%), OpenAI 24%→72% (+48%), HuggingFace 18%→42% (+24%)

### Fixed
- **CLI: Improved `providers` command messaging** - Now provides clear, actionable guidance when AI features are not installed or configured:
  - When AI extras are not installed: Shows explicit instructions to run `pip install icon-gen-ai[ai]`
  - When no API key is configured: Lists all supported API keys (ANTHROPIC_API_KEY, HF_TOKEN, OPENAI_API_KEY) with instructions on how to set them
  - When provider is active: Shows the active provider name and model
- **CLI: Updated `search` command error messages** - More descriptive errors that mention all three supported providers
- **Documentation: Added API key configuration guide** - README now includes instructions on how to configure API keys after installing AI extras

### Changed
- API keys are now listed alphabetically in all CLI messages (ANTHROPIC_API_KEY, HF_TOKEN, OPENAI_API_KEY)

