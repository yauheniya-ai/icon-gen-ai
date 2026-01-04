# icon-gen-ai

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/icon-gen-ai?color=blue&label=PyPI)](https://pypi.org/project/icon-gen-ai/)
[![Tests](https://github.com/yauheniya-ai/icon-gen-ai/actions/workflows/tests.yml/badge.svg)](https://github.com/yauheniya-ai/icon-gen-ai/actions/workflows/tests.yml)
[![Coverage](https://img.shields.io/badge/coverage-60%25-yellow.svg)](https://github.com/yauheniya-ai/icon-gen-ai)
[![GitHub last commit](https://img.shields.io/github/last-commit/yauheniya-ai/icon-gen)](https://github.com/yauheniya-ai/icon-gen/commits/main)
[![Downloads](https://pepy.tech/badge/icon-gen-ai)](https://pepy.tech/project/icon-gen-ai)

Generate customizable icons from Iconify, direct URLs, or local files with easy export to PNG, SVG, WebP formats.

<div align="center">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/docs/demo.svg" width="100%" alt="CLI Demo">
  <br><sub>
    <a href="https://yauheniya-ai.github.io/icon-gen-ai/">View CLI Usage Examples</a>
  </sub>
</div>

## Features

- AI-assisted icon search and generation
- Simple and intuitive CLI and Python API
- Access 200,000+ icons from Iconify
- Unlimited icons from direct URLs or local files
- Customize colors, sizes, and backgrounds and adjust border radius
- Gradient color option for icons and backgrounds
- Export to SVG, PNG, or WEBP format

## Installation

```bash
pip install icon-gen-ai
```

**(Optional) AI features**: 
```bash
pip install icon-gen-ai[ai]
```

## Quick Start

### Generate Single Icons

<div align="center" style="padding: 40px; ">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/claude_white_mediumslateblue_bg.svg" width="70" alt="Claude">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/gemini_white_deeppink_bg.svg" width="70" alt="Gemini">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/mistral_white_gradient_bg.svg" width="70" alt="Mistral">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/openai_gradient_transparent_bg.svg" width="70" alt="OpenAI">
</div>

```python
from icon_gen import IconGenerator

generator = IconGenerator(output_dir="output")

# From URL
generator.generate_icon(
    direct_url='https://upload.wikimedia.org/wikipedia/commons/b/b0/Claude_AI_symbol.svg',
    output_name='claude_white_mediumslateblue_bg',
    color='white',
    bg_color='mediumslateblue',
    border_radius=0,
    size=256
)

# From Iconify
generator.generate_icon(
    icon_name='simple-icons:googlegemini',
    output_name='gemini_white_deeppink_bg',
    color='white',
    bg_color='deeppink',
    border_radius=128,  # Circle (half of size)
    size=256
)

# From Iconify 
generator.generate_icon(
    icon_name='simple-icons:mistralai',
    output_name='mistral_white_gradient_bg',
    color='white',
    bg_color=('mediumslateblue', 'deeppink'),  # Gradient
    border_radius=48,
    size=256
)

# From Iconify 
generator.generate_icon(
    icon_name='simple-icons:openai',
    output_name='openai_gradient_transparent_bg',
    color=('mediumslateblue', 'deeppink'),  # Gradient icon
    bg_color=None,
    size=256
)
```

### Generate Multiple Icons (Batch)

<div align="center" style="padding: 40px; ">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/llama_deepskyblue.svg" width="70" alt="Llama">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/deepseek_deepskyblue.svg" width="70" alt="DeepSeek">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/nemotron_deepskyblue.svg" width="70" alt="Nemotron">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/grok_deepskyblue.svg" width="70" alt="Grok">
</div>

```python
from icon_gen import IconGenerator

generator = IconGenerator(output_dir="output")

# Generate multiple icons at once
ai_icons = {
    'llama_deepskyblue': 'simple-icons:meta',
    'deepseek_deepskyblue': {
        'local_file': 'input/deepseek-icon.png'
    },
    'nemotron_deepskyblue': {
        'url': 'https://companieslogo.com/img/orig/NVDA-df4c2377.svg'
    },
    'grok_deepskyblue': {
        'url': 'https://unpkg.com/@lobehub/icons-static-svg@latest/icons/grok.svg'
    }
}

generator.generate_batch(ai_icons, color='deepskyblue', size=256, outline_color='deepskyblue', outline_width=8, border_radius=48)
```

### Animation Support

When you apply a solid color to an animated SVG icon, the animations are automatically preserved:

<div align="center" style="padding: 40px; ">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/bars_scale_mediumslateblue.svg" width="70" alt="bars scale">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/my_location_loop_mediumslateblue.svg" width="70" alt="my location loop">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/speedometer_loop_mediumslateblue.svg" width="70" alt="speedometer loop">
  <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" width="40" height="1" alt="">
  <img src="https://raw.githubusercontent.com/yauheniya-ai/icon-gen-ai/main/output/upload_outline_loop_mediumslateblue.svg" width="70" alt="upload outline loop">
</div>


```python
from icon_gen import IconGenerator

generator = IconGenerator(output_dir="output")

color = 'mediumslateblue' 

animated_icons = {
    f'speedometer_loop_{color}': 'line-md:speedometer-loop',
    f'upload_outline_loop_{color}': 'line-md:upload-outline-loop',
    f'my_location_loop_{color}': 'line-md:my-location-loop',
    f'bars_scale_middle_{color}': 'svg-spinners:bars-scale-middle'
}

generator.generate_batch(ai_icons, color=color, size=256, outline_color='deeppink', bg_color='snow', outline_width=8, border_radius=48)
```

**What preserves animations:**
- Solid colors
- No color specified (original colors)
- Backgrounds and outlines

**What removes animations:**
- Gradient colors on the icon itself: `color=('deeppink', 'mediumslateblue')`

**Note:** Background gradients don't affect icon animations - only icon color gradients do.

## Icon Sources

**Three ways to get icons:**

### 1. Iconify (200,000+ icons)
Browse at [Iconify](https://icon-sets.iconify.design/)

**Format:** `collection:icon-name`
```python
# Popular collections:
'simple-icons:openai'           # Company logos
'mdi:github'                    # Material Design Icons  
'fa6-solid:scale-balanced'      # Font Awesome
'heroicons:scale'               # HeroIcons
```

**AI-powered search** (requires `pip install icon-gen-ai[ai]`):
```bash
icon-gen-ai search "payment icons for checkout" --generate
```

### 2. Direct URL
Any public image URL (SVG, PNG with transparent background):
```python
direct_url='https://upload.wikimedia.org/wikipedia/commons/b/b0/Claude_AI_symbol.svg'
direct_url='https://companieslogo.com/img/orig/NVDA-df4c2377.svg'
```

### 3. Local File
SVG or PNG (with transparent background):
```python
local_file='input/my-icon.svg'
local_file='input/my-icon.png'
```

## Examples

Check out the `examples/` directory for more use cases:

**Basic Generation:**
- `generate_ai_icons_singular.py` - Generate icons one-by-one with custom backgrounds & gradients
- `generate_ai_icons_batch.py` - Generate multiple AI model icons at once (batch mode)

**AI-Powered Search** (requires `pip install icon-gen-ai[ai]`):
- `ai_simple_usage.py` - Search and generate icons using natural language
- `ai_icon_search.py` - Advanced search with custom styles and project context

## Development

```bash
# Clone the repository
git clone https://github.com/yauheniya-ai/icon-gen-ai.git
cd icon-gen-ai

# Install all dependencies (including dev tools)
uv sync
uv sync --extra ai --dev

# Run tests
uv run pytest --cov=src --cov-report=term-missing
```

## License

MIT License - see LICENSE file for details

## Author

Yauheniya Varabyova (yauheniya.ai@gmail.com)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
