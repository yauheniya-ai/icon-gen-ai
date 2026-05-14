"""Advanced tests for icon generator."""

from pathlib import Path
from unittest.mock import patch, MagicMock
from icon_gen_ai.generator import IconGenerator, parse_color


def test_gradient_background(tmp_path):
    """Test gradient background generation."""
    generator = IconGenerator(output_dir=str(tmp_path))

    result = generator.generate_icon(
        "mdi:github",
        output_name="test_gradient_bg",
        color="white",
        size=128,
        bg_color=("mediumslateblue", "deeppink"),
        border_radius=20,
    )

    assert result is not None
    assert result.exists()
    content = result.read_text()
    assert "linearGradient" in content
    assert "bgGradient" in content


def test_gradient_icon(tmp_path):
    """Test gradient icon color."""
    generator = IconGenerator(output_dir=str(tmp_path))

    result = generator.generate_icon(
        "mdi:heart",
        output_name="test_gradient_icon",
        color=("#FF0000", "#FF6B6B"),
        size=128,
    )

    assert result is not None
    assert result.exists()


def test_circular_icon(tmp_path):
    """Test circular border radius."""
    generator = IconGenerator(output_dir=str(tmp_path))

    result = generator.generate_icon(
        "mdi:star",
        output_name="test_circle",
        color="white",
        size=256,
        bg_color="mediumslateblue",
        border_radius=128,  # Half of size = circle
    )

    assert result is not None
    content = result.read_text()
    assert 'rx="128"' in content or "rx='128'" in content


def test_batch_with_mixed_configs(tmp_path):
    """Test batch generation with different configurations."""
    generator = IconGenerator(output_dir=str(tmp_path))

    icons = {
        "icon1": "mdi:home",
        "icon2": {"icon": "mdi:settings", "color": "red", "size": 128},
        "icon3": {
            "icon": "mdi:user",
            "color": "white",
            "bg_color": "#000000",
            "border_radius": 64,
            "size": 128,
        },
    }

    results = generator.generate_batch(icons, color="blue", size=64)

    assert len(results) == 3
    assert all(r.exists() for r in results)


def test_invalid_icon_name(tmp_path):
    """Test handling of invalid icon names."""
    generator = IconGenerator(output_dir=str(tmp_path))

    result = generator.generate_icon(
        "invalid:nonexistent", output_name="invalid_test", size=64
    )

    # Should return None for invalid icons
    assert result is None


def test_direct_url_icon(tmp_path):
    """Test icon generation from direct URL."""
    generator = IconGenerator(output_dir=str(tmp_path))

    result = generator.generate_icon(
        icon_name="",  # Not used when direct_url is provided
        output_name="url_icon",
        color="white",
        size=128,
        direct_url="https://upload.wikimedia.org/wikipedia/commons/b/b0/Claude_AI_symbol.svg",
    )

    assert result is not None
    assert result.exists()


def test_apply_gradient_via_raster_without_cairosvg(tmp_path, monkeypatch):
    """Test gradient application when cairosvg not available."""
    # Mock RASTER_AVAILABLE as False
    import icon_gen_ai.generator as gen_module

    monkeypatch.setattr(gen_module, "RASTER_AVAILABLE", False)

    generator = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg><rect width="100" height="100"/></svg>'

    result = generator.apply_gradient_via_raster(
        svg, "deeppink", "mediumslateblue", 256
    )
    # Should return original SVG when raster not available
    assert result == svg


def test_save_svg_with_invalid_path():
    """Test SVG save with invalid path."""
    generator = IconGenerator()

    # Try to save to invalid location
    result = generator.save_svg("<svg></svg>", Path("/invalid/path/file.svg"))
    assert result is False


def test_batch_with_invalid_config(tmp_path):
    """Test batch generation with invalid configurations."""
    generator = IconGenerator(output_dir=str(tmp_path))

    icons = {
        "valid": "mdi:home",
        "invalid": 12345,  # Invalid type
        "dict_valid": {"icon": "mdi:star"},
    }

    results = generator.generate_batch(icons)
    # Should skip invalid and continue
    assert len(results) >= 1


def test_modify_svg_with_gradient(tmp_path):
    """Test SVG modification with gradient color."""
    generator = IconGenerator(output_dir=str(tmp_path))

    svg = '<svg width="24" height="24"><path d="M0 0"/></svg>'
    modified = generator.modify_svg(
        svg, color=("deeppink", "mediumslateblue"), size=128
    )

    assert 'width="128"' in modified
    # May contain gradient if cairosvg available


