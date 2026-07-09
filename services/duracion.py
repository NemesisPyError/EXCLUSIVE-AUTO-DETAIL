from datetime import date, time, datetime, timedelta, timezone
from extensions import db
from models.horario import Horario
from models.reserva import Reserva
from models.box import Box
from models.precio_servicio import PrecioServicio


class CalculadorDuracion:

    MARGEN_TALLER_MINUTOS = 15

    @classmethod
    def calcular_duracion(cls, servicio_id, tipo_vehiculo_id, segmento_id,
                          nivel_suciedad_id, adicionales_ids=None):
        ids_a_consultar = [servicio_id]
        if adicionales_ids:
            ids_a_consultar.extend(adicionales_ids)

        precios = {
            p.servicio_id: p
            for p in db.session.query(PrecioServicio).filter(
                PrecioServicio.servicio_id.in_(ids_a_consultar),
                PrecioServicio.tipo_vehiculo_id == tipo_vehiculo_id,
                PrecioServicio.segmento_id == segmento_id,
                PrecioServicio.nivel_suciedad_id == nivel_suciedad_id,
            ).all()
        }

        base = precios.get(servicio_id)
        minutos = base.duracion_minutos if base else 60

        if adicionales_ids:
            for ad_id in adicionales_ids:
                ad = precios.get(ad_id)
                if ad:
                    minutos += ad.duracion_minutos

        minutos += cls.MARGEN_TALLER_MINUTOS
        return minutos


class PlanificadorOcupacion:

    @classmethod
    def boxes_disponibles(cls, tipo_vehiculo_id):
        from models.box_tipo_vehiculo import BoxTipoVehiculo

        tipo_box_ids = (
            db.session.query(BoxTipoVehiculo.tipo_box_id)
            .filter_by(tipo_vehiculo_id=tipo_vehiculo_id)
            .all()
        )
        tipo_box_id_list = [b[0] for b in tipo_box_ids]

        if not tipo_box_id_list:
            return []

        return (
            db.session.query(Box)
            .filter(
                Box.tipo_box_id.in_(tipo_box_id_list),
                Box.activo.is_(True),
            )
            .order_by(Box.tipo_box_id, Box.orden)
            .all()
        )

    @classmethod
    def _hora_a_minutos(cls, t):
        return t.hour * 60 + t.minute

    @classmethod
    def _reservas_en_box_fecha(cls, box_id, fecha):
        query = (
            db.session.query(Reserva)
            .filter(
                Reserva.fecha == fecha,
                Reserva.deleted_at.is_(None),
            )
        )
        if box_id is not None:
            query = query.filter(Reserva.box_id == box_id)
        return query.order_by(Reserva.hora_inicio).all()

    @classmethod
    def hay_disponibilidad(cls, box_id, fecha, hora_inicio, duracion_min):
        inicio_min = cls._hora_a_minutos(hora_inicio)
        fin_min = inicio_min + duracion_min

        reservas = cls._reservas_en_box_fecha(box_id, fecha)

        for r in reservas:
            r_inicio = cls._hora_a_minutos(r.hora_inicio)
            r_fin = r_inicio + r.duracion_total_min
            if inicio_min < r_fin and fin_min > r_inicio:
                return False
        return True

    @classmethod
    def asignar_box(cls, tipo_vehiculo_id, fecha, hora_inicio, duracion_min):
        boxes = cls.boxes_disponibles(tipo_vehiculo_id)
        for box in boxes:
            if cls.hay_disponibilidad(box.id, fecha, hora_inicio, duracion_min):
                return box
        return None

    @classmethod
    def horario_activo(cls, dia_semana):
        return (
            Horario.query
            .filter_by(dia_semana=dia_semana, activo=True)
            .first()
        )

    @classmethod
    def slots_disponibles(cls, fecha, duracion_min, tipo_vehiculo_id=None):
        horario = cls.horario_activo(fecha.isoweekday())
        if not horario:
            return []

        boxes = []
        if tipo_vehiculo_id:
            boxes = cls.boxes_disponibles(tipo_vehiculo_id)

        box_ids = [b.id for b in boxes] if boxes else []
        reservas = {}
        if box_ids:
            for r in cls._reservas_en_box_fecha(None, fecha):
                if r.box_id in box_ids:
                    reservas.setdefault(r.box_id, []).append(r)
            for bid in box_ids:
                reservas.setdefault(bid, [])

        slots = []
        intervalo = 30
        hora = datetime.combine(fecha, horario.hora_inicio)
        fin = datetime.combine(fecha, horario.hora_fin)

        while hora + timedelta(minutes=duracion_min) <= fin:
            hh = hora.time()
            disponible = False

            if box_ids:
                for bid in box_ids:
                    ocupado = False
                    for r in reservas.get(bid, []):
                        r_inicio = cls._hora_a_minutos(r.hora_inicio)
                        r_fin = r_inicio + r.duracion_total_min
                        slot_inicio = cls._hora_a_minutos(hh)
                        slot_fin = slot_inicio + duracion_min
                        if slot_inicio < r_fin and slot_fin > r_inicio:
                            ocupado = True
                            break
                    if not ocupado:
                        disponible = True
                        break
            else:
                disponible = True

            slots.append({
                'hora': hh.strftime('%H:%M'),
                'disponible': disponible,
            })
            hora += timedelta(minutes=intervalo)

        return slots

    @classmethod
    def validar_multidia(cls, fecha, dias, duracion_min):
        resultado = []
        for i in range(dias):
            dia = fecha + timedelta(days=i)
            horario = cls.horario_activo(dia.isoweekday())
            resultado.append({
                'fecha': dia.isoformat(),
                'disponible': horario is not None,
            })
        return resultado

    @classmethod
    def obtener_agenda_dia(cls, fecha):
        horario = cls.horario_activo(fecha.isoweekday())
        if not horario:
            return {"boxes": [], "horas": [], "horas_objs": [], "reservas": {}}

        from sqlalchemy.orm import joinedload
        boxes = (
            Box.query
            .options(joinedload(Box.tipo_box))
            .order_by(Box.tipo_box_id, Box.orden)
            .all()
        )

        horas = []
        horas_objs = []
        h = datetime.combine(fecha, horario.hora_inicio)
        fin = datetime.combine(fecha, horario.hora_fin)
        while h < fin:
            horas.append(h.strftime('%H:%M'))
            horas_objs.append(h)
            h += timedelta(minutes=30)

        reservas = (
            db.session.query(Reserva)
            .options(
                joinedload(Reserva.cliente),
                joinedload(Reserva.servicio),
                joinedload(Reserva.vehiculo).joinedload('tipo_vehiculo'),
            )
            .filter(
                Reserva.fecha == fecha,
                Reserva.box_id.isnot(None),
                Reserva.deleted_at.is_(None),
            )
            .order_by(Reserva.box_id, Reserva.hora_inicio)
            .all()
        )

        reservas_por_box = {}
        for r in reservas:
            reservas_por_box.setdefault(r.box_id, []).append(r)

        return {
            "boxes": boxes,
            "horas": horas,
            "horas_objs": horas_objs,
            "reservas": reservas_por_box,
        }
