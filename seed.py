"""
Seed script --- Puebla la base de datos con datos iniciales.
Uso: python seed.py
"""
from app import create_app
from extensions import db
from models.servicio import Servicio
from models.estado_reserva import EstadoReserva
from models.horario import Horario
from models.usuario import Usuario
from models.galeria import Galeria
from models.factor_tiempo import FactorTiempo
from models.tipo_vehiculo import TipoVehiculo
from models.categoria_servicio import CategoriaServicio
from models.tipo_lavado import TipoLavado
from models.subtipo_lavado import SubTipoLavado
from models.tipo_detallado import TipoDetallado
from models.regla_precio import ReglaPrecio
from datetime import time

app = create_app()

with app.app_context():
    if Servicio.query.count() > 0:
        print("La base de datos ya tiene datos. Omitiendo seed.")
        exit()

    print("Sembrando datos iniciales...")

    # --- Estados de reserva ---
    estados = [
        ('Pendiente', '#ffc107', 1),
        ('Confirmada', '#0d6efd', 2),
        ('Vehiculo recibido', '#17a2b8', 3),
        ('En proceso', '#6f42c1', 4),
        ('Lavado terminado', '#fd7e14', 5),
        ('Esperando retiro', '#198754', 6),
        ('Finalizada', '#0dcaf0', 7),
        ('Cancelada', '#dc3545', 8),
    ]
    for nombre, color, orden in estados:
        db.session.add(EstadoReserva(nombre=nombre, color_badge=color, orden=orden))

    # --- Servicios (backward compat, old model) ---
    servicios = [
        ('Lavado Express', 'Lavado exterior rapido con shampoo neutro, secado y neblinado de neumaticos.',
         'lavado_vehiculo', 5000.00, 20),
        ('Lavado Detallado', 'Lavado exterior e interior completo, aspirado profundo, lavado de tapizados y plasticos.',
         'lavado_vehiculo', 12000.00, 60),
        ('Limpieza Integral', 'Lavado Detallado + limpieza de motor, desinfeccion interna y tratamiento de cueros.',
         'lavado_vehiculo', 20000.00, 120),
        ('Pulido Comercial', 'Pulido mecanico de una etapa, abrillantado y encerado con sellante de alta duracion.',
         'tratamiento_pintura', 25000.00, 180),
        ('Pulido Tecnico', 'Pulido de dos etapas con correccion de pintura, lustre final y recubrimiento sellador.',
         'tratamiento_pintura', 40000.00, 300),
        ('Revestimiento Ceramico', 'Aplicacion de recubrimiento ceramico de 9H de dureza, proteccion contra rayos UV y quimicos.',
         'tratamiento_pintura', 60000.00, 480),
        ('Remocion de Lluvia Acida', 'Tratamiento quimico-mecanico para eliminar manchas de lluvia acida de la pintura y cristales.',
         'tratamiento_pintura', 15000.00, 120),
        ('Lavado Express de Motos', 'Lavado exterior rapido, cadena y lubricacion basica.',
         'lavado_moto', 3000.00, 20),
        ('Lavado Detallado de Motos', 'Lavado completo, pulido de carenados, tratamiento de cromados y acondicionamiento de cadena.',
         'lavado_moto', 8000.00, 60),
        ('Retiro y Entrega del Vehiculo', 'Nos encargamos de retirar tu vehiculo en la direccion que nos indiques.',
         'retiro_entrega', 0.00, 0),
    ]
    for nombre, desc, cat, precio, tiempo in servicios:
        db.session.add(Servicio(
            nombre=nombre, descripcion=desc, categoria=cat,
            precio=precio, tiempo_estimado_min=tiempo, activo=True
        ))

    # --- Factores de Tiempo (legacy) ---
    factores_suciedad = [
        ('Leve', 0), ('Media', 15), ('Alta', 30), ('Extrema', 60),
    ]
    for i, (nombre, minutos) in enumerate(factores_suciedad):
        db.session.add(FactorTiempo(
            tipo='suciedad', nombre=nombre,
            minutos_adicionales=minutos, orden=i + 1, activo=True
        ))

    factores_condicion = [
        ('Mucho barro', 15), ('Arena', 10), ('Pelo de mascotas', 20),
        ('Interior muy sucio', 25), ('Manchas dificiles', 30),
        ('Restos de comida', 15), ('Lluvia acida', 20),
    ]
    for i, (nombre, minutos) in enumerate(factores_condicion):
        db.session.add(FactorTiempo(
            tipo='condicion', nombre=nombre,
            minutos_adicionales=minutos, orden=i + 1, activo=True
        ))

    # --- Usuario admin ---
    admin = Usuario(nombre='Administrador', email='admin@exclusiveautodetail.com', rol='admin', activo=True)
    admin.set_password('Admin1234!')
    db.session.add(admin)

    # --- Horarios (lunes a sabado, 07:00 a 17:00, capacidad 3) ---
    for dia in range(1, 7):
        db.session.add(Horario(
            dia_semana=dia, hora_inicio=time(7, 0), hora_fin=time(17, 0),
            capacidad_maxima=3, activo=True
        ))

    # --- Galeria (categorias placeholder) ---
    galeria_cats = [
        'Antes y Despues', 'Resultado Pulido', 'Revestimiento Ceramico',
        'Detalle Interior', 'Lavado Profundo', 'Brillo Final',
    ]
    for orden, cat in enumerate(galeria_cats, start=1):
        db.session.add(Galeria(
            titulo=cat, descripcion=None,
            url_imagen=f'/static/img/placeholder-galeria-{orden}.jpg',
            tipo=cat, activo=True, orden=orden
        ))

    # ---------------------------------------------------------------
    # NUEVA ARQUITECTURA FASE 2
    # ---------------------------------------------------------------

    # --- Tipos de Vehiculo ---
    tipos_vehiculo = [
        ('Auto', 'auto', 'fa-solid fa-car', 1),
        ('SUV / Camioneta', 'suv-camioneta', 'fa-solid fa-truck', 2),
        ('Moto baja cilindrada', 'moto-baja', 'fa-solid fa-motorcycle', 3),
        ('Moto alta cilindrada', 'moto-alta', 'fa-solid fa-motorcycle', 4),
    ]
    tipos_dict = {}
    for nombre, slug, icono, orden in tipos_vehiculo:
        tv = TipoVehiculo(nombre=nombre, slug=slug, icono=icono, orden=orden, activo=True)
        db.session.add(tv)
        tipos_dict[slug] = tv

    db.session.flush()

    # --- Categorias de Servicio ---
    categorias_data = [
        ('Lavado', 'lavado', True, False, True, 1),
        ('Detallado', 'detallado', False, False, True, 2),
        ('Integral', 'integral', False, True, False, 3),
        ('Tratamientos Especiales', 'tratamientos', False, False, False, 4),
    ]
    cats_dict = {}
    for nombre, slug, usa_nivel, permite_md, tiene_st, orden in categorias_data:
        cat = CategoriaServicio(
            nombre=nombre, slug=slug,
            usa_nivel_suciedad=usa_nivel,
            permite_multidias=permite_md,
            tiene_subtipos=tiene_st,
            orden=orden, activo=True
        )
        db.session.add(cat)
        cats_dict[slug] = cat

    db.session.flush()

    # --- Tipos de Lavado (Normal, Alta, Extrema) ---
    lavados_data = [
        ('Normal', 'normal', False, False, 1),
        ('Alta', 'alta', True, True, 2),
        ('Extrema', 'extrema', True, True, 3),
    ]
    lavados_dict = {}
    for nombre, slug, cerrado, insp, orden in lavados_data:
        tl = TipoLavado(
            nombre=nombre, slug=slug,
            es_cerrado=cerrado, requiere_inspeccion=insp,
            orden=orden, activo=True
        )
        db.session.add(tl)
        lavados_dict[slug] = tl

    db.session.flush()

    # --- SubTipos de Lavado (Interior, Exterior, Completo) - solo para Normal ---
    subtipos_data = [
        ('Interior', 'interior', 1),
        ('Exterior', 'exterior', 2),
        ('Completo', 'completo', 3),
    ]
    subtipos_dict = {}
    for nombre, slug, orden in subtipos_data:
        st = SubTipoLavado(
            tipo_lavado_id=lavados_dict['normal'].id,
            nombre=nombre, slug=slug,
            orden=orden, activo=True
        )
        db.session.add(st)
        subtipos_dict[slug] = st

    db.session.flush()

    # --- Tipos de Detallado ---
    detallado_data = [
        ('Detallado Interior', 'detallado-interior', 1),
        ('Detallado Exterior', 'detallado-exterior', 2),
        ('Detallado Completo', 'detallado-completo', 3),
    ]
    detallados_dict = {}
    for nombre, slug, orden in detallado_data:
        td = TipoDetallado(nombre=nombre, slug=slug, orden=orden, activo=True)
        db.session.add(td)
        detallados_dict[slug] = td

    db.session.flush()

    # --- Reglas de Precio (matrix) ---
    # Precios base por combinacion: (categoria, vehiculo, tipo_lavado, subtipo, precio, tiempo)
    # Para NORMAL: precio_fijo
    # Para ALTA/EXTREMA: precio_estimado + es_precio_estimado=True

    reglas = []

    lav_normal_precios = {
        'auto': {'interior': (25000, 30), 'exterior': (20000, 25), 'completo': (40000, 50)},
        'suv-camioneta': {'interior': (35000, 40), 'exterior': (28000, 35), 'completo': (55000, 70)},
        'moto-baja': {'interior': (10000, 20), 'exterior': (8000, 15), 'completo': (15000, 30)},
        'moto-alta': {'interior': (15000, 25), 'exterior': (12000, 20), 'completo': (22000, 40)},
    }
    for veh_slug, subtipos in lav_normal_precios.items():
        for st_slug, (precio, tiempo) in subtipos.items():
            reglas.append((
                cats_dict['lavado'].id, tipos_dict[veh_slug].id,
                lavados_dict['normal'].id, subtipos_dict[st_slug].id,
                None, None, precio, None, False, tiempo, 0,
                'Lavado Normal', None, True
            ))

    # Alta y Extrema (precio_estimado)
    for tipo_slug in ['alta', 'extrema']:
        for veh_slug, precio_tiempo in {
            'auto': (60000, 90),
            'suv-camioneta': (80000, 120),
            'moto-baja': (25000, 45),
            'moto-alta': (35000, 60),
        }.items():
            precio, tiempo = precio_tiempo
            reglas.append((
                cats_dict['lavado'].id, tipos_dict[veh_slug].id,
                lavados_dict[tipo_slug].id, None,
                None, None, None, precio, True, tiempo, 0,
                f'Lavado {tipo_slug.capitalize()}',
                'El precio puede variar luego de la inspeccion visual del vehiculo.',
                True
            ))

    # Detallado
    for td_slug, precio_tiempo in {
        'detallado-interior': {'auto': (150000, 180), 'suv-camioneta': (200000, 240),
                                'moto-baja': (60000, 90), 'moto-alta': (80000, 120)},
        'detallado-exterior': {'auto': (120000, 150), 'suv-camioneta': (160000, 200),
                                'moto-baja': (50000, 75), 'moto-alta': (65000, 100)},
        'detallado-completo': {'auto': (250000, 300), 'suv-camioneta': (330000, 400),
                                'moto-baja': (100000, 150), 'moto-alta': (130000, 200)},
    }.items():
        for veh_slug, (precio, tiempo) in precio_tiempo.items():
            reglas.append((
                cats_dict['detallado'].id, tipos_dict[veh_slug].id,
                None, None, detallados_dict[td_slug].id, None,
                precio, None, False, tiempo, 0,
                f'Detallado - {veh_slug}', None, True
            ))

    # Integral (multidia)
    for veh_slug, (precio, tiempo, dias) in {
        'auto': (300000, 480, 2),
        'suv-camioneta': (400000, 600, 3),
        'moto-baja': (120000, 240, 1),
        'moto-alta': (180000, 360, 2),
    }.items():
        reglas.append((
            cats_dict['integral'].id, tipos_dict[veh_slug].id,
            None, None, None, None,
            precio, None, False, tiempo, dias,
            'Servicio Integral', None, True
        ))

    # Tratamientos Especiales: enlazar con servicios existentes
    # IDs dependen del flush, asi que enlazamos via servicio_id luego
    # Por ahora usamos un approach de precios globales por vehiculo
    tratamientos_por_veh = {}
    for veh_slug, precios in {
        'auto': (250000, 300),
        'suv-camioneta': (350000, 400),
        'moto-baja': (80000, 120),
        'moto-alta': (120000, 180),
    }.items():
        tratamientos_por_veh[veh_slug] = precios

    for cat_id, veh_id, tl_id, stl_id, td_id, svc_id, p_fijo, p_est, es_est, tpo, dias, desc, nota, activo in reglas:
        db.session.add(ReglaPrecio(
            categoria_servicio_id=cat_id,
            tipo_vehiculo_id=veh_id,
            tipo_lavado_id=tl_id,
            subtipo_lavado_id=stl_id,
            tipo_detallado_id=td_id,
            servicio_id=svc_id,
            precio_fijo=p_fijo,
            precio_estimado=p_est,
            es_precio_estimado=es_est,
            tiempo_estimado_min=tpo,
            dias_bloqueo=dias,
            descripcion_publica=desc,
            nota_inspeccion=nota,
            activo=activo,
        ))

    db.session.commit()
    print("Seed completado. Datos insertados:")
    print(f"  - {EstadoReserva.query.count()} estados de reserva")
    print(f"  - {Servicio.query.count()} servicios (legacy)")
    print(f"  - {Usuario.query.count()} usuarios (admin: admin@exclusiveautodetail.com / Admin1234!)")
    print(f"  - {Horario.query.count()} horarios")
    print(f"  - {FactorTiempo.query.count()} factores de tiempo")
    print(f"  - {Galeria.query.count()} imagenes de galeria")
    print(f"  - {TipoVehiculo.query.count()} tipos de vehiculo")
    print(f"  - {CategoriaServicio.query.count()} categorias de servicio")
    print(f"  - {TipoLavado.query.count()} tipos de lavado")
    print(f"  - {SubTipoLavado.query.count()} subtipos de lavado")
    print(f"  - {TipoDetallado.query.count()} tipos de detallado")
    print(f"  - {ReglaPrecio.query.count()} reglas de precio")