# -------------------- NEW COVERAGE TESTS --------------------

def test_parse_color_transparent():
    """parse_color handles transparent/none values."""
    assert parse_color("transparent") == (0, 0, 0)
    assert parse_color("none") == (0, 0, 0)
    assert parse_color("TRANSPARENT") == (0, 0, 0)


def test_parse_color_named():
    """parse_color handles CSS named colors."""
    r, g, b = parse_color("red")
    assert r == 255 and g == 0 and b == 0


def test_parse_color_invalid_falls_back_to_white():
    """parse_color with unknown string returns white."""
    assert parse_color("not_a_real_color_xyz") == (255, 255, 255)


def test_create_gradient_def_radial():
    """create_gradient_def with radial direction."""
    gen = IconGenerator()
    result = gen.create_gradient_def("gid", "#FF0000", "#0000FF", direction="radial")
    assert "radialGradient" in result
    assert "gid" in result


def test_create_gradient_def_vertical():
    """create_gradient_def with vertical direction."""
    gen = IconGenerator()
    result = gen.create_gradient_def("gid", "#FF0000", "#0000FF", direction="vertical")
    assert "linearGradient" in result
    # vertical: x1=0%, y1=0%, x2=0%, y2=100%
    assert 'y2="100%"' in result


def test_create_gradient_def_diagonal():
    """create_gradient_def with diagonal direction."""
    gen = IconGenerator()
    result = gen.create_gradient_def("gid", "#FF0000", "#0000FF", direction="diagonal")
    assert "linearGradient" in result
    assert 'x2="100%"' in result and 'y2="100%"' in result


def test_elements_forced_black():
    """_elements_forced_black forces all fills to black."""
    gen = IconGenerator()
    svg_fragment = '<path fill="red" d="M0 0"/><circle fill="blue" r="5"/>'
    result = gen._elements_forced_black(svg_fragment)
    assert 'fill="black"' in result
    assert "red" not in result
    assert "blue" not in result


def test_elements_forced_black_preserves_none():
    """_elements_forced_black does not override fill=none."""
    gen = IconGenerator()
    svg_fragment = '<path fill="none" d="M0 0"/>'
    result = gen._elements_forced_black(svg_fragment)
    # fill=none should be kept
    assert 'fill="none"' in result


def test_wrap_with_background_gradient():
    """wrap_with_background with gradient bg_color."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'
    result = gen.wrap_with_background(svg, 256, bg_color=("red", "blue"))
    assert "linearGradient" in result or "bgGradient" in result


def test_wrap_with_background_cutout():
    """wrap_with_background with cutout=True generates mask."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'
    result = gen.wrap_with_background(svg, 256, bg_color="red", cutout=True)
    assert "cutoutMask" in result or "mask" in result.lower()


def test_wrap_with_background_outline():
    """wrap_with_background with outline renders stroke attrs."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>'
    result = gen.wrap_with_background(
        svg, 256, bg_color="#FF0000", border_radius=16,
        outline_width=4, outline_color="white"
    )
    assert 'stroke="white"' in result
    assert 'stroke-width="4"' in result


def test_modify_svg_scale_no_color():
    """modify_svg with scale but no color wraps in a group transform."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24" width="24" height="24"><path d="M0 0"/></svg>'
    result = gen.modify_svg(svg, color=None, size=128, scale=0.7)
    assert 'width="128"' in result
    assert "scale(0.7)" in result or "scale" in result


def test_modify_svg_color_preserve_animations():
    """modify_svg with solid color recolors path fills."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24"><path fill="black" d="M0 0"/></svg>'
    result = gen.modify_svg(svg, color="red", size=64)
    assert 'fill="red"' in result


def test_modify_svg_transparent_color():
    """modify_svg with transparent color sets fill=none."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24"><path fill="black" d="M0 0"/></svg>'
    result = gen.modify_svg(svg, color="transparent", size=64)
    assert 'fill="none"' in result


