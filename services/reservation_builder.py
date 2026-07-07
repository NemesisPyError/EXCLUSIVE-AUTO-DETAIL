from extensions import db
from models.cliente import Cliente
from models.vehiculo import Vehiculo
from models.reserva import Reserva, ReservaServicio
from models.servicio import Servicio
from models.estado_reserva import EstadoReserva
from models.factor_tiempo import FactorTiempo, ReservaFactorTiempo
from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.tipo_lavado import TipoLavado
from models.subtipo_lavado import SubTipoLavado
from models.tipo_detallado import TipoDetallado
from models.reserva_item import ReservaItem
from services.validaciones import (
    validar_telefono_paraguay,
    validar_fecha_futura,
    validar_disponibilidad_por_rango,
)
from services.duracion import CalculadorDuracion
from services.pricing_service import PricingEngine
from services.security_service import log_error
from datetime import datetime
import secrets
import re


class ReservationBuilder:

    @staticmethod
    def build_reservation(data):
        if not data:
            return False, {'error': 'Datos JSON requeridos.'}, 400

        nombre = (data.get('nombre') or '').strip()
        apellido = (data.get('apellido') or '').strip()
        cedula = (data.get('cedula') or '').strip()
        telefono = (data.get('telefono') or '').strip()
        tipo_vehiculo_slug = (data.get('tipo_vehiculo_slug') or '').strip()
        tipo_vehiculo_nombre = (data.get('tipo_vehiculo') or '').strip()
        marca = (data.get('marca') or '').strip()
        modelo = (data.get('modelo') or '').strip()
        categoria_slug = (data.get('categoria_slug') or '').strip()
        tipo_lavado_slug = (data.get('tipo_lavado_slug') or '').strip() or None
        subtipo_slug = (data.get('subtipo_slug') or '').strip() or None
        tipo_detallado_slug = (data.get('tipo_detallado_slug') or '').strip() or None
        servicio_ids = data.get('servicio_ids') or []
        factor_ids = data.get('factor_ids') or []
        fecha_str = (data.get('fecha') or '').strip()
        hora_str = (data.get('hora') or '').strip()
        fecha_fin_str = (data.get('fecha_fin') or '').strip() or None
        dias_bloqueo = data.get('dias_bloqueo')

        errores = []

        if not nombre:
            errores.append({'campo': 'nombre', 'error': 'El nombre es obligatorio.'})
        if not apellido:
            errores.append({'campo': 'apellido', 'error': 'El apellido es obligatorio.'})

        if not cedula:
            errores.append({'campo': 'cedula', 'error': 'El numero de cedula es obligatorio.'})
        elif not re.fullmatch(r'[A-Z0-9.\-]{5,20}', cedula, re.IGNORECASE):
            errores.append({'campo': 'cedula', 'error': 'Formato de cedula invalido. Use solo numeros, puntos o guiones (5-20 caracteres).'})

        if not telefono:
            errores.append({'campo': 'telefono', 'error': 'El telefono es obligatorio.'})
        elif not validar_telefono_paraguay(telefono):
            errores.append({'campo': 'telefono', 'error': 'Formato de telefono invalido. Use +5959XXXXXXXX o 09XXXXXXXX.'})

        if not marca:
            errores.append({'campo': 'marca', 'error': 'La marca es obligatoria.'})
        if not modelo:
            errores.append({'campo': 'modelo', 'error': 'El modelo es obligatorio.'})

        if not tipo_vehiculo_slug:
            errores.append({'campo': 'tipo_vehiculo', 'error': 'El tipo de vehiculo es obligatorio.'})
        else:
            vehiculo_tipo = TipoVehiculo.query.filter_by(slug=tipo_vehiculo_slug, activo=True).first()
            if not vehiculo_tipo:
                errores.append({'campo': 'tipo_vehiculo', 'error': 'Tipo de vehiculo no valido.'})

        if not categoria_slug:
            errores.append({'campo': 'categoria', 'error': 'La categoria de servicio es obligatoria.'})
        else:
            categoria = CategoriaServicio.query.filter_by(slug=categoria_slug, activo=True).first()
            if not categoria:
                errores.append({'campo': 'categoria', 'error': 'Categoria de servicio no valida.'})

        if not fecha_str:
            errores.append({'campo': 'fecha', 'error': 'La fecha es obligatoria.'})
        else:
            try:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                if not validar_fecha_futura(fecha):
                    errores.append({'campo': 'fecha', 'error': 'La fecha debe ser hoy o futura.'})
            except (ValueError, TypeError):
                errores.append({'campo': 'fecha', 'error': 'Formato de fecha invalido. Use YYYY-MM-DD.'})
                fecha = None

        if not hora_str:
            errores.append({'campo': 'hora', 'error': 'La hora es obligatoria.'})
        else:
            try:
                hora = datetime.strptime(hora_str, '%H:%M').time()
            except (ValueError, TypeError):
                errores.append({'campo': 'hora', 'error': 'Formato de hora invalido. Use HH:MM.'})
                hora = None

        if errores:
            return False, {'errores': errores}, 422

        precio_data, _ = PricingEngine.obtener_precio(
            vehiculo_slug=tipo_vehiculo_slug,
            categoria_slug=categoria_slug,
            tipo_lavado_slug=tipo_lavado_slug,
            subtipo_slug=subtipo_slug,
            tipo_detallado_slug=tipo_detallado_slug,
        )

        if precio_data is None:
            return False, {
                'errores': [{'campo': 'servicio', 'error': 'No se encontro precio para esta combinacion de vehiculo y servicio.'}],
            }, 409

        duracion_total = precio_data['tiempo_estimado_min']

        if factor_ids:
            duracion_total += CalculadorDuracion.calcular([], factor_ids)

        if servicio_ids:
            duracion_total += CalculadorDuracion.calcular(servicio_ids, [])

        try:
            Reserva.query.filter(
                Reserva.fecha == fecha
            ).with_for_update().all()

            disponible, error_msg = validar_disponibilidad_por_rango(
                fecha, hora, duracion_total, lock_rows=True
            )
            if not disponible:
                db.session.rollback()
                return False, {
                    'errores': [
                        {'campo': 'hora', 'error': error_msg or 'Horario no disponible.'}
                    ],
                }, 409

            hora_fin = CalculadorDuracion.calcular_hora_fin(hora, duracion_total)

            fecha_fin = None
            if fecha_fin_str:
                try:
                    fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    fecha_fin = None

            cliente = Cliente(
                nombre=nombre,
                apellido=apellido,
                cedula=cedula,
                telefono=telefono,
                email=None,
            )
            db.session.add(cliente)
            db.session.flush()

            estado_pendiente = EstadoReserva.query.filter_by(
                nombre='Pendiente'
            ).first()
            if not estado_pendiente:
                return False, {'error': 'Estado Pendiente no encontrado.'}, 500

            es_estimado = precio_data.get('es_precio_estimado', False)
            precio_valor = (
                precio_data.get('precio_estimado') if es_estimado
                else precio_data.get('precio_fijo')
            )

            reserva = Reserva(
                cliente_id=cliente.id,
                estado_id=estado_pendiente.id,
                fecha=fecha,
                hora_inicio=hora,
                duracion_total_min=duracion_total,
                hora_fin=hora_fin,
                fecha_fin=fecha_fin,
                dias_bloqueo=precio_data.get('dias_bloqueo') or 0,
                categoria_servicio_id=categoria.id,
                tipo_lavado_id=TipoLavado.query.filter_by(slug=tipo_lavado_slug).first().id if tipo_lavado_slug else None,
                subtipo_lavado_id=SubTipoLavado.query.filter_by(slug=subtipo_slug).first().id if subtipo_slug else None,
                tipo_detallado_id=TipoDetallado.query.filter_by(slug=tipo_detallado_slug).first().id if tipo_detallado_slug else None,
                requiere_inspeccion=es_estimado,
                precio_estimado=precio_data.get('precio_estimado'),
                precio_final=precio_data.get('precio_fijo') if not es_estimado else None,
                observaciones=data.get('observaciones', ''),
            )
            db.session.add(reserva)
            db.session.flush()

            token = secrets.token_urlsafe(32)
            reserva.confirmacion_token = token

            vehiculo = Vehiculo(
                reserva_id=reserva.id,
                tipo_vehiculo=tipo_vehiculo_nombre or tipo_vehiculo_slug,
                tipo_vehiculo_id=vehiculo_tipo.id,
                marca=marca,
                modelo=modelo,
                anio=data.get('anio'),
                color=data.get('color'),
                nivel_suciedad=(tipo_lavado_slug or ''),
            )
            db.session.add(vehiculo)

            item_desc = precio_data.get('descripcion_publica') or (
                f'{categoria.nombre}' +
                (f' {tipo_lavado_slug}' if tipo_lavado_slug else '') +
                (f' {subtipo_slug}' if subtipo_slug else '') +
                (f' {tipo_detallado_slug}' if tipo_detallado_slug else '')
            )
            db.session.add(ReservaItem(
                reserva_id=reserva.id,
                tipo_item=categoria.slug,
                regla_precio_id=precio_data.get('regla_id'),
                precio_aplicado=precio_valor,
                tiempo_aplicado_min=precio_data['tiempo_estimado_min'],
                descripcion=item_desc,
            ))

            if servicio_ids:
                servicios_activos = Servicio.query.filter(
                    Servicio.id.in_(servicio_ids),
                    Servicio.activo.is_(True),
                ).all()
                servicios_map = {s.id: s for s in servicios_activos}
                for sid in servicio_ids:
                    srv = servicios_map.get(sid)
                    if srv:
                        db.session.add(ReservaServicio(reserva_id=reserva.id, servicio_id=sid))
                        db.session.add(ReservaItem(
                            reserva_id=reserva.id,
                            tipo_item='tratamiento',
                            servicio_id=sid,
                            precio_aplicado=float(srv.precio),
                            tiempo_aplicado_min=srv.tiempo_estimado_min,
                            descripcion=srv.nombre,
                        ))

            if factor_ids:
                factores_activos = FactorTiempo.query.filter(
                    FactorTiempo.id.in_(factor_ids),
                    FactorTiempo.activo.is_(True),
                ).all()
                factores_map = {f.id for f in factores_activos}
                for fid in factor_ids:
                    if fid in factores_map:
                        db.session.add(ReservaFactorTiempo(reserva_id=reserva.id, factor_tiempo_id=fid))

            db.session.commit()
            return True, {'reserva_id': reserva.id, 'confirmacion_token': token}, 201

        except Exception as e:
            db.session.rollback()
            log_error('/reservas/crear', str(e))
            return False, {'error': 'Ocurrio un error al procesar la reserva. Intente nuevamente.'}, 500
