from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.marca import Marca
from models.modelo_vehiculo import ModeloVehiculo
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache
import re


@admin_bp.route('/marcas')
@login_required
@role_required('admin')
def listar_marcas():
    buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Marca.query
    if buscar:
        query = query.filter(Marca.nombre.ilike(f'%{buscar}%'))

    query = query.order_by(Marca.nombre)
    paginacion = query.paginate(page=page, per_page=25, error_out=False)

    from sqlalchemy.orm import joinedload
    items = Marca.query.options(
        joinedload(Marca.modelos)
    ).filter(
        Marca.id.in_([m.id for m in paginacion.items])
    ).order_by(Marca.nombre).all()

    marca_dict = {m.id: m for m in items}

    return render_template(
        'admin/marcas.html',
        marcas=paginacion.items,
        paginacion=paginacion,
        buscar=buscar,
        marca_dict=marca_dict,
    )


@admin_bp.route('/marcas/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_marca():
    nombre = (request.form.get('nombre') or '').strip()
    pais = (request.form.get('pais_origen') or '').strip()

    if not nombre:
        flash('El nombre de la marca es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_marcas'))

    slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')
    if Marca.query.filter_by(slug=slug).first():
        flash('Ya existe una marca con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_marcas'))

    marca = Marca(
        nombre=nombre,
        slug=slug,
        pais_origen=pais or None,
        activo=True,
    )
    db.session.add(marca)
    db.session.commit()
    _invalidar_cache()
    flash(f'Marca "{nombre}" creada correctamente.', 'success')
    return redirect(url_for('admin.listar_marcas'))


@admin_bp.route('/marcas/<int:marca_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_marca(marca_id):
    marca = Marca.query.get_or_404(marca_id)
    nombre = (request.form.get('nombre') or '').strip()

    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_marcas'))

    nuevo_slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')
    existente = Marca.query.filter(Marca.slug == nuevo_slug, Marca.id != marca_id).first()
    if existente:
        flash('Ya existe otra marca con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_marcas'))

    marca.nombre = nombre
    marca.slug = nuevo_slug
    marca.pais_origen = (request.form.get('pais_origen') or '').strip() or None
    marca.activo = request.form.get('activo', '1') == '1'
    db.session.commit()
    _invalidar_cache()
    flash(f'Marca "{nombre}" actualizada.', 'success')
    return redirect(url_for('admin.listar_marcas'))


@admin_bp.route('/marcas/<int:marca_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_marca(marca_id):
    marca = Marca.query.get_or_404(marca_id)
    marca.activo = not marca.activo
    db.session.commit()
    _invalidar_cache()
    estado = 'activada' if marca.activo else 'desactivada'
    return jsonify({'success': True, 'activo': marca.activo, 'mensaje': f'Marca {estado}.'})