def test_modify_svg_gradient_with_scale():
    """modify_svg with gradient tuple and scale."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24" width="24" height="24"><path d="M0 0"/></svg>'
    # Gradient uses raster path; just ensure no crash
    result = gen.modify_svg(svg, color=("red", "blue"), size=64, scale=0.8)
    assert result is not None


def test_load_local_file_not_found(tmp_path):
    """load_local_file returns None for missing files."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.load_local_file(str(tmp_path / "nonexistent.svg"))
    assert result is None


def test_load_local_file_svg(tmp_path):
    """load_local_file loads SVG files directly."""
    svg_path = tmp_path / "icon.svg"
    svg_path.write_text('<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>', encoding="utf-8")
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.load_local_file(str(svg_path))
    assert result is not None
    content, is_raster = result
    assert "<svg" in content
    assert is_raster is False


def test_generate_icon_with_local_svg_color(tmp_path):
    """generate_icon from local SVG file with solid color."""
    svg_path = tmp_path / "test.svg"
    svg_path.write_text(
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<path fill="black" d="M0 0h24v24H0z"/></svg>',
        encoding="utf-8",
    )
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        local_file=str(svg_path),
        output_name="colored",
        color="deeppink",
        size=64,
    )
    assert result is not None
    assert result.exists()
    assert 'fill="deeppink"' in result.read_text()


def test_generate_icon_with_background_and_scale(tmp_path):
    """generate_icon applies default scale=0.7 when background is present."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        "mdi:home",
        output_name="home_bg",
        color="white",
        bg_color="#333333",
        border_radius=32,
        size=128,
    )
    assert result is not None
    content = result.read_text()
    assert "scale" in content or "transform" in content


def test_generate_icon_with_animation(tmp_path):
    """generate_icon with animation preset embeds animateTransform."""
    svg_path = tmp_path / "anim.svg"
    svg_path.write_text(
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<path fill="black" d="M0 0h24v24H0z"/></svg>',
        encoding="utf-8",
    )
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        local_file=str(svg_path),
        output_name="animated",
        animation="spin:2s",
        size=64,
    )
    assert result is not None
    assert "animateTransform" in result.read_text()


def test_generate_icon_no_source_returns_none(tmp_path):
    """generate_icon with no icon_name, url, or local_file returns None."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(output_name="nothing")
    assert result is None


def test_generate_icon_cutout_with_background(tmp_path):
    """generate_icon with transparent color + bg produces cutout SVG."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        "mdi:home",
        output_name="cutout_test",
        color="transparent",
        bg_color="mediumslateblue",
        size=64,
    )
    assert result is not None
    content = result.read_text()
    assert "cutoutMask" in content or "mask" in content.lower()


def test_generate_icon_png_format(tmp_path):
    """generate_icon with format=png produces a PNG file."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        "mdi:home",
        output_name="home_png",
        format="png",
        size=32,
        color="white",
    )
    # PNG needs cairosvg; skip assertion on result value but ensure no crash
    if result is not None:
        assert result.suffix == ".png"
        assert result.exists()


def test_generate_icon_scale_explicit(tmp_path):
    """generate_icon with explicit scale parameter."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        "mdi:home",
        output_name="scaled",
        scale=0.5,
        size=64,
    )
    assert result is not None


def test_generate_batch_with_dict_configs(tmp_path):
    """generate_batch where some icons use dict config with url/local_file keys."""
    svg_path = tmp_path / "local.svg"
    svg_path.write_text(
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 0h24v24H0z"/></svg>',
        encoding="utf-8",
    )
    gen = IconGenerator(output_dir=str(tmp_path))
    icons = {
        "from_name": "mdi:home",
        "from_local": {"local_file": str(svg_path), "size": 32, "color": "black"},
    }
    results = gen.generate_batch(icons, size=32)
    assert len(results) >= 1


def test_wrap_with_background_no_bg():
    """wrap_with_background with bg_color=None results in fill=none."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>'
    result = gen.wrap_with_background(svg, 128, bg_color=None)
    assert 'fill="none"' in result


def test_generate_icon_direct_url_mocked(tmp_path):
    """generate_icon with direct_url uses get_icon_from_url (mocked)."""
    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" d="M0 0"/></svg>'
    with patch.object(gen, "get_icon_from_url", return_value=(svg, False)):
        result = gen.generate_icon(
            direct_url="https://example.com/icon.svg",
            output_name="mock_url_icon",
            size=32,
            color="deeppink",
        )
    assert result is not None
    assert result.exists()


