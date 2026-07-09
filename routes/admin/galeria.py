from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from extensions import db, limiter
from decorators import role_required
from models.galeria import Galeria
from models.galeria_categoria import GaleriaCategoria
from services.security_service import log_error
from services.image_service import is_allowed as _galeria_allowed
from services.image_service import save_image as _galeria_guardar
from services.image_service import delete_image as _galeria_borrar
from routes.admin import admin_bp


@admin_bp.route('/galeria')
@login_required
@role_required('admin')
def listar_galeria():
    from collections import OrderedDict
    import json
    from sqlalchemy.orm import joinedload
    categorias = GaleriaCategoria.query.options(
        joinedload(GaleriaCategoria.imagenes)
    ).order_by(
        GaleriaCategoria.orden, GaleriaCategoria.id
    ).all()

    grupos = OrderedDict()
    for cat in categorias:
        grupos[cat] = sorted(cat.imagenes, key=lambda x: (x.orden, x.id))

    items = [i for imgs in grupos.values() for i in imgs]

    galeria_data = json.dumps([
        {
            'id': it.id,
            'categoria_id': it.categoria_id,
            'categoria_nombre': it.categoria.nombre if it.categoria else '',
            'titulo': it.titulo,
            'activo': it.activo,
            'activo': it.activo,
        }
        for it in items
    ], ensure_ascii=False)

    categorias_data = json.dumps([
        {
            'id': c.id,
            'nombre': c.nombre,
            'activo': c.activo,
        }
        for c in categorias
    ], ensure_ascii=False)

    return render_template(
        'admin/galeria.html',
        grupos=grupos,
        categorias=categorias,
        galeria_data=galeria_data,
        categorias_data=categorias_data,
    )


