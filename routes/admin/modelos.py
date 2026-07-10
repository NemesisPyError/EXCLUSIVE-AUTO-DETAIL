from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from decorators import role_required
from models.modelo_vehiculo import ModeloVehiculo
from models.marca import Marca
from models.tipo_vehiculo import TipoVehiculo
from models.segmento import Segmento
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache
import re


@admin_bp.route('/modelos')
@login_required
@role_required('admin')
def listar_modelos():
    buscar = request.args.get('buscar', '').strip()
    marca_id = request.args.get('marca_id', type=int)
    tipo_id = request.args.get('tipo_vehiculo_id', type=int)
    page = request.args.get('page', 1, type=int)

    from sqlalchemy.orm import joinedload
    query = ModeloVehiculo.query.options(
        joinedload(ModeloVehiculo.marca),
        joinedload(ModeloVehiculo.tipo_vehiculo),
        joinedload(ModeloVehiculo.segmento),
    )

    if buscar:
        query = query.filter(ModeloVehiculo.nombre.ilike(f'%{buscar}%'))
    if marca_id:
        query = query.filter(ModeloVehiculo.marca_id == marca_id)
    if tipo_id:
        query = query.filter(ModeloVehiculo.tipo_vehiculo_id == tipo_id)

    query = query.order_by(ModeloVehiculo.marca_id, ModeloVehiculo.nombre)
    paginacion = query.paginate(page=page, per_page=25, error_out=False)

    marcas = Marca.query.filter_by(activo=True).order_by(Marca.nombre).all()
    tipos = TipoVehiculo.query.order_by(TipoVehiculo.orden).all()
    segmentos = Segmento.query.order_by(Segmento.orden).all()

    return render_template(
        'admin/modelos.html',
        modelos=paginacion.items,
        paginacion=paginacion,
        buscar=buscar,
        marca_id=marca_id,
        tipo_id=tipo_id,
        marcas=marcas,
        tipos=tipos,
        segmentos=segmentos,
    )


@admin_bp.route('/modelos/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_modelo():
    nombre = (request.form.get('nombre') or '').strip()
    marca_id = request.form.get('marca_id', type=int)
    tipo_id = request.form.get('tipo_vehiculo_id', type=int)
    segmento_id = request.form.get('segmento_id', type=int)
    anio_desde = request.form.get('anio_desde', type=int)
    anio_hasta = request.form.get('anio_hasta', type=int)

    errores = []
    if not nombre:
        errores.append('El nombre del modelo es obligatorio.')
    if not marca_id:
        errores.append('La marca es obligatoria.')
    if not tipo_id:
        errores.append('El tipo de vehiculo es obligatorio.')
    if not segmento_id:
        errores.append('El segmento es obligatorio.')

    if errores:
        for e in errores:
            flash(e, 'danger')
        return redirect(url_for('admin.listar_modelos'))

    slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')
    if ModeloVehiculo.query.filter_by(marca_id=marca_id, slug=slug).first():
        flash('Ya existe un modelo con ese nombre para esa marca.', 'danger')
        return redirect(url_for('admin.listar_modelos'))

    modelo = ModeloVehiculo(
        marca_id=marca_id,
        nombre=nombre,
        slug=slug,
        tipo_vehiculo_id=tipo_id,
        segmento_id=segmento_id,
        anio_desde=anio_desde or None,
        anio_hasta=anio_hasta or None,
        activo=True,
    )
    db.session.add(modelo)
    db.session.commit()
    _invalidar_cache()
    flash(f'Modelo "{nombre}" creado.', 'success')
    return redirect(url_for('admin.listar_modelos'))


@admin_bp.route('/modelos/<int:modelo_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_modelo(modelo_id):
    modelo = ModeloVehiculo.query.get_or_404(modelo_id)
    nombre = (request.form.get('nombre') or '').strip()

    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_modelos'))

    slug = re.sub(r'[^a-z0-9]+', '-', nombre.lower()).strip('-')
    existente = ModeloVehiculo.query.filter(
        ModeloVehiculo.marca_id == modelo.marca_id,
        ModeloVehiculo.slug == slug,
        ModeloVehiculo.id != modelo_id,
    ).first()
    if existente:
        flash('Ya existe otro modelo con ese nombre para esa marca.', 'danger')
        return redirect(url_for('admin.listar_modelos'))

    modelo.nombre = nombre
    modelo.slug = slug
    modelo.marca_id = request.form.get('marca_id', type=int) or modelo.marca_id
    modelo.tipo_vehiculo_id = request.form.get('tipo_vehiculo_id', type=int) or modelo.tipo_vehiculo_id
    modelo.segmento_id = request.form.get('segmento_id', type=int) or modelo.segmento_id
    modelo.anio_desde = request.form.get('anio_desde', type=int) or None
    modelo.anio_hasta = request.form.get('anio_hasta', type=int) or None
    modelo.activo = request.form.get('activo', '1') == '1'
    db.session.commit()
    _invalidar_cache()
    flash(f'Modelo "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_modelos'))


@admin_bp.route('/modelos/<int:modelo_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_modelo(modelo_id):
    modelo = ModeloVehiculo.query.get_or_404(modelo_id)
    modelo.activo = not modelo.activo
    db.session.commit()
    _invalidar_cache()
    estado = 'activado' if modelo.activo else 'desactivado'
    return jsonify({'success': True, 'activo': modelo.activo, 'mensaje': f'Modelo {estado}.'})