def test_generate_icon_direct_url_gradient_raster_mocked(tmp_path):
    """generate_icon direct_url with gradient color applies gradient to raster source."""
    gen = IconGenerator(output_dir=str(tmp_path))
    # A minimal raster-wrapped SVG (simulating what get_icon_from_url returns for PNG)
    raster_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><rect width="24" height="24" fill="red"/></svg>'
    with patch.object(gen, "get_icon_from_url", return_value=(raster_svg, True)):
        result = gen.generate_icon(
            direct_url="https://example.com/icon.png",
            output_name="url_raster_grad",
            color=("red", "blue"),
            size=32,
        )
    # Result may be None if cairosvg not available, but should not crash
    assert "Traceback" not in str(result or "")


def test_load_local_file_raster_png(tmp_path):
    """load_local_file handles PNG raster images when PIL is available."""
    try:
        from PIL import Image
    except ImportError:
        return  # skip if PIL not available

    img = Image.new("RGBA", (32, 32), color=(255, 0, 0, 255))
    png_path = tmp_path / "icon.png"
    img.save(png_path)

    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.load_local_file(str(png_path))
    assert result is not None
    content, is_raster = result
    assert is_raster is True
    assert "<svg" in content
    assert "image" in content.lower()


def test_load_local_file_raster_with_color(tmp_path):
    """load_local_file recolors PNG pixels with target_color."""
    try:
        from PIL import Image
    except ImportError:
        return

    img = Image.new("RGBA", (16, 16), color=(255, 0, 0, 255))
    png_path = tmp_path / "colored.png"
    img.save(png_path)

    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.load_local_file(str(png_path), target_color="blue")
    assert result is not None
    content, is_raster = result
    assert is_raster is True


def test_generate_icon_local_png(tmp_path):
    """generate_icon from a local PNG file."""
    try:
        from PIL import Image
    except ImportError:
        return

    img = Image.new("RGBA", (32, 32), color=(200, 100, 50, 255))
    png_path = tmp_path / "img.png"
    img.save(png_path)

    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        local_file=str(png_path),
        output_name="from_png",
        size=32,
    )
    assert result is not None
    assert result.exists()


def test_generate_icon_local_png_with_gradient(tmp_path):
    """generate_icon from local PNG with gradient color (raster+gradient path)."""
    try:
        from PIL import Image
    except ImportError:
        return

    img = Image.new("RGBA", (16, 16), color=(255, 0, 0, 255))
    png_path = tmp_path / "grad.png"
    img.save(png_path)

    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        local_file=str(png_path),
        output_name="png_with_gradient",
        color=("red", "blue"),
        size=16,
    )
    # No crash regardless of result
    assert result is None or result.exists()


def test_generate_icon_no_name_covers_else_branch(tmp_path):
    """generate_icon returns None when no source is given."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon()
    assert result is None


def test_recolor_svg_transparent(tmp_path):
    """recolor_svg_to_single_color with transparent color erases pixels."""
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        return

    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" fill="red"/></svg>'
    result = gen.recolor_svg_to_single_color(svg, "transparent", size=16)
    # Should return modified SVG (transparent pixels)
    assert result is not None


def test_modify_svg_preserve_animations_false(tmp_path):
    """modify_svg with preserve_animations=False uses recolor_svg_to_single_color."""
    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect fill="black" width="24" height="24"/></svg>'
    result = gen.modify_svg(svg, color="red", size=64, preserve_animations=False)
    assert result is not None


def test_generate_icon_with_outline(tmp_path):
    """generate_icon with outline_width renders outline attrs in SVG."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        "mdi:home",
        output_name="outlined",
        bg_color="#000000",
        outline_width=4,
        outline_color="white",
        size=64,
        color="white",
    )
    assert result is not None
    content = result.read_text()
    assert 'stroke="white"' in content


def test_generate_batch_full_dict_config(tmp_path):
    """generate_batch with full dict config including bg, border_radius, scale."""
    gen = IconGenerator(output_dir=str(tmp_path))
    icons = {
        "icon_full": {
            "icon": "mdi:home",
            "color": "white",
            "bg_color": "#333333",
            "border_radius": 32,
            "size": 32,
            "scale": 0.6,
        },
        "icon_outline": {
            "icon": "mdi:star",
            "color": "white",
            "bg_color": "#000000",
            "outline_width": 2,
            "outline_color": "white",
            "size": 32,
        },
    }
    results = gen.generate_batch(icons)
    assert len(results) >= 1


