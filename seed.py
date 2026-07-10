"""
Seed script — Puebla la base de datos con datos iniciales.
Uso: python seed.py
"""
from datetime import time
from app import create_app
from extensions import db
from models.segmento import Segmento
from models.tipo_vehiculo import TipoVehiculo
from models.nivel_suciedad import NivelSuciedad
from models.categoria_servicio import CategoriaServicio
from models.servicio import Servicio
from models.precio_servicio import PrecioServicio
from models.tipo_box import TipoBox
from models.box import Box
from models.box_tipo_vehiculo import BoxTipoVehiculo
from models.horario import Horario
from models.estado_reserva import EstadoReserva
from models.usuario import Usuario
from models.galeria import Galeria
from models.galeria_categoria import GaleriaCategoria
from models.marca import Marca
from models.modelo_vehiculo import ModeloVehiculo
from models.servicio_tipo_vehiculo import ServicioTipoVehiculo

app = create_app()

with app.app_context():
    if Servicio.query.count() > 0:
        print("La base de datos ya tiene datos. Omitiendo seed.")
        exit()

    print("Sembrando datos iniciales...")

    # --- Segmentos ---
    segmentos_data = [
        ('Pequeño', 'pequenio', 'Vehiculos de dimensiones reducidas', 1),
        ('Mediano', 'mediano', 'Vehiculos de tamano estandar', 2),
        ('Grande', 'grande', 'Vehiculos de gran porte', 3),
        ('Extra grande', 'extra-grande', 'Furgones, vans, camiones, lanchas', 4),
    ]
    seg_dict = {}
    for nombre, slug, desc, orden in segmentos_data:
        s = Segmento(nombre=nombre, slug=slug, descripcion=desc, orden=orden)
        db.session.add(s)
        seg_dict[slug] = s
    db.session.flush()

    # --- Tipos de Vehiculo ---
    tipos_data = [
        ('Moto', 'moto', 'Motocicleta de cualquier cilindrada', 'fa-motorcycle', 1),
        ('Auto', 'auto', 'Sedan, hatchback, coupe', 'fa-car', 2),
        ('SUV', 'suv', 'Crossover, todoterreno', 'fa-truck', 3),
        ('Pickup/Camioneta', 'pickup', 'Pickup mediana y grande', 'fa-truck-pickup', 4),
        ('Furgon', 'furgon', 'Furgoneta de carga cerrada', 'fa-van-shuttle', 5),
        ('Van/Minivan', 'van', 'Vehiculo de pasajeros multi-fila', 'fa-van', 6),
        ('Cuatrimoto', 'cuatrimoto', 'ATV recreativo o utilitario', 'fa-motorcycle', 7),
        ('Jet Ski', 'jetski', 'Moto acuatica personal', 'fa-water', 8),
        ('Lancha/Bote', 'lancha', 'Embarcacion menor, lancha deportiva', 'fa-ship', 9),
        ('Camion', 'camion', 'Camion liviano y mediano', 'fa-truck', 10),
    ]
    tv_dict = {}
    for nombre, slug, desc, icono, orden in tipos_data:
        tv = TipoVehiculo(nombre=nombre, slug=slug, descripcion=desc, icono=icono, orden=orden)
        db.session.add(tv)
        tv_dict[slug] = tv
    db.session.flush()

    # --- Niveles de Suciedad ---
    niveles_data = [
        ('Normal', 'Suciedad leve, polvo superficial, uso urbano', 1),
        ('Alta', 'Barro visible, suciedad acumulada', 2),
        ('Extrema', 'Barro abundante, grasa, arena, tierra de camino rural', 3),
    ]
    nv_dict = {}
    for nombre, desc, orden in niveles_data:
        n = NivelSuciedad(nombre=nombre, descripcion=desc, orden=orden)
        db.session.add(n)
        nv_dict[nombre.lower()] = n
    db.session.flush()

    # --- Estados de Reserva ---
    estados_data = [
        ('Pendiente', '#6c757d', 1, False, False),
        ('Confirmada', '#0d6efd', 2, False, False),
        ('Recibida', '#198754', 3, False, False),
        ('En Proceso', '#fd7e14', 4, False, False),
        ('Lista', '#0dcaf0', 5, False, False),
        ('Entregada', '#198754', 6, True, False),
        ('Cancelada', '#dc3545', 7, True, True),
    ]
    for nombre, color, orden, terminal, cancelacion in estados_data:
        db.session.add(EstadoReserva(
            nombre=nombre, color_badge=color, orden=orden,
            es_terminal=terminal, es_cancelacion=cancelacion,
        ))
    db.session.flush()

    # --- Categorias de Servicio ---
    cats_serv_data = [
        ('Lavado', 'lavado', 1),
        ('Detallado', 'detallado', 2),
        ('Tratamiento', 'tratamiento', 3),
        ('Especial', 'especial', 4),
        ('Adicional', 'adicional', 5),
        ('Paquete', 'paquete', 6),
    ]
    cat_dict = {}
    for nombre, slug, orden in cats_serv_data:
        c = CategoriaServicio(nombre=nombre, slug=slug, orden=orden)
        db.session.add(c)
        cat_dict[slug] = c
    db.session.flush()

    # --- Servicios Base ---
    servicios_base = [
        ('Lavado Exterior', 'lavado-exterior', 'Lavado exterior con shampoo neutro, secado y neblinado de neumaticos', 'base', cat_dict['lavado'].id),
        ('Lavado Interior', 'lavado-interior', 'Lavado interior, aspirado, limpieza de plasticos y vidrios', 'base', cat_dict['lavado'].id),
        ('Lavado Completo', 'lavado-completo', 'Lavado exterior + interior completo', 'base', cat_dict['lavado'].id),
        ('Detallado Interior', 'detallado-interior', 'Detallado interior profundo: tapizados, cueros, alfombras, techo', 'base', cat_dict['detallado'].id),
        ('Detallado Exterior', 'detallado-exterior', 'Correccion de pintura, pulido, sellado', 'base', cat_dict['detallado'].id),
        ('Detallado Completo', 'detallado-completo', 'Detallado interior + exterior completo', 'base', cat_dict['detallado'].id),
        ('Pulido', 'pulido', 'Pulido mecanico con correccion de pintura', 'base', cat_dict['tratamiento'].id),
        ('Tratamiento Ceramico', 'tratamiento-ceramico', 'Aplicacion de recubrimiento ceramico 9H', 'base', cat_dict['tratamiento'].id),
        ('Tratamiento Acrilico', 'tratamiento-acrilico', 'Sellador acrilico de alta duracion', 'base', cat_dict['tratamiento'].id),
        ('Lavado de Motor', 'lavado-motor', 'Lavado y desengrase de motor', 'base', cat_dict['especial'].id),
    ]

    svc_dict = {}
    for nombre, slug, desc, tipo, cat_id in servicios_base:
        s = Servicio(
            nombre=nombre, slug=slug, descripcion=desc,
            tipo=tipo, categoria_servicio_id=cat_id,
            requiere_inspeccion_previa=('Ceramico' in nombre or 'Pulido' in nombre),
            requiere_varios_dias=('Ceramico' in nombre),
            dias_bloqueo=2 if 'Ceramico' in nombre else None,
        )
        db.session.add(s)
        svc_dict[slug] = s
    db.session.flush()

    # --- Servicios Adicionales ---
    adicionales_data = [
        ('Desinfeccion con Ozono', 'desinfeccion-ozono', 'Eliminacion de olores y bacterias con ozono'),
        ('Restauracion de Faros', 'restauracion-faros', 'Pulido y sellado de faros opacos'),
        ('Limpieza de Tapizado Profunda', 'limpieza-tapizado', 'Extraccion profunda de suciedad de butacas y alfombras'),
        ('Aromatizante', 'aromatizante', 'Aplicacion de fragancia interior'),
        ('Retiro a Domicilio', 'retiro-domicilio', 'Buscar el vehiculo en ubicacion del cliente'),
        ('Entrega a Domicilio', 'entrega-domicilio', 'Llevar el vehiculo a ubicacion del cliente'),
    ]
    add_dict = {}
    for nombre, slug, desc in adicionales_data:
        s = Servicio(
            nombre=nombre, slug=slug, descripcion=desc,
            tipo='adicional', categoria_servicio_id=cat_dict['adicional'].id,
        )
        db.session.add(s)
        add_dict[slug] = s
    db.session.flush()

    # --- Paquetes ---
    paquetes_data = [
        ('Express', 'paquete-express', 'Lavado Exterior + Aromatizante', ['lavado-exterior'], 'lavado-exterior'),
        ('Full', 'paquete-full', 'Lavado Completo + Aromatizante', ['lavado-completo'], 'lavado-completo'),
        ('Premium', 'paquete-premium', 'Detallado Completo + Desinfeccion Ozono', ['detallado-completo'], 'detallado-completo'),
        ('Proteccion Total', 'paquete-proteccion-total', 'Pulido + Tratamiento Ceramico', ['pulido'], 'pulido'),
        ('Integral', 'paquete-integral', 'Detallado Completo + Lavado de Motor + Desinfeccion Ozono', ['detallado-completo'], 'detallado-completo'),
    ]
    pkg_dict = {}
    for nombre, slug, desc, componentes, principal_slug in paquetes_data:
        s = Servicio(
            nombre=nombre, slug=slug, descripcion=desc,
            tipo='paquete', categoria_servicio_id=cat_dict['paquete'].id,
            requiere_varios_dias=('Proteccion' in nombre),
            dias_bloqueo=2 if 'Proteccion' in nombre else None,
        )
        db.session.add(s)
        pkg_dict[slug] = s
    db.session.flush()

    # --- Precios y Duraciones (matriz simplificada) ---
    # Combinaciones: servicio x tipo_vehiculo x segmento x nivel_suciedad
    precios_config = {
        'lavado-exterior': {
            'moto':     {'pequenio': (15000, 20), 'mediano': (20000, 25)},
            'auto':     {'pequenio': (25000, 25), 'mediano': (30000, 30), 'grande': (35000, 35)},
            'suv':      {'mediano': (35000, 35), 'grande': (40000, 40)},
            'pickup':   {'mediano': (35000, 35), 'grande': (40000, 40)},
            'furgon':   {'mediano': (35000, 40), 'grande': (40000, 45)},
            'van':      {'mediano': (40000, 45), 'grande': (45000, 50)},
            'cuatrimoto': {'pequenio': (15000, 20)},
            'jetski':   {'pequenio': (15000, 20)},
            'lancha':   {'grande': (50000, 60), 'extra-grande': (60000, 75)},
            'camion':   {'grande': (50000, 60), 'extra-grande': (60000, 75)},
        },
        'lavado-interior': {
            'auto':     {'pequenio': (30000, 30), 'mediano': (35000, 35), 'grande': (40000, 45)},
            'suv':      {'mediano': (40000, 45), 'grande': (45000, 55)},
            'pickup':   {'mediano': (40000, 45), 'grande': (45000, 55)},
            'furgon':   {'mediano': (45000, 50), 'grande': (50000, 60)},
            'van':      {'mediano': (50000, 60), 'grande': (55000, 70)},
            'camion':   {'grande': (60000, 75), 'extra-grande': (70000, 90)},
        },
        'lavado-completo': {
            'moto':     {'pequenio': (25000, 30), 'mediano': (35000, 40)},
            'auto':     {'pequenio': (40000, 45), 'mediano': (50000, 55), 'grande': (60000, 70)},
            'suv':      {'mediano': (60000, 70), 'grande': (70000, 85)},
            'pickup':   {'mediano': (60000, 70), 'grande': (70000, 85)},
            'furgon':   {'mediano': (65000, 75), 'grande': (75000, 90)},
            'van':      {'mediano': (75000, 90), 'grande': (85000, 105)},
            'cuatrimoto': {'pequenio': (25000, 30)},
            'jetski':   {'pequenio': (25000, 30)},
            'lancha':   {'grande': (90000, 110), 'extra-grande': (110000, 140)},
            'camion':   {'grande': (90000, 110), 'extra-grande': (110000, 140)},
        },
        'detallado-interior': {
            'auto':     {'pequenio': (100000, 120), 'mediano': (130000, 150), 'grande': (160000, 190)},
            'suv':      {'mediano': (150000, 180), 'grande': (180000, 220)},
            'pickup':   {'mediano': (150000, 180), 'grande': (180000, 220)},
            'furgon':   {'mediano': (170000, 210), 'grande': (200000, 250)},
            'van':      {'mediano': (190000, 240), 'grande': (220000, 280)},
            'lancha':   {'grande': (250000, 300), 'extra-grande': (300000, 360)},
        },
        'detallado-exterior': {
            'auto':     {'pequenio': (120000, 150), 'mediano': (150000, 180), 'grande': (180000, 220)},
            'suv':      {'mediano': (170000, 210), 'grande': (200000, 250)},
            'pickup':   {'mediano': (170000, 210), 'grande': (200000, 250)},
            'furgon':   {'mediano': (190000, 230), 'grande': (220000, 270)},
            'van':      {'mediano': (210000, 260), 'grande': (240000, 300)},
            'lancha':   {'grande': (280000, 340), 'extra-grande': (330000, 400)},
        },
        'detallado-completo': {
            'auto':     {'pequenio': (180000, 240), 'mediano': (220000, 300), 'grande': (260000, 360)},
            'suv':      {'mediano': (250000, 340), 'grande': (290000, 400)},
            'pickup':   {'mediano': (250000, 340), 'grande': (290000, 400)},
            'furgon':   {'mediano': (280000, 380), 'grande': (320000, 440)},
            'van':      {'mediano': (310000, 420), 'grande': (350000, 480)},
            'lancha':   {'grande': (400000, 520), 'extra-grande': (460000, 600)},
        },
        'pulido': {
            'auto':     {'pequenio': (150000, 180), 'mediano': (200000, 240), 'grande': (250000, 300)},
            'suv':      {'mediano': (230000, 280), 'grande': (280000, 340)},
            'pickup':   {'mediano': (230000, 280), 'grande': (280000, 340)},
            'furgon':   {'mediano': (260000, 310), 'grande': (310000, 370)},
        },
        'tratamiento-ceramico': {
            'auto':     {'pequenio': (300000, 480), 'mediano': (400000, 600), 'grande': (500000, 720)},
            'suv':      {'mediano': (450000, 660), 'grande': (550000, 780)},
            'pickup':   {'mediano': (450000, 660), 'grande': (550000, 780)},
        },
        'tratamiento-acrilico': {
            'auto':     {'pequenio': (200000, 300), 'mediano': (260000, 360), 'grande': (320000, 420)},
            'suv':      {'mediano': (290000, 400), 'grande': (350000, 480)},
            'pickup':   {'mediano': (290000, 400), 'grande': (350000, 480)},
        },
        'lavado-motor': {
            'auto':     {'pequenio': (30000, 30), 'mediano': (40000, 40), 'grande': (50000, 50)},
            'suv':      {'mediano': (50000, 50), 'grande': (60000, 60)},
            'pickup':   {'mediano': (50000, 50), 'grande': (60000, 60)},
            'camion':   {'grande': (80000, 90), 'extra-grande': (100000, 120)},
        },
        'desinfeccion-ozono': {
            'auto': {'pequenio': (15000, 15), 'mediano': (15000, 15), 'grande': (15000, 15)},
            'suv':  {'mediano': (15000, 15), 'grande': (15000, 15)},
            'pickup': {'mediano': (15000, 15), 'grande': (15000, 15)},
            'van':  {'mediano': (20000, 20), 'grande': (20000, 20)},
        },
        'restauracion-faros': {
            'auto':     {'pequenio': (25000, 30), 'mediano': (25000, 30), 'grande': (25000, 30)},
            'suv':      {'mediano': (30000, 35), 'grande': (30000, 35)},
            'pickup':   {'mediano': (30000, 35), 'grande': (30000, 35)},
        },
        'limpieza-tapizado': {
            'auto':     {'pequenio': (35000, 40), 'mediano': (40000, 45), 'grande': (45000, 55)},
            'suv':      {'mediano': (45000, 55), 'grande': (50000, 65)},
            'pickup':   {'mediano': (45000, 55), 'grande': (50000, 65)},
            'van':      {'mediano': (55000, 70), 'grande': (60000, 80)},
        },
        'retiro-domicilio': {
            'auto':     {'pequenio': (15000, 0), 'mediano': (15000, 0), 'grande': (15000, 0)},
            'suv':      {'mediano': (20000, 0), 'grande': (20000, 0)},
            'pickup':   {'mediano': (20000, 0), 'grande': (20000, 0)},
            'van':      {'mediano': (25000, 0), 'grande': (25000, 0)},
        },
        'entrega-domicilio': {
            'auto':     {'pequenio': (15000, 0), 'mediano': (15000, 0), 'grande': (15000, 0)},
            'suv':      {'mediano': (20000, 0), 'grande': (20000, 0)},
            'pickup':   {'mediano': (20000, 0), 'grande': (20000, 0)},
            'van':      {'mediano': (25000, 0), 'grande': (25000, 0)},
        },
        'paquete-express': {
            'auto':     {'pequenio': (35000, 30), 'mediano': (40000, 35)},
            'suv':      {'mediano': (45000, 40)},
            'pickup':   {'mediano': (45000, 40)},
        },
        'paquete-full': {
            'auto':     {'pequenio': (55000, 50), 'mediano': (65000, 60), 'grande': (75000, 75)},
            'suv':      {'mediano': (75000, 75), 'grande': (85000, 90)},
            'pickup':   {'mediano': (75000, 75), 'grande': (85000, 90)},
        },
        'paquete-premium': {
            'auto':     {'pequenio': (190000, 255), 'mediano': (230000, 315), 'grande': (270000, 375)},
            'suv':      {'mediano': (260000, 355), 'grande': (300000, 415)},
            'pickup':   {'mediano': (260000, 355), 'grande': (300000, 415)},
        },
        'paquete-proteccion-total': {
            'auto':     {'pequenio': (400000, 660), 'mediano': (500000, 840), 'grande': (600000, 1020)},
            'suv':      {'mediano': (550000, 940), 'grande': (650000, 1120)},
            'pickup':   {'mediano': (550000, 940), 'grande': (650000, 1120)},
        },
        'paquete-integral': {
            'auto':     {'pequenio': (210000, 285), 'mediano': (260000, 355), 'grande': (310000, 425)},
            'suv':      {'mediano': (300000, 405), 'grande': (350000, 475)},
            'pickup':   {'mediano': (300000, 405), 'grande': (350000, 475)},
        },
    }

    # Multiplicadores de suciedad para cada nivel
    suciedad_multiplicadores = {
        'normal': {'precio': 1.0, 'duracion': 1.0},
        'alta': {'precio': 1.3, 'duracion': 1.3},
        'extrema': {'precio': 1.6, 'duracion': 1.6},
    }

    for svc_slug, tipos in precios_config.items():
        svc = svc_dict.get(svc_slug) or add_dict.get(svc_slug) or pkg_dict.get(svc_slug)
        if not svc:
            continue
        for tv_slug, segmentos in tipos.items():
            tv = tv_dict.get(tv_slug)
            if not tv:
                continue
            for seg_slug, (precio_base, duracion_base) in segmentos.items():
                seg = seg_dict.get(seg_slug)
                if not seg:
                    continue
                for nv_name, mult in suciedad_multiplicadores.items():
                    nv = nv_dict.get(nv_name)
                    if not nv:
                        continue
                    precio = int(precio_base * mult['precio'])
                    duracion = max(1, int(duracion_base * mult['duracion']))
                    db.session.add(PrecioServicio(
                        servicio_id=svc.id,
                        tipo_vehiculo_id=tv.id,
                        segmento_id=seg.id,
                        nivel_suciedad_id=nv.id,
                        precio=precio,
                        duracion_minutos=duracion,
                    ))
    db.session.flush()

    # --- Compatibilidades Servicio-Tipo de Vehiculo ---
    for svc_slug, tipos in precios_config.items():
        svc = svc_dict.get(svc_slug) or add_dict.get(svc_slug) or pkg_dict.get(svc_slug)
        if not svc:
            continue
        for tv_slug in tipos:
            tv = tv_dict.get(tv_slug)
            if not tv:
                continue
            exists = ServicioTipoVehiculo.query.filter_by(
                servicio_id=svc.id, tipo_vehiculo_id=tv.id
            ).first()
            if not exists:
                db.session.add(ServicioTipoVehiculo(
                    servicio_id=svc.id, tipo_vehiculo_id=tv.id
                ))
    db.session.flush()

    # --- Tipos de Box ---
    tipos_box_data = [
        ('Estandar', 'Box para autos, SUVs y pickups'),
        ('Grande', 'Box para vans, furgones y camiones'),
        ('Moto', 'Box para motos y cuatrimotos'),
        ('Acuatico', 'Box con desague para jet skis y lanchas'),
        ('Exterior', 'Box al aire libre para lavados rapidos'),
    ]
    tb_dict = {}
    for nombre, desc in tipos_box_data:
        tb = TipoBox(nombre=nombre, descripcion=desc)
        db.session.add(tb)
        tb_dict[nombre.lower()] = tb
    db.session.flush()

    # --- Boxes ---
    boxes_crear = [
        ('Box 1', 'estandar', 1),
        ('Box 2', 'estandar', 2),
        ('Box 3', 'grande', 3),
        ('Box 4', 'moto', 4),
    ]
    for nombre, tb_nombre, orden in boxes_crear:
        db.session.add(Box(
            tipo_box_id=tb_dict[tb_nombre].id,
            nombre=nombre, activo=True, orden=orden,
        ))

    # --- Horarios (Lunes a Sabado, 07:00 a 18:00) ---
    for dia in range(1, 7):
        db.session.add(Horario(
            dia_semana=dia, hora_inicio=time(7, 0), hora_fin=time(18, 0),
            activo=True,
        ))

    # --- Usuario Admin ---
    admin_existente = Usuario.query.filter_by(email='admin@exclusiveautodetail.com').first()
    if not admin_existente:
        admin = Usuario(
            nombre='Administrador', apellido='Sistema',
            email='admin@exclusiveautodetail.com', rol='admin', activo=True,
        )
        admin.set_password('Admin1234!')
        db.session.add(admin)
    else:
        print("Admin ya existe, omitiendo creacion.")

    # --- Galeria (placeholder) ---
    galeria_cats = [
        'Antes y Despues', 'Resultado Pulido', 'Revestimiento Ceramico',
        'Detalle Interior', 'Lavado Profundo', 'Brillo Final',
    ]
    _webp_placeholders = [
        '/static/img/galeria/galeria_8fff38584b.webp',
        '/static/img/galeria/galeria_169b69de2a.webp',
        '/static/img/galeria/galeria_412ee87fc8.webp',
    ]
    for orden, cat_nombre in enumerate(galeria_cats, start=1):
        gc = GaleriaCategoria(nombre=cat_nombre, orden=orden, activo=True)
        db.session.add(gc)
        db.session.flush()
        db.session.add(Galeria(
            categoria_id=gc.id,
            titulo=cat_nombre,
            url_imagen=_webp_placeholders[(orden - 1) % len(_webp_placeholders)],
            url_thumb=_webp_placeholders[(orden - 1) % len(_webp_placeholders)],
            orden=1, activo=True,
        ))

    # --- Catalogo de Marcas y Modelos (resumido) ---
    import re
    marcas_modelos = {
        'Toyota': {'pais': 'Japon', 'modelos': [
            'Corolla', 'Hilux', 'Yaris', 'RAV4', 'Camry', 'Fortuner',
            'Land Cruiser', 'Etios', 'Hiace', 'Prius',
        ]},
        'Hyundai': {'pais': 'Corea del Sur', 'modelos': [
            'HB20', 'Creta', 'Tucson', 'Santa Fe', 'i30', 'Elantra',
        ]},
        'Kia': {'pais': 'Corea del Sur', 'modelos': [
            'Picanto', 'Rio', 'Sportage', 'Sorento', 'Carnival',
        ]},
        'Chevrolet': {'pais': 'Estados Unidos', 'modelos': [
            'Onix', 'Tracker', 'S10', 'Spin', 'Cruze',
        ]},
        'Volkswagen': {'pais': 'Alemania', 'modelos': [
            'Gol', 'Polo', 'Virtus', 'Nivus', 'T-Cross', 'Amarok',
        ]},
        'Ford': {'pais': 'Estados Unidos', 'modelos': [
            'Fiesta', 'Focus', 'Ranger', 'Bronco', 'Mustang',
        ]},
        'Nissan': {'pais': 'Japon', 'modelos': [
            'March', 'Versa', 'Kicks', 'Frontier', 'X-Trail',
        ]},
        'Honda': {'pais': 'Japon', 'modelos': [
            'Civic', 'City', 'HR-V', 'CR-V', 'Fit',
        ]},
        'Fiat': {'pais': 'Italia', 'modelos': [
            'Mobi', 'Argo', 'Cronos', 'Strada', 'Toro',
        ]},
        'Renault': {'pais': 'Francia', 'modelos': [
            'Kwid', 'Sandero', 'Duster', 'Oroch', 'Logan',
        ]},
    }

    marcas_dict = {}
    for nombre_marca, data in marcas_modelos.items():
        slug = re.sub(r'[^a-z0-9]+', '-', nombre_marca.lower()).strip('-')
        m = Marca(nombre=nombre_marca, slug=slug, pais_origen=data['pais'], activo=True)
        db.session.add(m)
        db.session.flush()
        marcas_dict[nombre_marca] = m
        for nombre_modelo in data['modelos']:
            modelo_slug = re.sub(r'[^a-z0-9]+', '-', nombre_modelo.lower()).strip('-')
            mv = ModeloVehiculo(
                marca_id=m.id,
                nombre=nombre_modelo,
                slug=modelo_slug,
                tipo_vehiculo_id=tv_dict['auto'].id,
                segmento_id=seg_dict['mediano'].id,
                activo=True,
            )
            db.session.add(mv)

    db.session.commit()
    print("Seed completado.")
    print(f"  - {Segmento.query.count()} segmentos")
    print(f"  - {TipoVehiculo.query.count()} tipos de vehiculo")
    print(f"  - {NivelSuciedad.query.count()} niveles de suciedad")
    print(f"  - {CategoriaServicio.query.count()} categorias de servicio")
    print(f"  - {Servicio.query.count()} servicios")
    print(f"  - {PrecioServicio.query.count()} registros de precio/duracion")
    print(f"  - {TipoBox.query.count()} tipos de box")
    print(f"  - {Box.query.count()} boxes")
    print(f"  - {Horario.query.count()} horarios")
    print(f"  - {EstadoReserva.query.count()} estados de reserva")
    print(f"  - {Usuario.query.count()} usuarios (admin: admin@exclusiveautodetail.com / Admin1234!)")
    print(f"  - {Marca.query.count()} marcas")
    print(f"  - {ModeloVehiculo.query.count()} modelos")