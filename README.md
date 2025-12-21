# icon-gen

Generate customizable icons from Iconify with easy export to PNG, SVG, WebP.

## Installation
```bash
pip install icon-gen
```

## Usage
```python
from icon_gen import IconGenerator

generator = IconGenerator()
generator.create_icon('mdi:github', color='white', size=256, format='png')
```

## CLI
```bash
icon-gen mdi:github --color white --size 256 --format png -o github.png
```

## Features

- Access thousands of icons from Iconify
- Customize colors and sizes
- Export to PNG, SVG, WebP
- Simple CLI interface