@admin_bp.route('/galeria/categorias/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_categoria_galeria():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre de la categoría es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    existe = GaleriaCategoria.query.filter(
        GaleriaCategoria.nombre.ilike(nombre)
    ).first()
    if existe:
        flash('Ya existe una categoría con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    orden = db.session.query(db.func.max(GaleriaCategoria.orden)).scalar() or 0
    cat = GaleriaCategoria(nombre=nombre, orden=orden + 1, activo=True)
    db.session.add(cat)
    db.session.commit()
    flash(f'Categoría "{nombre}" creada.', 'success')
    return redirect(url_for('admin.listar_galeria'))


@admin_bp.route('/galeria/categorias/<int:cat_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_categoria_galeria(cat_id):
    cat = GaleriaCategoria.query.get_or_404(cat_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre de la categoría es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    duplicada = GaleriaCategoria.query.filter(
        GaleriaCategoria.nombre.ilike(nombre),
        GaleriaCategoria.id != cat_id,
    ).first()
    if duplicada:
        flash('Ya existe otra categoría con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    viejo = cat.nombre
    cat.nombre = nombre
    cat.activo = request.form.get('activo', '1') == '1'
    # categoria renombrada: no requiere actualizar campo tipo (ya no existe)
    db.session.commit()
    flash(f'Categoría renombrada de "{viejo}" a "{nombre}".', 'success')
    return redirect(url_for('admin.listar_galeria'))


@admin_bp.route('/galeria/categorias/<int:cat_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
@limiter.limit("10 per minute")
def eliminar_categoria_galeria(cat_id):
    cat = GaleriaCategoria.query.get_or_404(cat_id)
    try:
        for img in list(cat.imagenes):
            _galeria_borrar(img.url_imagen)
        db.session.delete(cat)
        db.session.commit()
        flash(f'Categoria "{cat.nombre}" y sus imagenes eliminadas.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error('/admin/galeria/categoria/eliminar', str(e))
        flash('Error al eliminar la categoria.', 'danger')
    return redirect(url_for('admin.listar_galeria'))


@admin_bp.route('/galeria/categorias/reordenar', methods=['POST'])
@login_required
@role_required('admin')
def reordenar_categorias_galeria():
    data = request.get_json(silent=True) or {}
    ordenes = data.get('ordenes')
    if not isinstance(ordenes, list):
        return jsonify({'success': False, 'error': 'Formato inválido.'}), 400
    try:
        for entry in ordenes:
            cid = entry.get('id')
            orden = entry.get('orden')
            if cid is None or orden is None:
                continue
            cat = GaleriaCategoria.query.get(int(cid))
            if cat:
                cat.orden = int(orden)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        log_error('/admin/galeria/categorias/reordenar', str(e))
        return jsonify({'success': False, 'error': 'Error al reordenar categorias.'}), 500


@admin_bp.route('/galeria/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_galeria():
    data = request.form
    cat_id = (data.get('categoria_id') or '').strip()
    if not cat_id:
        flash('La categoría es obligatoria.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    cat = GaleriaCategoria.query.get(int(cat_id))
    if not cat:
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    archivos = request.files.getlist('imagenes')
    guardadas = 0
    orden_base = db.session.query(db.func.max(Galeria.orden)).filter_by(categoria_id=cat.id).scalar() or 0

    for archivo in archivos:
        if not archivo or not archivo.filename:
            continue
        if not _galeria_allowed(archivo.filename, archivo.content_type):
            continue
        try:
            url_main, url_thumb = _galeria_guardar(archivo)
        except (ValueError, Exception):
            continue
        orden_base += 1
        item = Galeria(
            titulo=(data.get('titulo') or '').strip() or cat.nombre,
            url_imagen=url_main,
            url_thumb=url_thumb,
            categoria_id=cat.id,
            activo=data.get('activo', '1') == '1',
            orden=orden_base,
        )
        db.session.add(item)
        guardadas += 1

    if guardadas == 0:
        flash('No se subió ninguna imagen válida (png, jpg, jpeg, webp, gif).', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    db.session.commit()
    flash(f'{guardadas} imagen(es) agregada(s) a "{cat.nombre}".', 'success')
    return redirect(url_for('admin.listar_galeria'))


@admin_bp.route('/galeria/<int:item_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_galeria(item_id):
    item = Galeria.query.get_or_404(item_id)
    data = request.form

    cat_id = (data.get('categoria_id') or '').strip()
    if not cat_id:
        flash('La categoría es obligatoria.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    cat = GaleriaCategoria.query.get(int(cat_id))
    if not cat:
        flash('La categoría seleccionada no existe.', 'danger')
        return redirect(url_for('admin.listar_galeria'))

    item.titulo = (data.get('titulo') or '').strip() or cat.nombre
    item.categoria_id = cat.id
    item.activo = data.get('activo', '1') == '1'

    archivo = request.files.get('imagen')
    if archivo and archivo.filename and _galeria_allowed(archivo.filename, archivo.content_type):
        try:
            _galeria_borrar(item.url_imagen)
            url_main, url_thumb = _galeria_guardar(archivo)
            item.url_imagen = url_main
            item.url_thumb = url_thumb
        except (ValueError, Exception):
            flash('La imagen subida es invalida o esta corrupta.', 'danger')
            return redirect(url_for('admin.listar_galeria'))

    db.session.commit()
    flash('Imagen actualizada correctamente.', 'success')
    return redirect(url_for('admin.listar_galeria'))


@admin_bp.route('/galeria/<int:item_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_galeria(item_id):
    item = Galeria.query.get_or_404(item_id)
    try:
        _galeria_borrar(item.url_imagen)
        db.session.delete(item)
        db.session.commit()
        flash('Imagen eliminada correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error('/admin/galeria/eliminar', str(e))
        flash('Error al eliminar la imagen.', 'danger')
    return redirect(url_for('admin.listar_galeria'))


@admin_bp.route('/galeria/reordenar', methods=['POST'])
@login_required
@role_required('admin')
def reordenar_galeria():
    data = request.get_json(silent=True) or {}
    ordenes = data.get('ordenes')
    if not isinstance(ordenes, list):
        return jsonify({'success': False, 'error': 'Formato inválido.'}), 400

    try:
        for entry in ordenes:
            gid = entry.get('id')
            orden = entry.get('orden')
            if gid is None or orden is None:
                continue
            item = Galeria.query.get(int(gid))
            if item:
                item.orden = int(orden)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        log_error('/admin/galeria/reordenar', str(e))
        return jsonify({'success': False, 'error': 'Error al reordenar imagenes.'}), 500