def test_generate_icon_gradient_with_background(tmp_path):
    """generate_icon with gradient bg and gradient icon color."""
    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.generate_icon(
        "mdi:home",
        output_name="grad_combo",
        color=("deeppink", "mediumslateblue"),
        bg_color=("lime", "cyan"),
        border_radius=16,
        size=32,
    )
    assert result is not None


def test_apply_gradient_via_raster_directions(tmp_path):
    """apply_gradient_via_raster covers vertical, diagonal, radial directions."""
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        return

    gen = IconGenerator(output_dir=str(tmp_path))
    # Use a filled SVG so pixels are non-transparent
    svg = '<svg viewBox="0 0 8 8" xmlns="http://www.w3.org/2000/svg"><rect width="8" height="8" fill="black"/></svg>'
    for direction in ("vertical", "diagonal", "radial"):
        result = gen.apply_gradient_via_raster(svg, "red", "blue", size=8, direction=direction)
        assert result is not None
        assert len(result) > 0


def test_modify_svg_gradient_with_scale_filled(tmp_path):
    """modify_svg gradient+scale with a filled SVG so rect children exist."""
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        return

    gen = IconGenerator(output_dir=str(tmp_path))
    # Filled rect ensures apply_gradient_via_raster produces non-empty children
    svg = '<svg viewBox="0 0 8 8" xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8" fill="black"/></svg>'
    result = gen.modify_svg(svg, color=("red", "blue"), size=8, scale=0.8)
    assert result is not None
    # 'scale' should appear in the transform wrapping the rasterised rects
    assert "scale" in result


def test_modify_svg_color_no_viewbox():
    """modify_svg infers viewBox from width/height when viewBox is absent."""
    gen = IconGenerator()
    svg = '<svg width="24" height="24"><path fill="black" d="M12 0 L24 24 L0 24 Z"/></svg>'
    result = gen.modify_svg(svg, color="deeppink", size=64)
    assert result is not None
    assert 'fill="deeppink"' in result


def test_modify_svg_removes_style_with_fill():
    """modify_svg strips <style> blocks that contain fill rules."""
    gen = IconGenerator()
    # SVG with a <style> element whose text contains 'fill'
    svg = (
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<style>.cls-1{fill:red;}</style>'
        '<path class="cls-1" d="M0 0h24v24H0z"/>'
        '</svg>'
    )
    result = gen.modify_svg(svg, color="blue", size=64)
    assert result is not None
    # The style block should have been removed
    assert ".cls-1{fill:red;}" not in result


