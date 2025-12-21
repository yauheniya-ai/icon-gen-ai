"""Core icon generation logic using Iconify API."""

import requests
from pathlib import Path
from typing import Optional, Literal

FormatType = Literal['svg', 'png', 'webp']


class IconGenerator:
    """Generate and customize icons from Iconify."""
    
    ICONIFY_API = "https://api.iconify.design"
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the icon generator.
        
        Args:
            output_dir: Directory where icons will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def get_icon_svg(self, icon_name: str, color: str = "white") -> Optional[str]:
        """Fetch SVG icon from Iconify API.
        
        Args:
            icon_name: Icon identifier (e.g., 'mdi:github', 'simple-icons:openai')
            color: Color for the icon (default: white)
            
        Returns:
            SVG content as string, or None if request fails
        """
        # Iconify API endpoint for SVG with color
        url = f"{self.ICONIFY_API}/{icon_name}.svg"
        params = {'color': color}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching icon {icon_name}: {e}")
            return None
    
    def save_svg(self, svg_content: str, output_path: Path) -> bool:
        """Save SVG content to file.
        
        Args:
            svg_content: SVG markup as string
            output_path: Path where to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(svg_content, encoding='utf-8')
            print(f"✓ Saved: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving {output_path}: {e}")
            return False
    
    def generate_icon(
        self,
        icon_name: str,
        output_name: Optional[str] = None,
        color: str = "white",
        format: FormatType = 'svg'
    ) -> Optional[Path]:
        """Generate and save an icon.
        
        Args:
            icon_name: Icon identifier from Iconify
            output_name: Custom output filename (without extension)
            color: Icon color
            format: Output format (currently only 'svg' supported)
            
        Returns:
            Path to saved file, or None if failed
        """
        if format != 'svg':
            print(f"Warning: Format '{format}' not yet implemented, using SVG")
        
        # Fetch the icon
        svg_content = self.get_icon_svg(icon_name, color)
        if not svg_content:
            return None
        
        # Determine output filename
        if output_name is None:
            # Use the icon name, replacing ':' with '_'
            output_name = icon_name.replace(':', '_').replace('/', '_')
        
        output_path = self.output_dir / f"{output_name}.svg"
        
        # Save the file
        if self.save_svg(svg_content, output_path):
            return output_path
        return None
    
    def generate_batch(self, icons: dict[str, str], color: str = "white") -> list[Path]:
        """Generate multiple icons at once.
        
        Args:
            icons: Dictionary mapping output names to icon identifiers
            color: Color for all icons
            
        Returns:
            List of paths to successfully generated icons
        """
        results = []
        for output_name, icon_name in icons.items():
            print(f"\nGenerating {output_name}...")
            path = self.generate_icon(icon_name, output_name, color)
            if path:
                results.append(path)
        return results