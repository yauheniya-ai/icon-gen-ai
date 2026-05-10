# icon-gen-ai – Changelog

## 0.6.2 (2026-05-10)

### Fixed
- **CLI: Added missing `_dim()` helper** - `_dim()` was referenced in `providers` and `search` command output but never defined, causing `F821` (undefined name) errors at runtime
- **Generator: Bare `except` clause** - Changed bare `except:` to `except Exception:` in `parse_color()` for safer error handling
- **Animator: Removed dead code** - Removed unused `v1` variable assignments in the flip animation path (values were computed but never referenced)
- **Tests: Fixed `test_cli_group` assertion** - Updated assertion to match actual CLI output (`'icons from Iconify'` instead of `'generate icons from Iconify'`)

### Changed
- **Dev tooling: Replaced `black` with `ruff format`** - Removed `black` from dev dependencies; `ruff format` is fully Black-compatible and consolidates formatting and linting into a single tool
- **Code quality: Removed unused imports** - Cleaned up unused imports across test files (`pytest`, `re`, `Path`, `List`, `Union`, etc.) and src modules via `ruff --fix`
- **`__init__.py`: Intentional imports marked with `noqa`** - Post-`_check_deps()` import and optional AI imports annotated to silence E402/F401 for intentional patterns

## 0.6.1 (2026-05-03)

### Changed
- **CLI: Styled banner on launch** - Running `icon-gen-ai` with no arguments now displays an ASCII banner and version in mediumslateblue, followed by a fully styled help output
- **CLI: Custom colored help output** - Replaced Click's default plain-text help with a hand-crafted styled version using the package color palette: deeppink section headers, mediumslateblue option names, deepskyblue command names
- **CLI: Styled `--version` output** - `--version` now prints a colored `icon-gen-ai  vX.Y.Z` line instead of Click's default plain text
- **CLI: Color palette** - All CLI output uses three colors only: mediumslateblue `(123, 104, 238)`, deeppink `(255, 20, 147)`, and deepskyblue `(0, 191, 255)`
- **CLI: Styled generate output** - Parameter labels are deepskyblue, values are bold; success message shows a colored checkmark with the output path
- **CLI: Styled search results** - Result index is deeppink bold, icon name is bold white, reason text is deepskyblue
- **CLI: Styled providers output** - Status lines use mediumslateblue checkmarks, labels in deepskyblue, active provider name in deeppink
- **CLI: No extra dependencies** - All styling uses `click.style()` built into Click; no `rich` or other packages required

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

