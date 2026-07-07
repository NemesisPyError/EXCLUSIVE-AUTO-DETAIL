def serialize_vehiculo(tv):
    return {
        'id':          tv.id,
        'nombre':      tv.nombre,
        'slug':        tv.slug,
        'descripcion': tv.descripcion,
        'icono':       tv.icono,
        'orden':       tv.orden,
    }


def serialize_categoria(cs):
    return {
        'id':                 cs.id,
        'nombre':             cs.nombre,
        'slug':               cs.slug,
        'descripcion':        cs.descripcion,
        'icono':              cs.icono,
        'orden':              cs.orden,
        'usa_nivel_suciedad': cs.usa_nivel_suciedad,
        'permite_multidias':  cs.permite_multidias,
        'tiene_subtipos':     cs.tiene_subtipos,
    }


def serialize_lavado(tl):
    return {
        'id':                  tl.id,
        'nombre':              tl.nombre,
        'slug':                tl.slug,
        'descripcion':         tl.descripcion,
        'orden':               tl.orden,
        'es_cerrado':          tl.es_cerrado,
        'requiere_inspeccion': tl.requiere_inspeccion,
    }


def serialize_subtipo(st):
    return {
        'id':              st.id,
        'tipo_lavado_id':  st.tipo_lavado_id,
        'nombre':          st.nombre,
        'slug':            st.slug,
        'descripcion':     st.descripcion,
        'orden':           st.orden,
    }


def serialize_detallado(td):
    return {
        'id':          td.id,
        'nombre':      td.nombre,
        'slug':        td.slug,
        'descripcion': td.descripcion,
        'orden':       td.orden,
    }
