from datetime import date, datetime

months_names={
    'July': 'Julio',
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April' : 'Abril',
    'May' : 'Mayo',
    'June' : 'Junio',
    'August' : 'Agosto',
    'September' : 'Septiembre',
    'Octuber' : 'Octubre',
    'November': 'Noviembre',
    'December' : 'December'
}
"""2025-07-03 -> 03 de Julio"""
def transform_date(payment_date):
    month = payment_date.strftime("%B")
    day = payment_date.day
    year = date.today().year
    readable_date = f"{day} de {months_names[month]} de {year}"
    return readable_date
