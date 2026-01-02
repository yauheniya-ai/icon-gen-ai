"""Core icon generation logic using Iconify API, direct URLs, and local files."""

import requests
import re
from pathlib import Path
from typing import Optional, Literal, Union
from xml.etree import ElementTree as ET
from io import BytesIO

try:
    from PIL import Image
    import cairosvg
    RASTER_AVAILABLE = True
except ImportError:
    RASTER_AVAILABLE = False
    print("Warning: PIL/cairosvg not available. Gradient icons may not work properly.")

FormatType = Literal["svg", "png", "webp"]


class IconGenerator:
    ICONIFY_API = "https://api.iconify.design"

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def create_gradient_def(
        self,
        gradient_id: str,
        color1: str,
        color2: str,
        direction: str = "horizontal",
    ) -> str:
        """Create SVG gradient definition."""
        if direction == "vertical":
            x1, y1, x2, y2 = "0%", "0%", "0%", "100%"
        else:
            x1, y1, x2, y2 = "0%", "0%", "100%", "0%"

        return f"""<defs>
  <linearGradient id="{gradient_id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
    <stop offset="0%" stop-color="{color1}" stop-opacity="1" />
    <stop offset="100%" stop-color="{color2}" stop-opacity="1" />
  </linearGradient>
</defs>"""

    def apply_gradient_via_raster(
        self,
        svg_content: str,
        color1: str,
        color2: str,
        size: int = 256
    ) -> str:
        """Apply gradient by converting to PNG and back to SVG."""
        if not RASTER_AVAILABLE:
            print("Cannot apply gradient: PIL/cairosvg not installed")
            return svg_content
        
        try:
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=size,
                output_height=size
            )
            
            # Open as PIL Image
            img = Image.open(BytesIO(png_data)).convert("RGBA")
            width, height = img.size
            
            # Parse colors
            left_rgb = tuple(int(color1.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            right_rgb = tuple(int(color2.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            # Apply gradient
            pixels = list(img.getdata())
            new_data = []
            
            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    r, g, b, a = pixels[idx]
                    
                    # If pixel is not transparent, apply gradient
                    if a > 0:
                        ratio = x / (width - 1) if width > 1 else 0
                        new_r = int(left_rgb[0] * (1 - ratio) + right_rgb[0] * ratio)
                        new_g = int(left_rgb[1] * (1 - ratio) + right_rgb[1] * ratio)
                        new_b = int(left_rgb[2] * (1 - ratio) + right_rgb[2] * ratio)
                        new_data.append((new_r, new_g, new_b, a))
                    else:
                        new_data.append((r, g, b, a))
            
            img.putdata(new_data)
            
            # Convert back to SVG
            svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" shape-rendering="crispEdges">\n'
            svg_content = []
            
            for y in range(height):
                for x in range(width):
                    r, g, b, a = new_data[y * width + x]
                    if a > 0:
                        hex_color = f'#{r:02x}{g:02x}{b:02x}'
                        opacity = a / 255
                        svg_content.append(
                            f'<rect x="{x}" y="{y}" width="1" height="1" '
                            f'fill="{hex_color}" fill-opacity="{opacity:.3f}" />'
                        )
            
            svg_footer = '</svg>'
            return svg_header + '\n'.join(svg_content) + svg_footer
            
        except Exception as e:
            print(f"Error applying gradient via raster: {e}")
            import traceback
            traceback.print_exc()
            return svg_content

    def wrap_with_background(
        self,
        svg_content: str,
        size: int,
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_radius: int = 0,
    ) -> str:
        """Wrap SVG icon with a background."""
        # Parse original SVG
        try:
            root = ET.fromstring(svg_content)
            vb = root.get("viewBox", "0 0 24 24").split()
            vb_x, vb_y, vb_w, vb_h = map(float, vb)
            icon_elements = ''.join(
                ET.tostring(child, encoding="unicode") for child in root
            )
        except:
            vb_w = vb_h = 24
            icon_elements = svg_content

        # Background
        gradient_def = ""
        if bg_color is None:
            bg_fill = "none"
        elif isinstance(bg_color, tuple):
            gradient_def = self.create_gradient_def("bgGradient", bg_color[0], bg_color[1])
            bg_fill = "url(#bgGradient)"
        else:
            bg_fill = bg_color

        # Compute scaling & translation to center
        scale = size / max(vb_w, vb_h) * 0.7
        tx = size / 2
        ty = size / 2

        return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
{gradient_def}
  <rect width="{size}" height="{size}" rx="{border_radius}" ry="{border_radius}" fill="{bg_fill}" />
  <g transform="translate({tx},{ty}) scale({scale}) translate({-vb_w/2},{-vb_h/2})">
{icon_elements}
  </g>
</svg>"""

    def modify_svg(
        self,
        svg_content: str,
        color: Optional[Union[str, tuple[str, str]]] = None,
        size: Optional[int] = None,
    ) -> str:
        """Modify SVG content to apply color and size."""
        try:
            # For gradient colors, use raster method
            if isinstance(color, tuple):
                return self.apply_gradient_via_raster(svg_content, color[0], color[1], size or 256)
            
            # For solid colors, use XML manipulation
            root = ET.fromstring(svg_content)
            
            # Ensure viewBox exists
            if not root.get("viewBox"):
                w = re.sub(r"[^\d.]", "", root.get("width", "24"))
                h = re.sub(r"[^\d.]", "", root.get("height", "24"))
                root.set("viewBox", f"0 0 {w} {h}")

            # Apply size
            if size:
                root.set("width", str(size))
                root.set("height", str(size))

            # Apply solid color
            if color:
                def apply_solid_color(el):
                    tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
                    visual_tags = {
                        'path', 'circle', 'rect', 'polygon', 'ellipse',
                        'polyline', 'line', 'text'
                    }
                    
                    if tag in visual_tags:
                        current_fill = el.get('fill', '')
                        if current_fill and current_fill.lower() != 'none':
                            el.set('fill', color)
                        elif not current_fill:
                            el.set('fill', color)
                        
                        if el.get('stroke'):
                            el.set('stroke', color)
                    
                    for child in el:
                        apply_solid_color(child)
                
                apply_solid_color(root)

            return ET.tostring(root, encoding="unicode")
        except Exception as e:
            print(f"Warning: Could not modify SVG: {e}")
            import traceback
            traceback.print_exc()
            return svg_content

    def load_local_file(self, file_path: str, target_color: Optional[str] = None) -> Optional[str]:
        """Load and convert local image file to SVG.
        
        For raster images, if target_color is provided, non-transparent pixels
        will be recolored to that color while preserving transparency.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return None
        
        # If already SVG, just read it
        if file_path.suffix.lower() == '.svg':
            try:
                return file_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"Error reading SVG file {file_path}: {e}")
                return None
        
        # For raster images (PNG, JPG, etc.), convert to SVG
        if not RASTER_AVAILABLE:
            print("Error: PIL not available. Cannot process raster images.")
            print("Install with: pip install Pillow")
            return None
        
        try:
            # Load image
            img = Image.open(file_path).convert("RGBA")
            width, height = img.size
            
            # Apply color transformation if requested
            if target_color and target_color.lower() != 'currentcolor':
                # Parse target color
                if target_color.startswith('#'):
                    target_rgb = tuple(int(target_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                elif target_color.lower() == 'white':
                    target_rgb = (255, 255, 255)
                elif target_color.lower() == 'black':
                    target_rgb = (0, 0, 0)
                else:
                    # Try to parse named colors
                    color_map = {
                        'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
                        'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255),
                        'gray': (128, 128, 128), 'grey': (128, 128, 128),
                    }
                    target_rgb = color_map.get(target_color.lower(), (255, 255, 255))
                
                # Recolor non-transparent pixels
                pixels = list(img.getdata())
                new_pixels = []
                
                for r, g, b, a in pixels:
                    if a > 0:  # Non-transparent pixel
                        # Replace with target color, keeping alpha
                        new_pixels.append((*target_rgb, a))
                    else:
                        # Keep transparent pixels
                        new_pixels.append((r, g, b, a))
                
                img.putdata(new_pixels)
            
            # Create SVG representation
            svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
            svg_content = []
            
            # Convert to base64 embedded image
            from base64 import b64encode
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = b64encode(buffer.getvalue()).decode('utf-8')
            
            svg_content.append(
                f'<image width="{width}" height="{height}" '
                f'href="data:image/png;base64,{img_data}" />'
            )
            
            svg_footer = '</svg>'
            return svg_header + '\n'.join(svg_content) + svg_footer
            
        except Exception as e:
            print(f"Error converting {file_path} to SVG: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_icon_from_url(self, url: str) -> Optional[str]:
        """Fetch icon from URL."""
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"Error fetching from URL {url}: {e}")
            return None

    def get_icon_svg(self, icon_name: str, color: str = "currentColor") -> Optional[str]:
        """Fetch SVG icon from Iconify API."""
        try:
            r = requests.get(
                f"{self.ICONIFY_API}/{icon_name}.svg",
                params={"color": color},
                timeout=10,
            )
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"Error fetching icon {icon_name}: {e}")
            return None

    def save_svg(self, svg_content: str, output_path: Path) -> bool:
        """Save SVG content to file."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(svg_content, encoding="utf-8")
            return output_path
        except Exception as e:
            print(f"Error saving {output_path}: {e}")
            return False

    def generate_icon(
        self,
        icon_name: Optional[str] = None,
        output_name: Optional[str] = None,
        color: Optional[Union[str, tuple[str, str]]] = None,
        size: Optional[int] = None,
        format: FormatType = "svg",
        direct_url: Optional[str] = None,
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_radius: int = 0,
        local_file: Optional[str] = None,
    ) -> Optional[Path]:
        """Generate and save an icon with custom styling.
        
        Args:
            icon_name: Iconify icon name (e.g., 'mdi:home')
            output_name: Output filename (without extension)
            color: Icon color (solid or tuple for gradient)
            size: Icon size in pixels
            format: Output format (svg, png, webp)
            direct_url: Direct URL to fetch icon from
            bg_color: Background color (solid or tuple for gradient)
            border_radius: Border radius for background
            local_file: Path to local image file to convert
        """
        size = size or 256

        # Fetch the icon from appropriate source
        if local_file:
            # For local files, pass the color for immediate processing
            svg_content = self.load_local_file(local_file, color if not isinstance(color, tuple) else None)
        elif direct_url:
            svg_content = self.get_icon_from_url(direct_url)
        elif icon_name:
            # Fetch as black (or any solid color) for gradient conversion
            fetch_color = "black" if isinstance(color, tuple) else (color or "currentColor")
            svg_content = self.get_icon_svg(icon_name, fetch_color)
        else:
            print("Error: Must provide icon_name, direct_url, or local_file")
            return None

        if not svg_content:
            return None

        # Apply color and size modifications (skip color if already applied for local files)
        if local_file and color and not isinstance(color, tuple):
            # Color already applied during load, just apply size
            svg_content = self.modify_svg(svg_content, None, size)
        else:
            # Apply color and size modifications
            svg_content = self.modify_svg(svg_content, color, size)

        # Apply background if specified
        if bg_color is not None or border_radius > 0:
            svg_content = self.wrap_with_background(svg_content, size, bg_color, border_radius)

        # Determine output filename
        if output_name is None:
            if local_file:
                output_name = Path(local_file).stem
            elif icon_name:
                output_name = icon_name.replace(":", "_").replace("/", "_")
            else:
                output_name = "icon"

        output_path = self.output_dir / f"{output_name}.svg"
        return output_path if self.save_svg(svg_content, output_path) else None

    def generate_batch(
        self,
        icons: dict[str, str | dict],
        color: Optional[Union[str, tuple[str, str]]] = None,
        size: Optional[int] = None,
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_radius: int = 0,
    ) -> list[Path]:
        """Generate multiple icons at once."""
        results = []

        for output_name, icon_config in icons.items():
            print(f"\nGenerating {output_name}...")

            if isinstance(icon_config, str):
                path = self.generate_icon(
                    icon_config,
                    output_name,
                    color,
                    size,
                    bg_color=bg_color,
                    border_radius=border_radius,
                )
            elif isinstance(icon_config, dict):
                path = self.generate_icon(
                    icon_config.get("icon"),
                    output_name,
                    icon_config.get("color", color),
                    icon_config.get("size", size),
                    direct_url=icon_config.get("url"),
                    bg_color=icon_config.get("bg_color", bg_color),
                    border_radius=icon_config.get("border_radius", border_radius),
                    local_file=icon_config.get("local_file"),
                )
            else:
                print(f"Invalid config for {output_name}")
                continue

            if path:
                results.append(path)

        return results