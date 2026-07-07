"""Servicio de imágenes — validación, guardado y borrado de imágenes de galería."""
import os
import io
import uuid
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
ALLOWED_MIMES = {'image/png', 'image/jpeg', 'image/webp', 'image/gif'}


def is_allowed(filename, mimetype=None):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXT:
        return False
    if mimetype and mimetype not in ALLOWED_MIMES:
        return False
    return True


def save_image(file):
    try:
        from PIL import Image, UnidentifiedImageError
        file_bytes = file.read()
        file.seek(0)
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()
    except ImportError:
        pass
    except (UnidentifiedImageError, IOError, SyntaxError):
        raise ValueError('Archivo de imagen invalido o corrupto.')
    except Exception:
        raise ValueError('No se pudo verificar la imagen.')

    uid = uuid.uuid4().hex[:10]
    destino_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'galeria')
    os.makedirs(destino_dir, exist_ok=True)

    try:
        from PIL import Image
        pil_img = Image.open(io.BytesIO(file_bytes))
        if pil_img.mode in ('RGBA', 'P'):
            pil_img = pil_img.convert('RGBA')

        main = pil_img.copy()
        w_main, h_main = main.size
        if w_main > 1200:
            ratio = 1200 / w_main
            new_h = int(h_main * ratio)
            main = main.resize((1200, new_h), Image.Resampling.LANCZOS)

        main_rgb = main.convert('RGB') if main.mode == 'RGBA' else main
        nombre_main = secure_filename(f'galeria_{uid}.webp')
        main_rgb.save(os.path.join(destino_dir, nombre_main), 'WEBP', quality=85)

        thumb = pil_img.copy()
        w_thumb, h_thumb = thumb.size
        if w_thumb > 400:
            ratio = 400 / w_thumb
            new_h = int(h_thumb * ratio)
            thumb = thumb.resize((400, new_h), Image.Resampling.LANCZOS)

        thumb_rgb = thumb.convert('RGB') if thumb.mode == 'RGBA' else thumb
        nombre_thumb = secure_filename(f'galeria_{uid}_thumb.webp')
        thumb_rgb.save(os.path.join(destino_dir, nombre_thumb), 'WEBP', quality=85)

        return (
            f'/static/img/galeria/{nombre_main}',
            f'/static/img/galeria/{nombre_thumb}',
        )
    except (ImportError, UnidentifiedImageError):
        raise ValueError('No se pudo procesar la imagen.')
    except Exception:
        raise ValueError('Error al procesar la imagen.')


def delete_image(url_imagen):
    try:
        if not url_imagen or not url_imagen.startswith('/static/img/'):
            return
        rel = url_imagen.replace('/static/img/', '')
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], rel)
        if os.path.exists(ruta):
            os.remove(ruta)
        base, ext = os.path.splitext(rel)
        thumb_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], f'{base}_thumb{ext}'
        )
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
    except Exception:
        pass
