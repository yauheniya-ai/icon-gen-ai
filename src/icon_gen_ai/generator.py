"""Core icon generation logic using Iconify API, direct URLs, and local files."""

import requests
import re
from pathlib import Path
from typing import Optional, Literal, Union, Tuple
from xml.etree import ElementTree as ET
from io import BytesIO
from .animation import Animator
from .animation.webp_exporter import svg_animation_to_webp

try:
    from PIL import Image, ImageColor
    import cairosvg
    RASTER_AVAILABLE = True
except ImportError:
    RASTER_AVAILABLE = False
    print("Warning: PIL/cairosvg not available. Gradient icons may not work properly.")

FormatType = Literal["svg", "png", "webp", "ico"]


def parse_color(color: str) -> Tuple[int, int, int]:
    """Parse color string to RGB tuple (supports hex and CSS3 named colors)."""
    if color.lower() in ('transparent', 'none'):
        return (0, 0, 0)
    try:
        rgb = ImageColor.getrgb(color)
        return rgb[:3] if len(rgb) >= 3 else rgb
    except:
        return (255, 255, 255)  # Default to white


class IconGenerator:
    ICONIFY_API = "https://api.iconify.design"

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    # -------------------- GRADIENT --------------------
    def create_gradient_def(
        self,
        gradient_id: str,
        color1: str,
        color2: str,
        direction: str = "horizontal",
    ) -> str:
        if direction == "radial":
            return f"""<defs>
  <radialGradient id="{gradient_id}" cx="50%" cy="50%" r="50%" fx="50%" fy="50%">
    <stop offset="0%" stop-color="{color1}" stop-opacity="1" />
    <stop offset="100%" stop-color="{color2}" stop-opacity="1" />
  </radialGradient>
</defs>"""
        if direction == "vertical":
            x1, y1, x2, y2 = "0%", "0%", "0%", "100%"
        elif direction == "diagonal":
            x1, y1, x2, y2 = "0%", "0%", "100%", "100%"
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
        size: int = 256,
        direction: str = "horizontal",
    ) -> str:
        if not RASTER_AVAILABLE:
            print("Cannot apply gradient: PIL/cairosvg not installed")
            return svg_content
        try:
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=size,
                output_height=size
            )
            img = Image.open(BytesIO(png_data)).convert("RGBA")
            width, height = img.size
            
            left_rgb = parse_color(color1)
            right_rgb = parse_color(color2)
            
            pixels = list(img.getdata())
            new_data = []
            for y in range(height):
                for x in range(width):
                    idx = y * width + x
                    r, g, b, a = pixels[idx]
                    if a > 0:
                        if direction == "vertical":
                            ratio = y / (height - 1) if height > 1 else 0
                        elif direction == "diagonal":
                            ratio = (x + y) / (width + height - 2) if (width + height) > 2 else 0
                        elif direction == "radial":
                            cx, cy = (width - 1) / 2, (height - 1) / 2
                            max_r = ((cx ** 2 + cy ** 2) ** 0.5) or 1
                            ratio = min(((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / max_r, 1.0)
                        else:  # horizontal
                            ratio = x / (width - 1) if width > 1 else 0
                        new_r = int(left_rgb[0] * (1 - ratio) + right_rgb[0] * ratio)
                        new_g = int(left_rgb[1] * (1 - ratio) + right_rgb[1] * ratio)
                        new_b = int(left_rgb[2] * (1 - ratio) + right_rgb[2] * ratio)
                        new_data.append((new_r, new_g, new_b, a))
                    else:
                        new_data.append((r, g, b, a))
            img.putdata(new_data)

            # Convert to SVG rectangles
            svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" shape-rendering="crispEdges">\n'
            svg_content_list = []
            for y in range(height):
                for x in range(width):
                    r, g, b, a = new_data[y * width + x]
                    if a > 0:
                        hex_color = f'#{r:02x}{g:02x}{b:02x}'
                        opacity = a / 255
                        svg_content_list.append(
                            f'<rect x="{x}" y="{y}" width="1" height="1" '
                            f'fill="{hex_color}" fill-opacity="{opacity:.3f}" />'
                        )
            svg_footer = '</svg>'
            return svg_header + '\n'.join(svg_content_list) + svg_footer

        except Exception as e:
            print(f"Error applying gradient via raster: {e}")
            import traceback
            traceback.print_exc()
            return svg_content

    def recolor_svg_to_single_color(
        self,
        svg_content: str,
        target_color: str,
        size: int = 256
    ) -> str:
        """Recolor multi-color SVG to single color using raster method."""
        if not RASTER_AVAILABLE:
            print("Cannot recolor SVG: PIL/cairosvg not installed")
            print("Install with: pip install Pillow cairosvg")
            return svg_content
        
        try:
            target_rgb = parse_color(target_color)
            
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=size,
                output_height=size
            )
            
            # Open as PIL Image
            img = Image.open(BytesIO(png_data)).convert("RGBA")
            width, height = img.size
            
            # Recolor all non-transparent pixels
            pixels = list(img.getdata())
            new_pixels = []
            is_transparent_color = target_color.lower() in ('transparent', 'none')
            for r, g, b, a in pixels:
                if a > 0:  # Non-transparent pixel
                    if is_transparent_color:
                        new_pixels.append((r, g, b, 0))  # Erase: fully transparent
                    else:
                        new_pixels.append((*target_rgb, a))
                else:
                    new_pixels.append((r, g, b, a))
            
            img.putdata(new_pixels)
            
            # Convert back to SVG with embedded image
            from base64 import b64encode
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = b64encode(buffer.getvalue()).decode('utf-8')
            
            return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n<image width="{width}" height="{height}" href="data:image/png;base64,{img_data}" />\n</svg>'
            
        except Exception as e:
            print(f"Error recoloring SVG: {e}")
            import traceback
            traceback.print_exc()
            return svg_content

    # -------------------- BACKGROUND --------------------
    def _elements_forced_black(self, icon_elements_str: str) -> str:
        """Return icon elements with every fill/stroke forced to black.

        Used to build the cutout mask without depending on SVG filter support
        (cairosvg does not implement feColorMatrix).
        """
        try:
            # Parse as a fragment by wrapping in a temporary root
            wrapped = f"<_root>{icon_elements_str}</_root>"
            root = ET.fromstring(wrapped)

            def force_black(el):
                tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
                # Skip animation / meta elements
                if tag in ('animate', 'animateTransform', 'animateMotion', 'set', 'style', 'defs'):
                    return
                # Strip colour-related inline styles so they don't override fill attr
                if el.get('style'):
                    style = re.sub(r'fill\s*:[^;]+;?', 'fill:black;', el.get('style'))
                    style = re.sub(r'stroke\s*:[^;]+;?', 'stroke:black;', style)
                    el.set('style', style.strip())
                # Force fill to black unless explicitly none
                fill = el.get('fill', '')
                if fill.lower() not in ('none', ''):
                    el.set('fill', 'black')
                elif not fill:  # no fill attr at all — set explicitly for non-group elements
                    if tag not in ('g', 'svg'):
                        el.set('fill', 'black')
                # Force stroke to black unless explicitly none
                stroke = el.get('stroke', '')
                if stroke and stroke.lower() != 'none':
                    el.set('stroke', 'black')
                for child in el:
                    force_black(child)

            force_black(root)
            return ''.join(ET.tostring(child, encoding='unicode') for child in root)
        except Exception:
            # Fallback: just return the original (mask will still punch using alpha)
            return icon_elements_str

    def wrap_with_background(
        self,
        svg_content: str,
        size: int,
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_radius: int = 0,
        outline_width: int = 0,
        outline_color: Optional[str] = None,
        bg_direction: str = "horizontal",
        scale: float = 0.7,
        cutout: bool = False,
    ) -> str:
        """Wrap SVG icon with a background and optional outline.

        When *cutout* is True the icon shape punches a transparent hole through
        the background so that whatever is behind the final image shows through
        in the shape of the icon.
        """
        try:
            root = ET.fromstring(svg_content)
            vb = root.get("viewBox", "0 0 24 24").split()
            vb_x, vb_y, vb_w, vb_h = map(float, vb)
            icon_elements = "".join(
                ET.tostring(child, encoding="unicode") for child in root
            )
        except Exception:
            # Fallback when parsing fails: assume 24x24 viewBox at origin
            vb_x = 0.0
            vb_y = 0.0
            vb_w = vb_h = 24.0
            icon_elements = svg_content

        gradient_def = ""
        if bg_color is None:
            bg_fill = "none"
        elif isinstance(bg_color, tuple):
            gradient_def = self.create_gradient_def(
                "bgGradient", bg_color[0], bg_color[1], direction=bg_direction
            )
            bg_fill = "url(#bgGradient)"
        else:
            bg_fill = bg_color

        # Stroke-safe geometry
        half_stroke = outline_width / 2 if outline_width > 0 else 0
        rect_size = size - outline_width
        rect_radius = max(0, border_radius - half_stroke)

        outline_attrs = ""
        if outline_width > 0 and outline_color:
            outline_attrs = (
                f' stroke="{outline_color}" '
                f'stroke-width="{outline_width}"'
            )

        # Icon transform
        icon_scale = size / max(vb_w, vb_h) * scale
        tx = size / 2
        ty = size / 2

        if cutout:
            # Build a unified <defs> block with gradient (if any) + cutout mask.
            # We force all icon fills to black directly in the mask elements so that
            # the mask works in every renderer including cairosvg, which does NOT
            # support SVG <filter>/feColorMatrix inside masks.
            gradient_inner = (
                gradient_def
                .replace("<defs>", "")
                .replace("</defs>", "")
                .strip()
            )
            icon_transform = (
                f"translate({tx},{ty}) "
                f"scale({icon_scale}) "
                f"translate({-(vb_x + vb_w / 2)},{-(vb_y + vb_h / 2)})"
            )
            black_elements = self._elements_forced_black(icon_elements)
            return f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{size}" height="{size}"
     viewBox="0 0 {size} {size}">
  <defs>
    {gradient_inner}
    <mask id="cutoutMask">
      <!-- White = keep background visible -->
      <rect width="{size}" height="{size}" fill="white"/>
      <!-- Icon fills forced to black = cut out (make transparent) -->
      <g transform="{icon_transform}">
{black_elements}
      </g>
    </mask>
  </defs>
  <rect x="{half_stroke}" y="{half_stroke}"
        width="{rect_size}" height="{rect_size}"
        rx="{rect_radius}" ry="{rect_radius}"
        fill="{bg_fill}"{outline_attrs}
        mask="url(#cutoutMask)" />
</svg>"""

        return f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="{size}" height="{size}"
     viewBox="0 0 {size} {size}">
{gradient_def}
  <rect x="{half_stroke}" y="{half_stroke}"
        width="{rect_size}" height="{rect_size}"
        rx="{rect_radius}" ry="{rect_radius}"
        fill="{bg_fill}"{outline_attrs} />
  <g transform="
      translate({tx},{ty})
      scale({icon_scale})
      translate({-(vb_x + vb_w/2)},{-(vb_y + vb_h/2)})
  ">
{icon_elements}
  </g>
</svg>"""

    # -------------------- MODIFY SVG --------------------
    def modify_svg(
        self,
        svg_content: str,
        color: Optional[Union[str, tuple[str, str]]] = None,
        size: Optional[int] = None,
        preserve_animations: bool = True,
        direction: str = "horizontal",
        scale: Optional[float] = None,
    ) -> str:
        """Modify SVG content to apply color, size, and scale.
        
        If color is None, preserves original colors.
        If color is a tuple, applies gradient (loses embedded animations).
        If color is a string, attempts to recolor while preserving animations.
        
        Args:
            preserve_animations: If True, tries to preserve <style>, <animate>, etc.
            scale: Optional scale factor to apply to the icon (e.g., 0.7 for 70%)
        """
        try:
            # If no color specified, just apply size
            if color is None:
                try:
                    root = ET.fromstring(svg_content)
                    
                    # Ensure viewBox exists
                    if not root.get("viewBox"):
                        w = re.sub(r"[^\d.]", "", root.get("width", "24"))
                        h = re.sub(r"[^\d.]", "", root.get("height", "24"))
                        root.set("viewBox", f"0 0 {w} {h}")

                    # Apply size only
                    if size:
                        root.set("width", str(size))
                        root.set("height", str(size))

                    # Apply scale if provided
                    if scale is not None and scale != 1.0:
                        # Wrap content in a scaled group
                        vb = root.get("viewBox", "0 0 24 24").split()
                        vb_x, vb_y, vb_w, vb_h = map(float, vb)
                        
                        # Create wrapper group with transform
                        g = ET.Element("g")
                        cx, cy = vb_w / 2, vb_h / 2
                        g.set("transform", f"translate({cx},{cy}) scale({scale}) translate({-cx},{-cy})")
                        
                        # Move all children to the group
                        for child in list(root):
                            root.remove(child)
                            g.append(child)
                        root.append(g)

                    return ET.tostring(root, encoding="unicode")
                except Exception as e:
                    print(f"Warning: Could not modify SVG: {e}")
                    return svg_content
            
            # Handle gradient colors - must use raster method (loses animations)
            if isinstance(color, tuple):
                svg_content = self.apply_gradient_via_raster(
                    svg_content, 
                    color[0], 
                    color[1], 
                    size or 256,
                    direction=direction
                )
                
                # Apply scale if provided
                if scale is not None and scale != 1.0:
                    try:
                        root = ET.fromstring(svg_content)
                        vb = root.get("viewBox", "0 0 256 256").split()
                        vb_x, vb_y, vb_w, vb_h = map(float, vb)
                        
                        # Create wrapper group with transform
                        g = ET.Element("g")
                        cx, cy = vb_w / 2, vb_h / 2
                        g.set("transform", f"translate({cx},{cy}) scale({scale}) translate({-cx},{-cy})")
                        
                        # Move all children to the group
                        for child in list(root):
                            root.remove(child)
                            g.append(child)
                        root.append(g)
                        
                        return ET.tostring(root, encoding="unicode")
                    except Exception as e:
                        print(f"Warning: Could not apply scale to gradient: {e}")
                
                return svg_content
            
            # For solid colors with animation preservation
            if color and preserve_animations:
                try:
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

                    # ----- REMOVE STYLE FILLS HERE -----
                    for style in root.findall(".//{http://www.w3.org/2000/svg}style"):
                        if 'fill' in (style.text or ''):
                            root.remove(style)

                    # Apply color to fill/stroke attributes (preserves animations)
                    _is_transparent = color.lower() in ('transparent', 'none')
                    def apply_color_preserve_animation(el):
                        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
                        
                        # Skip animation elements
                        if tag in ('animate', 'animateTransform', 'animateMotion', 'set', 'style'):
                            return
                        
                        visual_tags = {
                            'path', 'circle', 'rect', 'polygon', 'ellipse',
                            'polyline', 'line', 'text', 'g'
                        }
                        
                        if tag in visual_tags:
                            if _is_transparent:
                                # Make the icon invisible (transparent / cutout)
                                el.set('fill', 'none')
                                if el.get('stroke'):
                                    el.set('stroke', 'none')
                            else:
                                current_fill = el.get('fill', '')
                                if current_fill and current_fill.lower() not in ('none', 'transparent', 'currentcolor'):
                                    el.set('fill', color)
                                elif not current_fill and tag != 'g':
                                    el.set('fill', color)
                                
                                if el.get('stroke') and el.get('stroke').lower() not in ('none', 'transparent'):
                                    el.set('stroke', color)
                        
                        for child in el:
                            apply_color_preserve_animation(child)
                    
                    apply_color_preserve_animation(root)
                    
                    # Apply scale if provided and no background will be added
                    if scale is not None and scale != 1.0:
                        # Wrap content in a scaled group
                        vb = root.get("viewBox", "0 0 24 24").split()
                        vb_x, vb_y, vb_w, vb_h = map(float, vb)
                        
                        # Create wrapper group with transform
                        g = ET.Element("g")
                        cx, cy = vb_w / 2, vb_h / 2
                        g.set("transform", f"translate({cx},{cy}) scale({scale}) translate({-cx},{-cy})")
                        
                        # Move all children to the group
                        for child in list(root):
                            root.remove(child)
                            g.append(child)
                        root.append(g)
                    
                    return ET.tostring(root, encoding="unicode")
                    
                except Exception as e:
                    print(f"Warning: Could not apply color with animation preservation: {e}")
                    # Fall back to raster method if XML manipulation fails
                    return self.recolor_svg_to_single_color(svg_content, color, size or 256)
            
            # For solid colors without animation preservation (multi-color recoloring)
            if color:
                return self.recolor_svg_to_single_color(svg_content, color, size or 256)
        
        except Exception as e:
            print(f"Warning: Could not modify SVG: {e}")
            return svg_content

    # -------------------- LOCAL FILE --------------------
    def load_local_file(self, file_path: str, target_color: Optional[str] = None, target_size: Optional[int] = None) -> Optional[tuple[str, bool]]:
        """Load local image file. Returns (svg_content, is_raster_image).
        
        For raster images, if target_color is provided, recolors during load.
        If target_size is provided, resizes the image.
        Returns a tuple: (svg_content, is_raster_image)
        """
        file_path = Path(file_path)
        is_jpeg = file_path.suffix.lower() in (".jpg", ".jpeg")
        
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return None

        if file_path.suffix.lower() == '.svg':
            try:
                svg_content = file_path.read_text(encoding='utf-8')
                return (svg_content, False)  # Not a raster image
            except Exception as e:
                print(f"Error reading SVG file {file_path}: {e}")
                return None

        if not RASTER_AVAILABLE:
            print("Error: PIL not available. Cannot process raster images.")
            return None

        try:
            img = Image.open(file_path).convert("RGBA")
            
            # Resize if requested: preserve aspect ratio and fit within target_size
            orig_w, orig_h = img.size
            if target_size:
                ratio = min(target_size / orig_w, target_size / orig_h)
                if ratio < 1:
                    new_w = max(1, int(round(orig_w * ratio)))
                    new_h = max(1, int(round(orig_h * ratio)))
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            width, height = img.size
            
            # Apply color transformation if requested (only for solid colors, not gradients)
            if target_color:
                if is_jpeg:
                    print(
                        "Warning: JPEG images do not support safe recoloring. "
                        "Please use SVG, PNG or WebP images with transparency to apply colors."
                    )
                else:
                    target_rgb = parse_color(target_color)
                    pixels = list(img.getdata())
                    new_pixels = []
                    for r, g, b, a in pixels:
                        if a > 0:
                            new_pixels.append((*target_rgb, a))
                        else:
                            new_pixels.append((r, g, b, a))
                    img.putdata(new_pixels)

            from base64 import b64encode
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = b64encode(buffer.getvalue()).decode('utf-8')

            svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n<image width="{width}" height="{height}" href="data:image/png;base64,{img_data}" />\n</svg>'
            return (svg_content, True)  # Is a raster image

        except Exception as e:
            print(f"Error converting {file_path} to SVG: {e}")
            import traceback
            traceback.print_exc()
            return None

    # -------------------- FETCH ICONS --------------------
    def get_icon_from_url(self, url: str, target_size: Optional[int] = None) -> Optional[tuple[str, bool]]:
        """Fetch an icon from a direct URL.

        Returns a tuple (svg_content, is_raster_image).
        For SVG responses returns the SVG text and False. For raster images
        (png/jpg/webp/etc) returns an SVG wrapper embedding the image as
        a data URI and True.
        """
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            r.raise_for_status()

            content_type = r.headers.get("Content-Type", "")

            # SVG content
            if 'svg' in content_type or url.lower().endswith('.svg'):
                try:
                    return (r.text, False)
                except Exception:
                    return (r.content.decode('utf-8', errors='replace'), False)

            # Raster content (png, jpeg, webp, etc.) - embed as data URI inside an SVG
            if content_type.startswith('image/') or any(url.lower().endswith(ext) for ext in ('.png', '.jpg', '.jpeg', '.webp')):
                data = r.content
                from base64 import b64encode

                # If we can, open and optionally resize the image to the target size
                if RASTER_AVAILABLE:
                    try:
                        img = Image.open(BytesIO(data)).convert('RGBA')
                        # If a target_size was requested, resize to fit within that size
                        # while preserving original aspect ratio (do not force a square).
                        orig_w, orig_h = img.size
                        if target_size:
                            ratio = min(target_size / orig_w, target_size / orig_h)
                            if ratio < 1:
                                new_w = max(1, int(round(orig_w * ratio)))
                                new_h = max(1, int(round(orig_h * ratio)))
                                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        width, height = img.size

                        # Re-encode as PNG for consistent embedding
                        buf = BytesIO()
                        img.save(buf, format='PNG')
                        b64 = b64encode(buf.getvalue()).decode('utf-8')
                        subtype = 'png'
                    except Exception:
                        # Fallback to original bytes if PIL processing fails
                        subtype = content_type.split('/')[-1].split(';')[0] if '/' in content_type else 'png'
                        b64 = b64encode(data).decode('utf-8')
                        width = height = target_size or 256
                else:
                    subtype = content_type.split('/')[-1].split(';')[0] if '/' in content_type else 'png'
                    b64 = b64encode(data).decode('utf-8')
                    width = height = target_size or 256

                svg_content = (
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n'
                    f'<image width="{width}" height="{height}" href="data:image/{subtype};base64,{b64}" />\n'
                    '</svg>'
                )
                return (svg_content, True)

            # Fallback: try to decode as text
            return (r.text, False)
        except Exception as e:
            print(f"Error fetching from URL {url}: {e}")
            return None

    def get_icon_svg(self, icon_name: str, color: str = "currentColor") -> Optional[str]:
        try:
            r = requests.get(f"{self.ICONIFY_API}/{icon_name}.svg", params={"color":color}, timeout=10)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"Error fetching icon {icon_name}: {e}")
            return None

    def save_svg(self, svg_content: str, output_path: Path) -> bool:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(svg_content, encoding="utf-8")
            return output_path
        except Exception as e:
            print(f"Error saving {output_path}: {e}")
            return False

    def generate_ico(self, svg_content: str, output_path: Path, size: int = 256) -> Path:
        """Generate ICO from SVG."""
        png_bytes = cairosvg.svg2png(
            bytestring=svg_content.encode("utf-8"),
            output_width=size,
            output_height=size,
        )
        img = Image.open(BytesIO(png_bytes)).convert("RGBA")
        img.save(output_path, format="ICO", sizes=[(size, size)])
        img.close()
        return output_path

    # -------------------- GENERATE ICON --------------------
    def generate_icon(
        self,
        icon_name: Optional[str] = None,
        direct_url: Optional[str] = None,
        local_file: Optional[str] = None,
        output_name: Optional[str] = None,
        format: FormatType = "svg",
        size: Optional[int] = None,
        scale: Optional[float] = None,
        color: Optional[Union[str, tuple[str, str]]] = None,
        direction: str = "horizontal",
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        bg_direction: str = "horizontal",
        border_radius: int = 0,
        outline_width: int = 0,
        outline_color: Optional[str] = None,
        animation: Optional[Union[str, dict]] = None,
    ) -> Optional[Path]:
        size = size or 256
        is_raster_source = False
        
        # Determine effective scale based on whether background will be applied
        # Default: 0.7 (70%) if bg is present, 1.0 (100%) if no bg
        has_background = (bg_color is not None or border_radius > 0 or outline_width > 0)
        effective_scale = scale if scale is not None else (0.7 if has_background else 1.0)
        is_cutout = (
            isinstance(color, str)
            and color.strip().lower() in ('transparent', 'none')
            and has_background
        )

        if local_file:
            # Check if it's a JPEG and color is requested
            file_path = Path(local_file)
            is_jpeg = file_path.suffix.lower() in (".jpg", ".jpeg")
            
            if is_jpeg and color:
                print(
                    "Error: JPEG images do not support recoloring. "
                    "Please use SVG, PNG or WebP images with transparency to apply colors."
                )
                return None
            
            # Don't pass gradient colors to load_local_file - it only handles solid colors
            # Also don't pass transparent/cutout color - we handle that at the wrapping stage
            solid_color = color if (color and not isinstance(color, tuple) and not is_cutout) else None
            result = self.load_local_file(local_file, solid_color, size)
            if result is None:
                return None
            svg_content, is_raster_source = result
            
            # If color is a gradient and it's a raster source, apply gradient now
            if isinstance(color, tuple) and is_raster_source:
                svg_content = self.apply_gradient_via_raster(
                    svg_content, 
                    color[0], 
                    color[1], 
                    size, 
                    direction=direction
                )

        elif direct_url:
            result = self.get_icon_from_url(direct_url, target_size=size)
            if result is None:
                return None
            svg_content, is_raster_source = result

            # If color is a gradient and the source is raster, apply gradient now
            if isinstance(color, tuple) and is_raster_source:
                svg_content = self.apply_gradient_via_raster(
                    svg_content,
                    color[0],
                    color[1],
                    size,
                    direction=direction,
                )

        elif icon_name:
            fetch_color = "black" if (
                isinstance(color, tuple) or
                (isinstance(color, str) and color.lower() in ('transparent', 'none'))
            ) else (color or "currentColor")
            svg_content = self.get_icon_svg(icon_name, fetch_color)

        else:
            print("Error: Must provide icon_name, direct_url, or local_file")
            return None

        if not svg_content:
            return None

        # Apply color + size + scale transformations
        # For raster sources, only apply scale if no background (color already applied during load)
        # For vector sources, apply color, size, and scale if no background
        effective_color = None if is_cutout else color

        if not is_raster_source:
            svg_content = self.modify_svg(
                svg_content,
                effective_color,
                size,
                preserve_animations=True,
                direction=direction,
                scale=effective_scale if not has_background else None,
            )
        elif not has_background and effective_scale != 1.0:
            # For raster sources without background, apply scale transformation
            svg_content = self.modify_svg(
                svg_content,
                None,  # No color change needed
                size,
                preserve_animations=False,
                direction=direction,
                scale=effective_scale,
            )

        # Apply animation presets (SVG-native) if requested for all sources
        if animation:
            try:
                svg_content = Animator().apply(svg_content, animation)
            except Exception as e:
                print(f"Warning: failed to apply animation: {e}")

        # Background / outline wrapper (keep a copy of pre-wrapped svg for exporters)
        svg_before_bg = svg_content
        if has_background:
            svg_content = self.wrap_with_background(
                svg_content,
                size,
                bg_color,
                border_radius,
                outline_width,
                outline_color,
                bg_direction=bg_direction,
                scale=effective_scale,
                cutout=is_cutout,
            )

        if output_name is None:
            if local_file:
                output_name = Path(local_file).stem
            elif icon_name:
                output_name = icon_name.replace(":", "_").replace("/", "_")
            else:
                output_name = "icon"

        format = (format or "svg").lower()

        output_path = self.output_dir / f"{output_name}.{format}"

        if format == "svg":
            return output_path if self.save_svg(svg_content, output_path) else None

        elif format == "ico":
            return self.generate_ico(svg_content, output_path, size)

        elif format in ("png", "webp", "jpg", "jpeg"):
            if not RASTER_AVAILABLE:
                print("Error: PIL/cairosvg not available. Cannot generate raster formats.")
                return None

            # For cutout mode cairosvg does not reliably render SVG <mask> elements,
            # so we composite manually with PIL:
            #   1. rasterize the background rect (no icon)
            #   2. rasterize the icon at the same position (transparent background)
            #   3. new_alpha = bg_alpha * (1 - icon_alpha/255)  →  icon punches a hole
            if is_cutout:
                from PIL import ImageChops, ImageOps

                # Icon centred/scaled the same way as in the background composite,
                # but rendered on a transparent canvas
                icon_positioned_svg = self.wrap_with_background(
                    svg_before_bg, size,
                    bg_color=None, border_radius=0, outline_width=0,
                    scale=effective_scale, cutout=False,
                )
                # Background-only SVG: use a 1 px transparent placeholder icon so
                # the rect geometry (border-radius, outline, gradient) is identical
                bg_only_svg = self.wrap_with_background(
                    '<svg xmlns="http://www.w3.org/2000/svg" '
                    'viewBox="0 0 1 1" width="1" height="1"/>',
                    size, bg_color, border_radius, outline_width, outline_color,
                    bg_direction=bg_direction, scale=effective_scale, cutout=False,
                )
                icon_bytes_raw = cairosvg.svg2png(
                    bytestring=icon_positioned_svg.encode('utf-8'),
                    output_width=size, output_height=size,
                )
                bg_bytes_raw = cairosvg.svg2png(
                    bytestring=bg_only_svg.encode('utf-8'),
                    output_width=size, output_height=size,
                )
                bg_img = Image.open(BytesIO(bg_bytes_raw)).convert("RGBA")
                icon_img = Image.open(BytesIO(icon_bytes_raw)).convert("RGBA")
                r, g, b, bg_a = bg_img.split()
                _, _, _, icon_a = icon_img.split()
                # Invert icon alpha: opaque icon pixel (255) → 0; transparent (0) → 255
                inv_icon_a = ImageOps.invert(icon_a)
                # multiply(a, b) = a*b/255  →  bg_a * (1 - icon_a/255)
                new_alpha = ImageChops.multiply(bg_a, inv_icon_a)
                result_img = Image.merge("RGBA", (r, g, b, new_alpha))
                buf = BytesIO()
                result_img.save(buf, format='PNG')
                png_bytes = buf.getvalue()
            else:
                # Convert SVG to PNG bytes
                png_bytes = cairosvg.svg2png(
                    bytestring=svg_content.encode('utf-8'),
                    output_width=size,
                    output_height=size,
                )
            
            if format == "png":
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(png_bytes)
                return output_path
            # Handle other raster formats
            if format in ("jpg", "jpeg"):
                image = Image.open(BytesIO(png_bytes))
                # Convert RGBA to RGB for JPEG (no transparency support)
                if image.mode == "RGBA":
                    rgb_image = Image.new("RGB", image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])  # Use alpha as mask
                    image = rgb_image
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path, format='JPEG', quality=95)
                image.close()
                return output_path

            if format == "webp":
                # If an SVG-native animation was requested and source is vector,
                # rasterize multiple frames and save an animated WebP.
                if animation and not is_raster_source:
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    # Rasterize frames from the pre-wrap (icon-only) SVG and
                    # let the exporter composite the background so transforms
                    # and centering are handled consistently.
                    src_svg_for_export = svg_before_bg or svg_content
                    
                    # Important: if no background, scale was already applied in modify_svg,
                    # so pass scale=1.0 to avoid double-scaling. If there's a background,
                    # wrap_with_background will handle it, so pass effective_scale.
                    webp_scale = 1.0 if not has_background else effective_scale
                    
                    result = svg_animation_to_webp(
                        src_svg_for_export,
                        output_path,
                        animation,
                        size=size,
                        fps=20,
                        loop=0,
                        quality=95,
                        bg_color=bg_color,
                        border_radius=border_radius,
                        outline_width=outline_width,
                        outline_color=outline_color,
                        bg_direction=bg_direction,
                        scale=webp_scale,
                    )
                    if result:
                        return Path(result)
                    # fall through to static webp saving on failure

                # Fallback: static webp from single-frame PNG
                image = Image.open(BytesIO(png_bytes))
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path, format='WEBP', quality=95)
                image.close()
                return output_path

        else:
            raise ValueError(f"Unsupported format: {format}")

    # -------------------- BATCH --------------------
    def generate_batch(
        self,
        icons: dict[str, str | dict],
        size: Optional[int] = None,
        scale: Optional[float] = None,
        color: Optional[Union[str, tuple[str, str]]] = None,
        direction: str = "horizontal",
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        bg_direction: str = "horizontal",
        border_radius: int = 0,
        outline_width: int = 0,
        outline_color: Optional[str] = None,
        animation: Optional[Union[str, dict]] = None,
    ) -> list[Path]:
        """Generate multiple icons at once."""
        results: list[Path] = []

        for output_name, icon_config in icons.items():
            print(f"\nGenerating {output_name}...")

            if isinstance(icon_config, str):
                path = self.generate_icon(
                    icon_name=icon_config,
                    output_name=output_name,
                    size=size,
                    scale=scale,
                    color=color,
                    direction=direction,
                    bg_color=bg_color,
                    bg_direction=bg_direction,
                    border_radius=border_radius,
                    outline_width=outline_width,
                    outline_color=outline_color,
                    animation=animation,
                )

            elif isinstance(icon_config, dict):
                path = self.generate_icon(
                    icon_name=icon_config.get("icon"),
                    direct_url=icon_config.get("url"),
                    local_file=icon_config.get("local_file"),
                    output_name=output_name,
                    size=icon_config.get("size", size),
                    scale=icon_config.get("scale", scale),
                    color=icon_config.get("color", color),
                    direction=icon_config.get("direction", direction),
                    bg_color=icon_config.get("bg_color", bg_color),
                    bg_direction=icon_config.get("bg_direction", bg_direction),
                    border_radius=icon_config.get("border_radius", border_radius),
                    outline_width=icon_config.get("outline_width", outline_width),
                    outline_color=icon_config.get("outline_color", outline_color),
                    animation=icon_config.get("animation", animation),
                )

            else:
                print(f"Invalid config for {output_name}")
                continue

            if path:
                results.append(path)

        return results