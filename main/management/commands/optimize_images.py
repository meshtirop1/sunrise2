"""Shrink oversized images under MEDIA_ROOT in place.

- Never makes a file bigger: the re-encode is kept only when smaller.
- Photographic PNGs (no transparency) are converted to JPEG and every
  ImageField in the database that pointed at the old file is updated.
- Idempotent; run by deploy.sh so admin uploads get optimized too.
"""
import io
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from PIL import Image

MAX_WIDTH = 1400
MAX_BYTES = 400 * 1024
JPEG_QUALITY = 82


def image_fields():
    from main.models import GalleryCategory, GalleryItem, Service, TeamMember
    return [(Service, 'image'), (GalleryCategory, 'image'),
            (GalleryItem, 'image'), (TeamMember, 'photo')]


class Command(BaseCommand):
    help = "Resize/recompress oversized images under MEDIA_ROOT; convert photo-PNGs to JPEG."

    def add_arguments(self, parser):
        parser.add_argument('--path', default=None)
        parser.add_argument('--no-db', action='store_true',
                            help="Directory is not MEDIA_ROOT: skip PNG->JPEG conversion")

    def handle(self, *args, **options):
        root = Path(options['path'] or settings.MEDIA_ROOT)
        if not root.exists():
            self.stdout.write(f"{root} does not exist - nothing to do")
            return
        saved = count = 0
        for path in sorted(root.rglob('*')):
            suffix = path.suffix.lower()
            if suffix not in ('.jpg', '.jpeg', '.png', '.webp'):
                continue
            size = path.stat().st_size
            if size <= MAX_BYTES:
                continue
            try:
                img = Image.open(path)
                img.load()
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(f"skip {path.name}: {exc}")
                continue
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)

            has_alpha = img.mode in ('RGBA', 'LA', 'P') and 'transparency' in img.info or img.mode == 'RGBA'
            to_jpeg = (suffix == '.png' and not has_alpha and not options['no_db'])

            buf = io.BytesIO()
            if suffix in ('.jpg', '.jpeg') or to_jpeg:
                img.convert('RGB').save(buf, 'JPEG', quality=JPEG_QUALITY,
                                        optimize=True, progressive=True)
            elif suffix == '.png':
                img.save(buf, 'PNG', optimize=True)
            else:
                img.save(buf, 'WEBP', quality=JPEG_QUALITY)
            data = buf.getvalue()
            if len(data) >= size:
                continue  # never regress

            if to_jpeg:
                new_path = path.with_suffix('.jpg')
                new_path.write_bytes(data)
                old_rel = str(path.relative_to(root)).replace('\\', '/')
                new_rel = str(new_path.relative_to(root)).replace('\\', '/')
                changed = 0
                for model, field in image_fields():
                    changed += model.objects.filter(**{field: old_rel}).update(**{field: new_rel})
                path.unlink()
                self.stdout.write(f"{old_rel} -> {new_rel}: {size//1024}KB -> "
                                  f"{len(data)//1024}KB ({changed} db ref(s) updated)")
            else:
                path.write_bytes(data)
                self.stdout.write(f"{path.relative_to(root)}: {size//1024}KB -> {len(data)//1024}KB")
            saved += size - len(data)
            count += 1
        self.stdout.write(self.style.SUCCESS(
            f"Optimized {count} image(s), saved {saved//1024}KB"))