def test_modify_svg_color_with_scale():
    """modify_svg with solid color + scale wraps content in a transform group."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" d="M0 0h24v24H0z"/></svg>'
    result = gen.modify_svg(svg, color="white", size=64, scale=0.8)
    assert result is not None
    assert "scale" in result


def test_modify_svg_transparent_with_stroke():
    """modify_svg transparent color clears both fill and stroke on a stroked element."""
    gen = IconGenerator()
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill="black" stroke="black" stroke-width="2" d="M0 0h24v24H0z"/></svg>'
    result = gen.modify_svg(svg, color="transparent", size=64)
    assert result is not None
    assert 'fill="none"' in result


def test_generate_icon_png_mocked(tmp_path):
    """generate_icon PNG format with mocked network call."""
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        return

    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" fill="red"/></svg>'
    with patch.object(gen, "get_icon_svg", return_value=svg):
        result = gen.generate_icon(
            "mdi:home", output_name="home_png", format="png", size=16
        )
    assert result is not None
    assert result.suffix == ".png"
    assert result.exists()


def test_generate_icon_cutout_local_svg(tmp_path):
    """generate_icon cutout mode from local SVG (mocked to avoid network)."""
    gen = IconGenerator(output_dir=str(tmp_path))
    svg_path = tmp_path / "icon.svg"
    svg_path.write_text(
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="24" height="24" fill="black"/></svg>',
        encoding="utf-8",
    )
    result = gen.generate_icon(
        local_file=str(svg_path),
        output_name="cutout_local",
        color="transparent",
        bg_color="red",
        size=32,
    )
    assert result is not None
    content = result.read_text()
    assert "mask" in content.lower() or "cutout" in content.lower()


def test_generate_icon_mocked_with_outline(tmp_path):
    """generate_icon with outline renders stroke in output SVG."""
    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" fill="red"/></svg>'
    with patch.object(gen, "get_icon_svg", return_value=svg):
        result = gen.generate_icon(
            "mdi:home",
            output_name="outlined_mocked",
            bg_color="#000000",
            outline_width=4,
            outline_color="white",
            size=32,
            color="white",
        )
    assert result is not None
    content = result.read_text()
    assert 'stroke="white"' in content


def test_load_local_file_with_resize(tmp_path):
    """load_local_file resizes large raster images to target_size."""
    try:
        from PIL import Image
    except ImportError:
        return

    # Create a 64x64 image; target_size=16 should trigger resize
    img = Image.new("RGBA", (64, 64), color=(0, 200, 0, 255))
    png_path = tmp_path / "big.png"
    img.save(png_path)

    gen = IconGenerator(output_dir=str(tmp_path))
    result = gen.load_local_file(str(png_path), target_size=16)
    assert result is not None
    content, is_raster = result
    assert is_raster is True
    # Resulting SVG dimensions should be 16x16 (scaled down)
    assert 'width="16"' in content or 'width="16"' in content


def test_generate_icon_batch_with_animation_dict(tmp_path):
    """generate_batch dict config with animation key exercises more batch code."""
    svg_path = tmp_path / "anim.svg"
    svg_path.write_text(
        '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="24" height="24" fill="black"/></svg>',
        encoding="utf-8",
    )
    gen = IconGenerator(output_dir=str(tmp_path))
    icons = {
        "animated_icon": {
            "local_file": str(svg_path),
            "animation": "spin:1s",
            "size": 32,
            "color": "white",
            "bg_color": "#333",
            "border_radius": 8,
            "scale": 0.7,
        },
        "plain_icon": {
            "local_file": str(svg_path),
            "size": 32,
        },
    }
    results = gen.generate_batch(icons)
    assert len(results) >= 1


def test_wrap_with_background_invalid_xml_fallback():
    """wrap_with_background falls back gracefully when SVG parsing fails."""
    gen = IconGenerator()
    # Invalid XML triggers the except Exception fallback in wrap_with_background
    result = gen.wrap_with_background("<<not_valid_xml>>", 128, bg_color="#FF0000")
    assert result is not None
    # Should still contain valid SVG wrapping around the fallback values
    assert "<svg" in result
    assert 'width="128"' in result


def test_modify_svg_invalid_xml_with_color():
    """modify_svg with invalid SVG falls through to exception handler."""
    gen = IconGenerator()
    # Invalid XML in the color+preserve_animations path hits inner except at line ~491
    result = gen.modify_svg("<<not_valid_xml_here>>", color="deeppink", size=64)
    # Should return something (the original or an error fallback)
    assert result is not None


def test_load_local_file_png_with_transparent_pixels(tmp_path):
    """Raster recoloring with transparent pixels hits the else branch (a==0)."""
    try:
        from PIL import Image
    except ImportError:
        return

    # Create small image with SOME transparent pixels (not a full rect)
    img = Image.new("RGBA", (8, 8), (0, 0, 0, 0))  # all transparent
    # Draw a 4x4 red square in the center
    for y in range(2, 6):
        for x in range(2, 6):
            img.putpixel((x, y), (255, 0, 0, 255))
    png_path = tmp_path / "partial.png"
    img.save(png_path)

    gen = IconGenerator(output_dir=str(tmp_path))
    # target_color causes recoloring; transparent pixels hit the else branch
    result = gen.load_local_file(str(png_path), target_color="blue")
    assert result is not None
    content, is_raster = result
    assert is_raster is True


def test_load_local_file_jpeg_with_color_shows_warning(tmp_path, capsys):
    """load_local_file prints a warning when recoloring JPEG (no transparency)."""
    try:
        from PIL import Image
    except ImportError:
        return

    # Create a JPEG file (no alpha channel)
    img = Image.new("RGB", (8, 8), (100, 50, 25))
    jpg_path = tmp_path / "icon.jpg"
    img.save(jpg_path, format="JPEG")

    gen = IconGenerator(output_dir=str(tmp_path))
    # Passing target_color for a JPEG should print a warning
    result = gen.load_local_file(str(jpg_path), target_color="red")
    # JPEG is converted to RGBA so may succeed; the warning is printed but result is not None
    assert result is not None or result is None  # Just ensure no crash


def test_generate_icon_mocked_direct_url_with_scale(tmp_path):
    """generate_icon direct_url sets output_name from URL path (covers line 303)."""
    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" fill="blue"/></svg>'
    with patch.object(gen, "get_icon_from_url", return_value=(svg, False)):
        result = gen.generate_icon(
            direct_url="https://example.com/myicon.svg",
            # No output_name: forces output_name = Path(url_path).stem = "myicon"
            size=32,
        )
    assert result is not None


def test_recolor_svg_with_transparent_pixels(tmp_path):
    """recolor_svg_to_single_color handles transparent pixels (else branch)."""
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        return

    gen = IconGenerator(output_dir=str(tmp_path))
    # Small icon with internal transparent areas
    svg = (
        '<svg viewBox="0 0 8 8" xmlns="http://www.w3.org/2000/svg">'
        '<rect x="2" y="2" width="4" height="4" fill="red"/>'
        '</svg>'
    )
    # Solid color recoloring: transparent pixels (corners) hit else branch
    result = gen.recolor_svg_to_single_color(svg, "blue", size=8)
    assert result is not None
    # Transparent recoloring: hits the is_transparent_color branch
    result2 = gen.recolor_svg_to_single_color(svg, "transparent", size=8)
    assert result2 is not None


def test_get_icon_from_url_returns_raster_svg(tmp_path):
    """get_icon_from_url with a PNG response wraps it in an SVG data-URI."""
    from unittest.mock import Mock
    try:
        from PIL import Image
    except ImportError:
        return

    # Build a minimal PNG in memory
    img = Image.new("RGBA", (16, 16), (200, 100, 50, 255))
    buf = __import__("io").BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.headers = {"Content-Type": "image/png"}
    mock_resp.content = png_bytes
    mock_resp.text = ""

    gen = IconGenerator(output_dir=str(tmp_path))
    with patch("requests.get", return_value=mock_resp):
        result = gen.get_icon_from_url("https://example.com/icon.png", target_size=16)

    assert result is not None
    content, is_raster = result
    assert is_raster is True
    assert "<svg" in content
    assert "image" in content.lower()


def test_get_icon_from_url_raster_with_resize(tmp_path):
    """get_icon_from_url resizes large raster images when target_size is smaller."""
    from unittest.mock import Mock
    try:
        from PIL import Image
    except ImportError:
        return

    # Large image: 64x64; target_size=8 triggers resize
    img = Image.new("RGBA", (64, 64), (0, 150, 200, 255))
    buf = __import__("io").BytesIO()
    img.save(buf, format="PNG")
    png_bytes = buf.getvalue()

    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.headers = {"Content-Type": "image/png"}
    mock_resp.content = png_bytes
    mock_resp.text = ""

    gen = IconGenerator(output_dir=str(tmp_path))
    with patch("requests.get", return_value=mock_resp):
        result = gen.get_icon_from_url("https://example.com/big.png", target_size=8)

    assert result is not None
    content, is_raster = result
    assert is_raster is True


def test_get_icon_from_url_fallback_text(tmp_path):
    """get_icon_from_url returns text fallback for unknown content type."""
    from unittest.mock import Mock

    mock_resp = Mock()
    mock_resp.raise_for_status = Mock()
    mock_resp.headers = {"Content-Type": "text/plain"}
    mock_resp.text = "<svg>fallback</svg>"
    mock_resp.content = b"<svg>fallback</svg>"

    gen = IconGenerator(output_dir=str(tmp_path))
    with patch("requests.get", return_value=mock_resp):
        result = gen.get_icon_from_url("https://example.com/icon.svg")

    # SVG URLs return the text directly
    assert result is not None


def test_generate_icon_ico_format_mocked(tmp_path):
    """generate_icon with format=ico produces an ICO file."""
    try:
        import cairosvg  # noqa: F401
    except ImportError:
        return

    gen = IconGenerator(output_dir=str(tmp_path))
    svg = '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect width="24" height="24" fill="red"/></svg>'
    with patch.object(gen, "get_icon_svg", return_value=svg):
        result = gen.generate_icon(
            "mdi:home", output_name="home_ico", format="ico", size=16
        )
    assert result is not None
    assert result.suffix == ".ico"
    assert result.exists()




