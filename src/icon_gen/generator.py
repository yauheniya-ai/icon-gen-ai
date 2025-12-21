"""Core icon generation logic using Iconify API and direct URLs."""

import requests
import re
from pathlib import Path
from typing import Optional, Literal, Union
from xml.etree import ElementTree as ET

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
        if direction == "vertical":
            x1, y1, x2, y2 = "0%", "0%", "0%", "100%"
        else:
            x1, y1, x2, y2 = "0%", "0%", "100%", "0%"

        return f"""
<defs>
  <linearGradient id="{gradient_id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
    <stop offset="0%" stop-color="{color1}" />
    <stop offset="100%" stop-color="{color2}" />
  </linearGradient>
</defs>
"""

    def wrap_with_background(
        self,
        svg_content: str,
        size: int,
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_radius: int = 0,
    ) -> str:

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

        return f"""
<svg xmlns="http://www.w3.org/2000/svg"
     width="{size}" height="{size}" viewBox="0 0 {size} {size}">
{gradient_def}
<rect width="{size}" height="{size}" rx="{border_radius}" ry="{border_radius}" fill="{bg_fill}" />
<g transform="translate({tx},{ty}) scale({scale}) translate({-vb_w/2},{-vb_h/2})">
{icon_elements}
</g>
</svg>
"""

    def modify_svg(
        self,
        svg_content: str,
        color: Optional[Union[str, tuple[str, str]]] = None,
        size: Optional[int] = None,
    ) -> str:
        try:
            root = ET.fromstring(svg_content)

            if not root.get("viewBox"):
                w = re.sub(r"[^\d.]", "", root.get("width", "24"))
                h = re.sub(r"[^\d.]", "", root.get("height", "24"))
                root.set("viewBox", f"0 0 {w} {h}")

            if size:
                root.set("width", str(size))
                root.set("height", str(size))

            if color:
                if isinstance(color, tuple):
                    # Insert gradient
                    gradient_elem = ET.fromstring(
                        self.create_gradient_def("iconGradient", color[0], color[1])
                    )
                    root.insert(0, gradient_elem)

                    # Recursively apply gradient fill
                    def apply_gradient(el):
                        if el.tag.endswith(("path","circle","rect","polygon","ellipse","g")):
                            el.set("fill", "url(#iconGradient)")
                            if el.get("stroke"):
                                el.set("stroke", "url(#iconGradient)")
                        for child in el:
                            apply_gradient(child)

                    apply_gradient(root)

                else:
                    # Solid color
                    def apply_color(el):
                        if el.tag.endswith(("path","circle","rect","polygon","ellipse","g")):
                            el.set("fill", color)
                            if el.get("stroke"):
                                el.set("stroke", color)
                        for child in el:
                            apply_color(child)

                    apply_color(root)

            return ET.tostring(root, encoding="unicode")
        except Exception as e:
            print(f"Warning: Could not modify SVG: {e}")
            return svg_content


    def get_icon_from_url(self, url: str) -> Optional[str]:
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"Error fetching from URL {url}: {e}")
            return None

    def get_icon_svg(self, icon_name: str, color: str = "white") -> Optional[str]:
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
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(svg_content, encoding="utf-8")
            print(f"✓ Saved: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving {output_path}: {e}")
            return False

    def generate_icon(
        self,
        icon_name: str,
        output_name: Optional[str] = None,
        color: Optional[Union[str, tuple[str, str]]] = None,
        size: Optional[int] = None,
        format: FormatType = "svg",
        direct_url: Optional[str] = None,
        bg_color: Optional[Union[str, tuple[str, str]]] = None,
        border_radius: int = 0,
    ) -> Optional[Path]:
        size = size or 256

        if direct_url:
            svg_content = self.get_icon_from_url(direct_url)
            if svg_content:
                svg_content = self.modify_svg(svg_content, color, size)
        else:
            if isinstance(color, tuple):
                svg_content = self.get_icon_svg(icon_name, "currentColor")
                if svg_content:
                    svg_content = self.modify_svg(svg_content, color, size)
            else:
                svg_content = self.get_icon_svg(icon_name, color or "currentColor")
                if svg_content:
                    svg_content = self.modify_svg(svg_content, None, size)

        if not svg_content:
            return None

        if bg_color is not None or border_radius > 0:
            svg_content = self.wrap_with_background(svg_content, size, bg_color, border_radius)

        if output_name is None:
            output_name = icon_name.replace(":", "_").replace("/", "_")

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
                    icon_config.get("icon", ""),
                    output_name,
                    icon_config.get("color", color),
                    icon_config.get("size", size),
                    direct_url=icon_config.get("url"),
                    bg_color=icon_config.get("bg_color", bg_color),
                    border_radius=icon_config.get("border_radius", border_radius),
                )
            else:
                continue

            if path:
                results.append(path)

        return results
