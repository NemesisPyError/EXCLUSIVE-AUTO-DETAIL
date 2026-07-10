import secrets
from datetime import datetime, timedelta, timezone, date as date_type, time as time_type
from extensions import db
from models.cliente import Cliente
from models.vehiculo import Vehiculo
from models.reserva import Reserva
from models.reserva_adicional import ReservaAdicional
from models.solicitud_catalogo import SolicitudCatalogo
from models.servicio import Servicio
from models.estado_reserva import EstadoReserva
from models.nivel_suciedad import NivelSuciedad
from services.pricing_service import PricingEngine
from services.duracion import CalculadorDuracion, PlanificadorOcupacion
from services.validaciones import (
    validar_telefono_py, validar_fecha_futura,
    validar_dentro_horario, validar_disponibilidad,
)


class ReservationValidationError(ValueError):
    pass


class ReservationBuilder:

    @classmethod
    def build_reservation(cls, data):
        if isinstance(data.get('fecha'), str):
            data['fecha'] = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
        if isinstance(data.get('hora_inicio'), str):
            data['hora_inicio'] = datetime.strptime(data['hora_inicio'], '%H:%M').time()

        errors = cls._validate_input(data)
        if errors:
            raise ReservationValidationError(errors)

        try:
            cliente = cls._get_or_create_cliente(data)
            vehiculo = cls._get_or_create_vehiculo(data, cliente)
            servicio = db.session.get(Servicio, data['servicio_id'])
            if not servicio:
                raise ReservationValidationError({'servicio_id': 'Servicio no encontrado.'})

            nivel_suciedad = db.session.get(NivelSuciedad, data['nivel_suciedad_id'])
            if not nivel_suciedad:
                raise ReservationValidationError({'nivel_suciedad_id': 'Nivel de suciedad no valido.'})

            estado = EstadoReserva.query.filter_by(nombre='Pendiente').first()
            if not estado:
                raise ReservationValidationError({'estado': 'Estado Pendiente no encontrado.'})

            duracion = CalculadorDuracion.calcular_duracion(
                servicio.id,
                vehiculo.tipo_vehiculo_id,
                vehiculo.segmento_id,
                nivel_suciedad.id,
                data.get('adicionales_ids', []),
            )

            fecha = data['fecha']
            hora_inicio = data['hora_inicio']
            dia_semana = fecha.isoweekday()

            ok, msg = validar_dentro_horario(dia_semana, hora_inicio, duracion)
            if not ok:
                raise ReservationValidationError({'horario': msg})

            precio = PricingEngine.obtener_precio(
                servicio.id,
                vehiculo.tipo_vehiculo_id,
                vehiculo.segmento_id,
                nivel_suciedad.id,
            )
            if not precio:
                raise ReservationValidationError({'precio': 'No hay precio configurado.'})

            precio_base = precio['precio']
            precio_adicionales = 0
            adicionales_precios = {}

            if data.get('adicionales_ids'):
                for ad_id in data['adicionales_ids']:
                    ad_precio = PricingEngine.obtener_precio(
                        ad_id, vehiculo.tipo_vehiculo_id,
                        vehiculo.segmento_id, nivel_suciedad.id,
                    )
                    adicionales_precios[ad_id] = ad_precio
                    if ad_precio:
                        precio_adicionales += ad_precio['precio']

            box_id = cls._asignar_box_atomico(
                vehiculo.tipo_vehiculo_id, fecha, hora_inicio, duracion
            )
            if box_id is None:
                raise ReservationValidationError({'disponibilidad': 'No hay box disponible en ese horario.'})

            fecha_entrega = fecha
            if servicio.requiere_varios_dias and servicio.dias_bloqueo:
                fecha_entrega = fecha + timedelta(days=servicio.dias_bloqueo - 1)

            confirmacion_token = secrets.token_urlsafe(32)

            reserva = Reserva(
                cliente_id=cliente.id,
                vehiculo_id=vehiculo.id,
                servicio_id=servicio.id,
                estado_reserva_id=estado.id,
                nivel_suciedad_id=nivel_suciedad.id,
                box_id=box_id,
                fecha=fecha,
                hora_inicio=hora_inicio,
                duracion_total_min=duracion,
                fecha_entrega_estimada=fecha_entrega,
                precio_estimado_base=precio_base,
                precio_estimado_adicionales=precio_adicionales,
                confirmacion_token=confirmacion_token,
            )

            db.session.add(reserva)
            db.session.flush()

            if data.get('adicionales_ids'):
                for ad_id in data['adicionales_ids']:
                    ad_servicio = db.session.get(Servicio, ad_id)
                    if not ad_servicio or ad_servicio.tipo != 'adicional':
                        continue
                    ad_precio = adicionales_precios.get(ad_id)
                    db.session.add(ReservaAdicional(
                        reserva_id=reserva.id,
                        servicio_id=ad_id,
                        precio_aplicado=ad_precio['precio'] if ad_precio else 0,
                        tiempo_aplicado_min=ad_precio['duracion_minutos'] if ad_precio else 0,
                    ))

            if vehiculo.modelo_id is None and vehiculo.marca_texto:
                solicitud_existente = (
                    db.session.query(SolicitudCatalogo)
                    .filter_by(
                        marca_texto=vehiculo.marca_texto,
                        modelo_texto=vehiculo.modelo_texto,
                        estado='pendiente',
                    )
                    .first()
                )
                if not solicitud_existente:
                    db.session.add(SolicitudCatalogo(
                        marca_texto=vehiculo.marca_texto,
                        modelo_texto=vehiculo.modelo_texto,
                        tipo_vehiculo_id=vehiculo.tipo_vehiculo_id,
                        segmento_id=vehiculo.segmento_id,
                        cliente_id=cliente.id,
                        vehiculo_id=vehiculo.id,
                        estado='pendiente',
                    ))

            db.session.commit()
            return reserva

        except ReservationValidationError:
            db.session.rollback()
            raise
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def _asignar_box_atomico(cls, tipo_vehiculo_id, fecha, hora_inicio, duracion_min):
        boxes = PlanificadorOcupacion.boxes_disponibles(tipo_vehiculo_id)
        if not boxes:
            return None

        inicio_min = PlanificadorOcupacion._hora_a_minutos(hora_inicio)
        fin_min = inicio_min + duracion_min

        for box in boxes:
            existing = (
                db.session.query(Reserva)
                .filter(
                    Reserva.box_id == box.id,
                    Reserva.fecha == fecha,
                    Reserva.deleted_at.is_(None),
                )
                .with_for_update()
                .all()
            )

            ocupado = False
            for r in existing:
                r_inicio = PlanificadorOcupacion._hora_a_minutos(r.hora_inicio)
                r_fin = r_inicio + r.duracion_total_min
                if inicio_min < r_fin and fin_min > r_inicio:
                    ocupado = True
                    break

            if not ocupado:
                return box.id

        return None

    @classmethod
    def _validate_input(cls, data):
        errors = {}
        if not data.get('servicio_id'):
            errors['servicio_id'] = 'Debe seleccionar un servicio.'
        if not data.get('nivel_suciedad_id'):
            errors['nivel_suciedad_id'] = 'Debe seleccionar el nivel de suciedad.'
        if not data.get('fecha'):
            errors['fecha'] = 'Debe seleccionar una fecha.'
        else:
            ok, msg = validar_fecha_futura(data['fecha'])
            if not ok:
                errors['fecha'] = msg
        if not data.get('hora_inicio'):
            errors['hora_inicio'] = 'Debe seleccionar una hora.'
        if not data.get('nombre') or not data.get('apellido'):
            errors['cliente'] = 'Nombre y apellido son obligatorios.'
        if data.get('telefono'):
            ok, msg = validar_telefono_py(data['telefono'])
            if not ok:
                errors['telefono'] = msg
        return errors

    @classmethod
    def _get_or_create_cliente(cls, data):
        from sqlalchemy.exc import IntegrityError
        telefono = data.get('telefono', '').strip()
        if not telefono:
            telefono = 'sin-telefono-' + datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')

        cliente = Cliente.query.filter_by(telefono=telefono).first()
        if not cliente:
            try:
                cliente = Cliente(
                    nombre=data.get('nombre', '').strip(),
                    apellido=data.get('apellido', '').strip(),
                    telefono=telefono,
                    cedula=data.get('cedula', '').strip() or None,
                    email=data.get('email', '').strip() or None,
                )
                db.session.add(cliente)
                db.session.flush()
            except IntegrityError:
                db.session.rollback()
                cliente = Cliente.query.filter_by(telefono=telefono).first()
                if not cliente:
                    raise ReservationValidationError({'telefono': 'Error al crear el cliente. Intente de nuevo.'})
        return cliente

    @classmethod
    def _get_or_create_vehiculo(cls, data, cliente):
        if data.get('vehiculo_id'):
            vehiculo = db.session.get(Vehiculo, data['vehiculo_id'])
            if vehiculo and vehiculo.cliente_id == cliente.id:
                return vehiculo

        from models.marca import Marca
        from models.modelo_vehiculo import ModeloVehiculo

        marca_id = None
        modelo_id = None
        marca_texto = None
        modelo_texto = None
        tipo_vehiculo_id = data.get('tipo_vehiculo_id')
        segmento_id = data.get('segmento_id')
        anio = data.get('anio')

        if data.get('modelo_id'):
            modelo = db.session.get(ModeloVehiculo, data['modelo_id'])
            if modelo:
                modelo_id = modelo.id
                marca_id = modelo.marca_id
                if not tipo_vehiculo_id:
                    tipo_vehiculo_id = modelo.tipo_vehiculo_id
                if not segmento_id:
                    segmento_id = modelo.segmento_id
        else:
            marca_texto = data.get('marca', '').strip()
            modelo_texto = data.get('modelo', '').strip()
            if not marca_texto:
                marca_texto = 'No especificada'
            if not modelo_texto:
                modelo_texto = 'No especificado'

            marca_existente = Marca.query.filter(
                db.func.lower(Marca.nombre) == marca_texto.lower()
            ).first()
            if marca_existente:
                marca_id = marca_existente.id

        if not tipo_vehiculo_id or not segmento_id:
            raise ReservationValidationError({'vehiculo': 'Tipo de vehiculo y segmento son obligatorios.'})

        vehiculo = Vehiculo(
            cliente_id=cliente.id,
            marca_id=marca_id,
            modelo_id=modelo_id,
            marca_texto=marca_texto,
            modelo_texto=modelo_texto,
            tipo_vehiculo_id=tipo_vehiculo_id,
            segmento_id=segmento_id,
            anio=anio,
            color=data.get('color', '').strip() or None,
            chapa=data.get('chapa', '').strip() or None,
            combustible=data.get('combustible', '').strip() or None,
            transmision=data.get('transmision', '').strip() or None,
        )
        db.session.add(vehiculo)
        db.session.flush()
        return vehiculo
