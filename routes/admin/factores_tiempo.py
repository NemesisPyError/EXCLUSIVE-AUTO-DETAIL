from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from decorators import role_required
from models.factor_tiempo import FactorTiempo, TipoFactor, ReservaFactorTiempo
from services.security_service import log_error
from routes.admin import admin_bp, _invalidar_cache


@admin_bp.route('/factores-tiempo')
@login_required
@role_required('admin')
def listar_factores_tiempo():
    factores = FactorTiempo.query.order_by(
        FactorTiempo.tipo, FactorTiempo.orden, FactorTiempo.nombre
    ).all()

    agrupados = {}
    for f in factores:
        if f.tipo not in agrupados:
            agrupados[f.tipo] = []
        agrupados[f.tipo].append(f)

    tipos = [t.value for t in TipoFactor]
    return render_template(
        'admin/factores_tiempo.html',
        agrupados=agrupados,
        tipos=tipos,
        tipos_labels={
            'suciedad': 'Nivel de Suciedad',
            'condicion': 'Condiciones',
            'generico': 'Genéricos',
        },
    )


@admin_bp.route('/factores-tiempo/crear', methods=['POST'])
@login_required
@role_required('admin')
def crear_factor_tiempo():
    data = request.form
    tipo = (data.get('tipo') or '').strip()
    nombre = (data.get('nombre') or '').strip()
    if not tipo or not nombre:
        flash('Tipo y nombre son obligatorios.', 'danger')
        return redirect(url_for('admin.listar_factores_tiempo'))

    orden = db.session.query(
        db.func.max(FactorTiempo.orden)
    ).filter_by(tipo=tipo).scalar() or 0

    factor = FactorTiempo(
        tipo=tipo,
        nombre=nombre,
        minutos_adicionales=int(data.get('minutos_adicionales') or 0),
        activo=data.get('activo', '1') == '1',
        orden=orden + 1,
    )
    db.session.add(factor)
    db.session.commit()
    _invalidar_cache()
    flash(f'Factor "{nombre}" creado correctamente.', 'success')
    return redirect(url_for('admin.listar_factores_tiempo'))


@admin_bp.route('/factores-tiempo/<int:factor_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_factor_tiempo(factor_id):
    factor = FactorTiempo.query.get_or_404(factor_id)
    data = request.form

    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return redirect(url_for('admin.listar_factores_tiempo'))

    factor.tipo = data.get('tipo', factor.tipo)
    factor.nombre = nombre
    factor.minutos_adicionales = int(data.get('minutos_adicionales') or 0)
    factor.activo = data.get('activo', '1') == '1'
    db.session.commit()
    _invalidar_cache()
    flash(f'Factor "{nombre}" actualizado.', 'success')
    return redirect(url_for('admin.listar_factores_tiempo'))


@admin_bp.route('/factores-tiempo/<int:factor_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_factor_tiempo(factor_id):
    factor = FactorTiempo.query.get_or_404(factor_id)
    factor.activo = not factor.activo
    db.session.commit()
    _invalidar_cache()
    estado = 'activado' if factor.activo else 'desactivado'
    return jsonify({'success': True, 'activo': factor.activo, 'mensaje': f'Factor {estado}.'})


@admin_bp.route('/factores-tiempo/<int:factor_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_factor_tiempo(factor_id):
    factor = FactorTiempo.query.get_or_404(factor_id)
    nombre = factor.nombre
    try:
        ReservaFactorTiempo.query.filter_by(factor_tiempo_id=factor.id).delete()
        db.session.delete(factor)
        db.session.commit()
        _invalidar_cache()
        flash(f'Factor "{nombre}" eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error('/admin/factores-tiempo/eliminar', str(e))
        flash('Error al eliminar el factor.', 'danger')
    return redirect(url_for('admin.listar_factores_tiempo'))
