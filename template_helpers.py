from datetime import datetime
from urllib.parse import quote
from services.whatsapp_service import normalize_phone


def register_template_helpers(app):

    @app.context_processor
    def inject_now():
        return {'now': datetime.now}

    @app.template_filter('thousandsep')
    def thousandsep(value):
        try:
            return f'{int(value):,}'.replace(',', '.')
        except (ValueError, TypeError):
            return value

    @app.template_filter('whatsapp_number')
    def whatsapp_number(texto):
        return normalize_phone(texto)

    @app.template_filter('urlencode')
    def urlencode_filter(texto):
        return quote(str(texto), safe='') if texto else ''
