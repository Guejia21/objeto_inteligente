"""
Ejecutable: Leer Reloj RTC
Datastream: rtc_time
Action: read
"""

from machine import RTC
import time

# Inicializar RTC si no existe
if 'rtc' not in pins:
    pins['rtc'] = RTC()
    print("✅ RTC inicializado")

# Obtener datetime del RTC
# RTC.datetime() retorna: (year, month, day, weekday, hours, minutes, seconds, subseconds)
dt = pins['rtc'].datetime()

# Calcular timestamp Unix aproximado
def to_unix_timestamp(dt):
    """Convierte datetime RTC a timestamp Unix aproximado"""
    year, month, day, _, hour, minute, second, _ = dt
    
    # Días desde 1970-01-01
    days = (year - 1970) * 365
    days += (year - 1969) // 4  # Años bisiestos
    
    # Días del mes actual
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    days += sum(days_in_month[:month])
    days += day - 1
    
    # Convertir a segundos
    timestamp = days * 86400 + hour * 3600 + minute * 60 + second
    return timestamp

# Nombres de días de la semana
weekdays = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

# Formatear resultado
timestamp_value = to_unix_timestamp(dt)
readable_date = f"{dt[0]:04d}-{dt[1]:02d}-{dt[2]:02d}"
readable_time = f"{dt[4]:02d}:{dt[5]:02d}:{dt[6]:02d}"
readable_full = f"{readable_date} {readable_time}"
weekday_name = weekdays[dt[3]] if dt[3] < 7 else 'N/A'

# Resultado
result = {
    'success': True,
    'datastream_id': 'rtc_time',
    'action': 'read',
    'value': readable_full,  # Formato legible como valor principal
    'details': {
        'year': dt[0],
        'month': dt[1],
        'day': dt[2],
        'weekday': dt[3],
        'weekday_name': weekday_name,
        'hour': dt[4],
        'minute': dt[5],
        'second': dt[6],
        'subsecond': dt[7],
        'date': readable_date,
        'time': readable_time,
        'timestamp': timestamp_value
    },
    'message': f"Reloj: {weekday_name} {readable_full}"
}

print(f"RTC: {readable_full} ({weekday_name})")