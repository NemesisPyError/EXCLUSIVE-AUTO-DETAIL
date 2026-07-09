from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.servicio import Servicio
from models.categoria_servicio import CategoriaServicio
from models.paquete_servicio import PaqueteServicio
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache
import re


@admin_bp.route('/paquetes')
@login_required
@role_required('admin')
def listar_paquetes():
    from sqlalchemy.orm import joinedload
    paquetes = Servicio.query.options(
        joinedload(Servicio.categoria)
    ).filter_by(
        tipo='paquete', deleted_at=None
    ).order_by(Servicio.nombre).all()

    servicios_base = Servicio.query.filter_by(
        tipo='base', activo=True, deleted_at=None
    ).order_by(Servicio.nombre).all()

    composiciones = {}
    for pkg in paquetes:
        comps = db.session.query(PaqueteServicio).filter_by(paquete_id=pkg.id).order_by(PaqueteServicio.orden).all()
        composiciones[pkg.id] = comps

    categorias = CategoriaServicio.query.order_by(CategoriaServicio.orden).all()

    return render_template(
        'admin/paquetes.html',
        paquetes=paquetes,
        servicios_base=servicios_base,
        composiciones=composiciones,
        categorias=categorias,
    )


@admin_bp.route('/paquetes/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_paquete():
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre del paquete es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_paquetes'))

    slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')
    if Servicio.query.filter_by(slug=slug).first():
        flash('Ya existe un servicio con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_paquetes'))

    cat_id = request.form.get('categoria_servicio_id', type=int)
    servicio_principal_id = request.form.get('servicio_principal_id', type=int)
    componentes = request.form.getlist('servicios_ids')

    if not servicio_principal_id:
        flash('Debe seleccionar un servicio principal.', 'danger')
        return redirect(url_for('admin.listar_paquetes'))

    pkg = Servicio(
        nombre=nombre,
        slug=slug,
        descripcion=(request.form.get('descripcion') or '').strip() or None,
        tipo='paquete',
        categoria_servicio_id=cat_id or 6,
        requiere_varios_dias=request.form.get('requiere_varios_dias') == '1',
        dias_bloqueo=request.form.get('dias_bloqueo', type=int) or None,
        activo=True,
    )
    db.session.add(pkg)
    db.session.flush()

    orden = 0
    for svc_id in componentes:
        svc_id = int(svc_id)
        orden += 1
        db.session.add(PaqueteServicio(
            paquete_id=pkg.id,
            servicio_id=svc_id,
            es_principal=(svc_id == servicio_principal_id),
            orden=orden,
        ))

    if not any(svc_id == servicio_principal_id for svc_id in [int(x) for x in componentes]):
        orden += 1
        db.session.add(PaqueteServicio(
            paquete_id=pkg.id,
            servicio_id=servicio_principal_id,
            es_principal=True,
            orden=orden,
        ))

    db.session.commit()
    _invalidar_cache()
    flash(f'Paquete "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_paquetes'))


@admin_bp.route('/paquetes/<int:pkg_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_paquete(pkg_id):
    pkg = Servicio.query.get_or_404(pkg_id)
    nombre = (request.form.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_paquetes'))

    slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')
    existente = Servicio.query.filter(Servicio.slug == slug, Servicio.id != pkg_id).first()
    if existente:
        flash('Ya existe otro servicio con ese nombre.', 'danger')
        return redirect(url_for('admin.listar_paquetes'))

    pkg.nombre = nombre
    pkg.slug = slug
    pkg.descripcion = (request.form.get('descripcion') or '').strip() or None
    pkg.categoria_servicio_id = request.form.get('categoria_servicio_id', type=int) or pkg.categoria_servicio_id
    pkg.requiere_varios_dias = request.form.get('requiere_varios_dias') == '1'
    pkg.dias_bloqueo = request.form.get('dias_bloqueo', type=int) or None
    pkg.activo = request.form.get('activo', '1') == '1'

    servicio_principal_id = request.form.get('servicio_principal_id', type=int)
    componentes = request.form.getlist('servicios_ids')

    if servicio_principal_id:
        db.session.query(PaqueteServicio).filter_by(paquete_id=pkg.id).delete()
        orden = 0
        for svc_id in componentes:
            svc_id = int(svc_id)
            orden += 1
            db.session.add(PaqueteServicio(
                paquete_id=pkg.id,
                servicio_id=svc_id,
                es_principal=(svc_id == servicio_principal_id),
                orden=orden,
            ))

    db.session.commit()
    _invalidar_cache()
    flash(f'Paquete "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_paquetes'))
