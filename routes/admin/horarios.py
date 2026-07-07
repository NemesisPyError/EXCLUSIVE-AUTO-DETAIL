from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from decorators import role_required
from models.horario import Horario
from datetime import datetime
from routes.admin import admin_bp, _invalidar_cache


@admin_bp.route('/horarios')
@login_required
@role_required('admin')
def listar_horarios():
    horarios = Horario.query.order_by(Horario.dia_semana, Horario.hora_inicio).all()
    return render_template('admin/horarios.html', horarios=horarios)


@admin_bp.route('/horarios/guardar', methods=['POST'])
@login_required
@role_required('admin')
def guardar_horarios():
    data = request.get_json(silent=True) or request.form

    if data.get('_method') == 'DELETE':
        return jsonify({'success': False, 'error': 'Use el toggle activo/inactivo para deshabilitar.'}), 400

    dia_semana = int(data.get('dia_semana', 0))
    hora_inicio_str = data.get('hora_inicio', '').strip()
    hora_fin_str = data.get('hora_fin', '').strip()

    if not 1 <= dia_semana <= 6:
        return jsonify({'success': False, 'error': 'Día de semana inválido (1=Lun, ..., 6=Sáb).'}), 400

    try:
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Formato de hora inválido. Use HH:MM.'}), 400

    if hora_inicio >= hora_fin:
        return jsonify({'success': False, 'error': 'hora_inicio debe ser menor a hora_fin.'}), 400

    horario_id = data.get('horario_id')
    if horario_id:
        horario = Horario.query.get(int(horario_id))
        if not horario:
            return jsonify({'success': False, 'error': 'Horario no encontrado.'}), 404
        horario.hora_inicio = hora_inicio
        horario.hora_fin = hora_fin
    else:
        horario = Horario(
            dia_semana=dia_semana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            capacidad_maxima=int(data.get('capacidad_maxima', 3)),
            activo=True,
        )
        db.session.add(horario)

    db.session.commit()
    _invalidar_cache()
    flash('Bloque horario guardado.', 'success')
    return redirect(url_for('admin.listar_horarios'))


@admin_bp.route('/horarios/<int:horario_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def toggle_horario(horario_id):
    horario = Horario.query.get_or_404(horario_id)
    horario.activo = not horario.activo
    db.session.commit()
    _invalidar_cache()
    estado = 'activado' if horario.activo else 'desactivado'
    return jsonify({'success': True, 'activo': horario.activo, 'mensaje': f'Horario {estado}.'})


@admin_bp.route('/horarios/<int:horario_id>/capacidad', methods=['POST'])
@login_required
@role_required('admin')
def cambiar_capacidad(horario_id):
    data = request.get_json(silent=True) or {}
    horario = Horario.query.get_or_404(horario_id)
    capacidad = data.get('capacidad_maxima')
    if not capacidad or int(capacidad) < 1:
        return jsonify({'success': False, 'error': 'La capacidad debe ser al menos 1.'}), 400
    horario.capacidad_maxima = int(capacidad)
    db.session.commit()
    _invalidar_cache()
    return jsonify({'success': True, 'capacidad_maxima': horario.capacidad_maxima})
