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

    dia_semana = int(data.get('dia_semana', 0))
    hora_inicio_str = data.get('hora_inicio', '').strip()
    hora_fin_str = data.get('hora_fin', '').strip()

    if not 1 <= dia_semana <= 7:
        return jsonify({'success': False, 'error': 'Dia de semana invalido (1=Lun, ..., 7=Dom).'}), 400

    try:
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Formato de hora invalido. Use HH:MM.'}), 400

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
