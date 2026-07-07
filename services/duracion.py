from models.servicio import Servicio
from models.factor_tiempo import FactorTiempo
from datetime import datetime, timedelta, time, date
from extensions import db


class CalculadorDuracion:

    @staticmethod
    def calcular(servicio_ids, factor_ids):
        total = 0

        if servicio_ids:
            suma_servicios = Servicio.query.filter(
                Servicio.id.in_(servicio_ids)
            ).with_entities(
                db.func.coalesce(db.func.sum(Servicio.tiempo_estimado_min), 0)
            ).scalar()
            total += int(suma_servicios)

        if factor_ids:
            suma_factores = FactorTiempo.query.filter(
                FactorTiempo.id.in_(factor_ids),
                FactorTiempo.activo.is_(True),
            ).with_entities(
                db.func.coalesce(db.func.sum(FactorTiempo.minutos_adicionales), 0)
            ).scalar()
            total += int(suma_factores)

        return total

    @staticmethod
    def calcular_hora_fin(hora_inicio, duracion_min):
        base = datetime.combine(datetime.today(), hora_inicio)
        fin = base + timedelta(minutes=duracion_min)
        return fin.time()


class PlanificadorOcupacion:

    PASO_SLOT = 30

    # ------------------------------------------------------------------
    # Metodos de planificacion
    # ------------------------------------------------------------------

    @staticmethod
    def clasificar_servicio(duracion_min):
        if duracion_min <= 60:
            return 'rapido'
        elif duracion_min <= 180:
            return 'normal'
        return 'detallado'

    @staticmethod
    def calcular_entrega(fecha_inicio, hora_inicio, duracion_min):
        """Calcula la fecha y hora estimada de entrega considerando
        los horarios laborales. Para servicios que exceden el cierre,
        calcula el siguiente dia habil."""
        from models.horario import Horario

        restante = duracion_min
        fecha = fecha_inicio
        cursor = datetime.combine(fecha, hora_inicio)
        max_dias = 30

        for _ in range(max_dias):
            dia = fecha.weekday() + 1
            horario = Horario.query.filter_by(dia_semana=dia, activo=True).first()

            if not horario:
                fecha += timedelta(days=1)
                cursor = datetime.combine(fecha, time(7, 0))
                continue

            cierre_dt = datetime.combine(fecha, horario.hora_fin)
            if cursor < datetime.combine(fecha, horario.hora_inicio):
                cursor = datetime.combine(fecha, horario.hora_inicio)

            disponibles = int((cierre_dt - cursor).total_seconds() / 60)
            if disponibles <= 0:
                fecha += timedelta(days=1)
                cursor = datetime.combine(fecha, horario.hora_inicio)
                continue

            if disponibles >= restante:
                entrega = cursor + timedelta(minutes=restante)
                return entrega.date(), entrega.time(), None

            restante -= disponibles
            fecha += timedelta(days=1)
            dia_next = fecha.weekday() + 1
            horario_next = Horario.query.filter_by(dia_semana=dia_next, activo=True).first()
            if horario_next:
                cursor = datetime.combine(fecha, horario_next.hora_inicio)
            else:
                cursor = datetime.combine(fecha, time(7, 0))

        return None, None, 'No se pudo calcular la entrega estimada.'

    # ------------------------------------------------------------------
    # Metodos existentes (sin cambios)
    # ------------------------------------------------------------------

    @staticmethod
    def intervalos_del_dia(fecha, for_update=False):
        from models.reserva import Reserva

        if not for_update:
            from extensions import cache
            cache_key = f'intervalos:{fecha.isoformat()}'
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        query = Reserva.query.filter(Reserva.fecha == fecha)
        if for_update:
            query = query.with_for_update()
        reservas = query.all()

        intervalos = []
        for r in reservas:
            fin = r.hora_fin_calculada
            if fin is None:
                continue
            intervalos.append((r.hora_inicio, fin))

        if not for_update:
            from extensions import cache
            cache.set(f'intervalos:{fecha.isoformat()}', intervalos, timeout=1800)

        return intervalos

    @classmethod
    def concurrentes_en_punto(cls, fecha, punto_time):
        intervalos = cls.intervalos_del_dia(fecha)
        return sum(1 for ini, fin in intervalos if ini <= punto_time < fin)

    @classmethod
    def validar_reserva(cls, fecha, hora_inicio, duracion_min, lock_rows=False):
        from models.horario import Horario

        dia = fecha.weekday() + 1
        horario = Horario.query.filter_by(dia_semana=dia, activo=True).first()

        if not horario:
            return False, 'El taller no opera este dia.'

        # Para servicios rapidos/normales: no deben exceder el cierre
        clase = cls.clasificar_servicio(duracion_min)
        hora_fin = (datetime.combine(fecha, hora_inicio) + timedelta(minutes=duracion_min)).time()
        if clase != 'detallado' and hora_fin > horario.hora_fin:
            return False, 'El servicio excede el horario de cierre del taller.'

        if hora_inicio < horario.hora_inicio:
            return False, 'La hora de inicio esta fuera del horario de atencion.'

        # Para servicios detallados: verificar solo hasta el cierre del primer dia
        minutos_a_verificar = duracion_min
        cierre_dt = datetime.combine(fecha, horario.hora_fin)
        inicio_dt = datetime.combine(fecha, hora_inicio)
        if clase == 'detallado':
            minutos_hasta_cierre = int((cierre_dt - inicio_dt).total_seconds() / 60)
            if minutos_hasta_cierre > 0:
                minutos_a_verificar = min(duracion_min, minutos_hasta_cierre)

        intervalos = cls.intervalos_del_dia(fecha, for_update=lock_rows)
        capacidad = horario.capacidad_maxima

        if not intervalos:
            return True, None

        for minuto in range(0, minutos_a_verificar + 1):
            t_check = (inicio_dt + timedelta(minutes=minuto)).time()
            if t_check > horario.hora_fin:
                break
            concurrentes = sum(
                1 for ini, fin in intervalos
                if ini <= t_check < fin
            )
            if concurrentes >= capacidad:
                return False, (
                    f'Capacidad maxima ({capacidad}) '
                    f'alcanzada a las {t_check.strftime("%H:%M")} hs.'
                )

        return True, None

    @classmethod
    def capacidad_restante_en_punto(cls, fecha, punto_time):
        from models.horario import Horario

        dia = fecha.weekday() + 1
        horario = Horario.query.filter_by(dia_semana=dia, activo=True).first()
        if not horario:
            return 0

        ocupados = cls.concurrentes_en_punto(fecha, punto_time)
        return max(horario.capacidad_maxima - ocupados, 0)

    @classmethod
    def capacidad_minima_durante_intervalo(cls, fecha, hora_inicio, duracion_min):
        paso = cls.PASO_SLOT
        min_cap = None

        for offset in range(0, duracion_min + 1, paso):
            t_check = (datetime.combine(fecha, hora_inicio) + timedelta(minutes=offset)).time()
            cap = cls.capacidad_restante_en_punto(fecha, t_check)
            if min_cap is None or cap < min_cap:
                min_cap = cap
            if min_cap == 0:
                break

        return min_cap if min_cap is not None else 0

    @classmethod
    def slots_disponibles(cls, fecha, duracion_min):
        from models.horario import Horario

        dia = fecha.weekday() + 1
        horario = Horario.query.filter_by(dia_semana=dia, activo=True).first()

        if not horario:
            return []

        clase = cls.clasificar_servicio(duracion_min)
        resultado = []
        paso = cls.PASO_SLOT
        cursor = datetime.combine(fecha, horario.hora_inicio)

        while True:
            hora_actual = cursor.time()
            if hora_actual < horario.hora_inicio:
                cursor += timedelta(minutes=paso)
                continue

            hora_fin_simulada = (cursor + timedelta(minutes=duracion_min)).time()

            # Servicios rapidos/normales deben caber en el horario
            if clase != 'detallado' and hora_fin_simulada > horario.hora_fin:
                break

            # Ya no hay mas slots validos
            if cursor.time() >= horario.hora_fin:
                break

            cap = cls.capacidad_minima_durante_intervalo(fecha, hora_actual, duracion_min)
            disponible = cap > 0

            if clase == 'detallado':
                fe, he, _ = cls.calcular_entrega(fecha, hora_actual, duracion_min)
                entrega = fe.strftime('%d/%m') + ' ' + he.strftime('%H:%M') if fe and he else None
            else:
                entrega = cls._formatear_hora(hora_fin_simulada)

            resultado.append({
                'hora': hora_actual.strftime('%H:%M'),
                'disponible': disponible,
                'lugares': cap,
                'entrega': entrega,
                'clase': clase,
            })

            cursor += timedelta(minutes=paso)

        return resultado

    @staticmethod
    def _formatear_hora(t):
        return t.strftime('%H:%M') if t else None

    # ------------------------------------------------------------------
    # NUEVO: Soporte multi-dia (Integral)
    # ------------------------------------------------------------------

    @classmethod
    def reservas_en_dia(cls, fecha):
        from models.reserva import Reserva
        return Reserva.query.filter(Reserva.fecha == fecha).count()

    @classmethod
    def validar_multidia(cls, fecha_inicio, dias, duracion_min):
        resultado = {
            'disponible': True,
            'bloqueos': [],
            'dias_problema': [],
        }

        from models.horario import Horario

        fecha_cursor = fecha_inicio
        for i in range(dias):
            dia_semana = fecha_cursor.weekday() + 1

            domingo = dia_semana == 7
            if domingo:
                fecha_cursor += timedelta(days=1)
                continue

            horario = Horario.query.filter_by(
                dia_semana=dia_semana, activo=True
            ).first()

            bloque = {
                'fecha': fecha_cursor.strftime('%Y-%m-%d'),
                'dia_semana': dia_semana,
                'opera': horario is not None,
                'tiene_capacidad': False,
                'reservas_existentes': cls.reservas_en_dia(fecha_cursor),
                'capacidad_maxima': horario.capacidad_maxima if horario else 0,
            }

            if horario:
                bloque['tiene_capacidad'] = (
                    bloque['reservas_existentes'] < horario.capacidad_maxima
                )

            resultado['bloqueos'].append(bloque)

            if not horario:
                resultado['disponible'] = False
                resultado['dias_problema'].append(fecha_cursor.strftime('%Y-%m-%d'))
            elif bloque['reservas_existentes'] >= horario.capacidad_maxima:
                resultado['disponible'] = False
                resultado['dias_problema'].append(fecha_cursor.strftime('%Y-%m-%d'))

            fecha_cursor += timedelta(days=1)

        return resultado
