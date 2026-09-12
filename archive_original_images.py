from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "assets" / "img"
BACKUP_DIR = ROOT / "archived-original-jpgs"

EXTENSIONS = {".jpg", ".jpeg"}
SOURCE_EXTENSIONS = {".html", ".css", ".scss", ".js"}
IMAGE_REFERENCE = re.compile(r"(?P<path>[^\"'\s)]+\.(?:jpg|jpeg))", re.IGNORECASE)


def referenced_jpgs():
    references = set()
    for source_path in ROOT.rglob("*"):
        if not source_path.is_file() or source_path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        text = source_path.read_text(encoding="utf-8", errors="ignore")
        for match in IMAGE_REFERENCE.finditer(text):
            reference = match.group("path").replace("\\", "/")
            if reference.startswith(("http://", "https://", "data:")):
                continue
            references.add(Path(reference).name.lower())
    return references


used_jpgs = referenced_jpgs()

moved = 0
skipped = 0

for image_path in IMAGE_DIR.rglob("*"):
    if not image_path.is_file():
        continue

    if image_path.suffix.lower() not in EXTENSIONS:
        continue

    if image_path.name.lower() in used_jpgs:
        print(f"KEPT - still referenced: {image_path.relative_to(IMAGE_DIR)}")
        skipped += 1
        continue

    webp_path = image_path.with_suffix(".webp")

    if not webp_path.exists():
        skipped += 1
        continue

    relative_path = image_path.relative_to(IMAGE_DIR)
    backup_path = BACKUP_DIR / relative_path

    # Never overwrite an existing backup.
    if backup_path.exists():
        print(f"SKIPPED - backup already exists: {backup_path}")
        skipped += 1
        continue

    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(image_path), str(backup_path))

    print(f"MOVED: {relative_path}")
    moved += 1

print(f"\nMoved: {moved}")
print(f"Skipped: {skipped}")
print(f"Archive: {BACKUP_DIR}")