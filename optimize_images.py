from pathlib import Path
from PIL import Image, ImageOps

IMAGE_DIR = Path("assets/img")
WEBP_QUALITY = 82
SKIP_FILES = {"SavardLogo.png", "favicon.png", "apple-touch-icon.png"}

extensions = {".jpg", ".jpeg", ".png"}

for image_path in IMAGE_DIR.rglob("*"):
    if "icons" in image_path.parts:
      continue
    if image_path.suffix.lower() not in extensions or image_path.name in SKIP_FILES:
        continue

    # Do not overwrite an existing WebP
    output_path = image_path.with_suffix(".webp")

    if output_path.exists():
        print(f"SKIPPED (already exists): {output_path}")
        continue

    try:
        with Image.open(image_path) as original:
            # Correct phone-photo rotation using EXIF data
            img = ImageOps.exif_transpose(original)

            # Preserve transparency where applicable
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert(
                    "RGBA" if "transparency" in img.info else "RGB"
                )

            img.save(
                output_path,
                "WEBP",
                quality=WEBP_QUALITY,
                method=6
            )

            old_kb = image_path.stat().st_size / 1024
            new_kb = output_path.stat().st_size / 1024

            print(
                f"{image_path.name}: "
                f"{old_kb:.0f} KB -> {new_kb:.0f} KB"
            )

    except Exception as e:
        print(f"ERROR: {image_path}: {e}")