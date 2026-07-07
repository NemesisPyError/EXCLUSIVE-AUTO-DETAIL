from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from decorators import role_required
from models.cliente import Cliente
from services.security_service import log_error
from routes.admin import admin_bp


@admin_bp.route('/clientes')
@login_required
@role_required('admin')
def listar_clientes():
    import json
    buscar = request.args.get('buscar', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Cliente.query

    if buscar:
        like = f'%{buscar}%'
        query = query.filter(
            db.or_(
                Cliente.nombre.ilike(like),
                Cliente.apellido.ilike(like),
                Cliente.telefono.ilike(like),
                Cliente.cedula.ilike(like),
            )
        )

    query = query.order_by(Cliente.created_at.desc(), Cliente.apellido, Cliente.nombre)

    paginacion = query.paginate(page=page, per_page=25, error_out=False)

    clientes_data = json.dumps([
        {
            'id': c.id,
            'nombre': c.nombre,
            'apellido': c.apellido,
            'cedula': c.cedula,
            'telefono': c.telefono,
            'email': c.email or '',
            'observaciones': c.observaciones or '',
            'reservas_count': c.reservas.count(),
        }
        for c in paginacion.items
    ], ensure_ascii=False)

    return render_template(
        'admin/clientes.html',
        clientes=paginacion.items,
        paginacion=paginacion,
        buscar=buscar,
        clientes_data=clientes_data,
    )


@admin_bp.route('/clientes/<int:cliente_id>/editar', methods=['POST'])
@login_required
@role_required('admin')
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    data = request.form

    nombre = (data.get('nombre') or '').strip()
    apellido = (data.get('apellido') or '').strip()
    if not nombre or not apellido:
        flash('Nombre y apellido son obligatorios.', 'danger')
        return redirect(url_for('admin.listar_clientes'))

    cliente.nombre = nombre
    cliente.apellido = apellido
    cliente.cedula = (data.get('cedula') or '').strip() or cliente.cedula
    cliente.telefono = (data.get('telefono') or '').strip() or cliente.telefono
    cliente.email = (data.get('email') or '').strip() or None
    cliente.observaciones = (data.get('observaciones') or '').strip() or None
    db.session.commit()
    flash('Cliente actualizado correctamente.', 'success')
    return redirect(url_for('admin.listar_clientes'))


@admin_bp.route('/clientes/<int:cliente_id>/eliminar', methods=['POST'])
@login_required
@role_required('admin')
def eliminar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if cliente.reservas.count() > 0:
        flash('No se puede eliminar: el cliente tiene reservas asociadas.', 'danger')
        return redirect(url_for('admin.listar_clientes'))
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        log_error('/admin/clientes/eliminar', str(e))
        flash('Error al eliminar el cliente.', 'danger')
    return redirect(url_for('admin.listar_clientes'))
