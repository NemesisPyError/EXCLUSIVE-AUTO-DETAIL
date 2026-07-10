from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.tipo_vehiculo import TipoVehiculo
from models.segmento import Segmento
from models.categoria_servicio import CategoriaServicio
from models.nivel_suciedad import NivelSuciedad
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache
import re


def _make_slug(nombre):
    return re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')


# =============================================================
# TIPOS DE VEHICULO
# =============================================================
@admin_bp.route('/tipos-vehiculo')
@login_required
@role_required('admin')
def listar_tipos_vehiculo():
    items = TipoVehiculo.query.order_by(TipoVehiculo.orden).all()
    return render_template('admin/tipos_vehiculo.html', items=items)


@admin_bp.route('/tipos-vehiculo/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_tipo_vehiculo():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_tipos_vehiculo'))
    slug = _make_slug(nombre)
    if TipoVehiculo.query.filter_by(slug=slug).first():
        flash('Ya existe un tipo con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_tipos_vehiculo'))
    item = TipoVehiculo(
        nombre=nombre, slug=slug,
        descripcion=(request.form.get('descripcion') or '').strip() or None,
        icono=(request.form.get('icono') or '').strip() or None,
        orden=int(request.form.get('orden', 0)),
    )
    db.session.add(item)
    db.session.commit()
    _invalidar_cache()
    flash(f'Tipo "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_tipos_vehiculo'))


@admin_bp.route('/tipos-vehiculo/<int:item_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_tipo_vehiculo(item_id):
    item = TipoVehiculo.query.get_or_404(item_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_tipos_vehiculo'))
    slug = _make_slug(nombre)
    existente = TipoVehiculo.query.filter(TipoVehiculo.slug == slug, TipoVehiculo.id != item_id).first()
    if existente:
        flash('Ya existe otro tipo con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_tipos_vehiculo'))
    item.nombre = nombre
    item.slug = slug
    item.descripcion = (request.form.get('descripcion') or '').strip() or None
    item.icono = (request.form.get('icono') or '').strip() or None
    item.orden = int(request.form.get('orden', item.orden))
    db.session.commit()
    _invalidar_cache()
    flash(f'Tipo "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_tipos_vehiculo'))


# =============================================================
# SEGMENTOS
# =============================================================
@admin_bp.route('/segmentos')
@login_required
@role_required('admin')
def listar_segmentos():
    items = Segmento.query.order_by(Segmento.orden).all()
    return render_template('admin/segmentos.html', items=items)


@admin_bp.route('/segmentos/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_segmento():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_segmentos'))
    slug = _make_slug(nombre)
    if Segmento.query.filter_by(slug=slug).first():
        flash('Ya existe un segmento con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_segmentos'))
    item = Segmento(
        nombre=nombre, slug=slug,
        descripcion=(request.form.get('descripcion') or '').strip() or None,
        orden=int(request.form.get('orden', 0)),
    )
    db.session.add(item)
    db.session.commit()
    _invalidar_cache()
    flash(f'Segmento "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_segmentos'))


@admin_bp.route('/segmentos/<int:item_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_segmento(item_id):
    item = Segmento.query.get_or_404(item_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_segmentos'))
    slug = _make_slug(nombre)
    existente = Segmento.query.filter(Segmento.slug == slug, Segmento.id != item_id).first()
    if existente:
        flash('Ya existe otro segmento con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_segmentos'))
    item.nombre = nombre
    item.slug = slug
    item.descripcion = (request.form.get('descripcion') or '').strip() or None
    item.orden = int(request.form.get('orden', item.orden))
    db.session.commit()
    _invalidar_cache()
    flash(f'Segmento "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_segmentos'))


# =============================================================
# CATEGORIAS DE SERVICIO
# =============================================================
@admin_bp.route('/categorias-servicio')
@login_required
@role_required('admin')
def listar_categorias_servicio():
    items = CategoriaServicio.query.order_by(CategoriaServicio.orden).all()
    return render_template('admin/categorias_servicio.html', items=items)


@admin_bp.route('/categorias-servicio/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_categoria_servicio():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_categorias_servicio'))
    slug = _make_slug(nombre)
    if CategoriaServicio.query.filter_by(slug=slug).first():
        flash('Ya existe una categoria con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_categorias_servicio'))
    item = CategoriaServicio(
        nombre=nombre, slug=slug,
        orden=int(request.form.get('orden', 0)),
    )
    db.session.add(item)
    db.session.commit()
    _invalidar_cache()
    flash(f'Categoria "{nombre}" creada.', 'success')
    return redirect(url_for('admin.listar_categorias_servicio'))


@admin_bp.route('/categorias-servicio/<int:item_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_categoria_servicio(item_id):
    item = CategoriaServicio.query.get_or_404(item_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_categorias_servicio'))
    slug = _make_slug(nombre)
    existente = CategoriaServicio.query.filter(
        CategoriaServicio.slug == slug, CategoriaServicio.id != item_id
    ).first()
    if existente:
        flash('Ya existe otra categoria con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_categorias_servicio'))
    item.nombre = nombre
    item.slug = slug
    item.orden = int(request.form.get('orden', item.orden))
    db.session.commit()
    _invalidar_cache()
    flash(f'Categoria "{nombre}" actualizada.', 'success')
    return redirect(url_for('admin.listar_categorias_servicio'))


# =============================================================
# NIVELES DE SUCIEDAD
# =============================================================
@admin_bp.route('/niveles-suciedad')
@login_required
@role_required('admin')
def listar_niveles_suciedad():
    items = NivelSuciedad.query.order_by(NivelSuciedad.orden).all()
    return render_template('admin/niveles_suciedad.html', items=items)


@admin_bp.route('/niveles-suciedad/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_nivel_suciedad():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_niveles_suciedad'))
    if NivelSuciedad.query.filter_by(nombre=nombre).first():
        flash('Ya existe un nivel con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_niveles_suciedad'))
    item = NivelSuciedad(
        nombre=nombre,
        descripcion=(request.form.get('descripcion') or '').strip() or None,
        orden=int(request.form.get('orden', 0)),
    )
    db.session.add(item)
    db.session.commit()
    _invalidar_cache()
    flash(f'Nivel "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_niveles_suciedad'))


@admin_bp.route('/niveles-suciedad/<int:item_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_nivel_suciedad(item_id):
    item = NivelSuciedad.query.get_or_404(item_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_niveles_suciedad'))
    existente = NivelSuciedad.query.filter(
        NivelSuciedad.nombre == nombre, NivelSuciedad.id != item_id
    ).first()
    if existente:
        flash('Ya existe otro nivel con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_niveles_suciedad'))
    item.nombre = nombre
    item.descripcion = (request.form.get('descripcion') or '').strip() or None
    item.orden = int(request.form.get('orden', item.orden))
    db.session.commit()
    _invalidar_cache()
    flash(f'Nivel "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_niveles_suciedad'))
