import re
from unidecode import unidecode
from typing import List, Union
from datetime import datetime

# Constantes mejoradas
MINUSCULA_EXCEPTIONS = {'de', 'del', 'la', 'las', 'y', 'a', 'el', 'los', 'las', 'mc', 'mac', 'van', 'von'}
OCR_CORRECTIONS = {
    'O': '0', 'Q': '0', 'I': '1', 'l': '1', '|': '1',
    'Z': '2', 'S': '5', 'B': '8', 'G': '6', '¢': 'c',
    '€': 'c', '¥': 'y', '´': '', '`': '', '~': ''
}

def basic_cleaning(text: Union[str, List[str]]) -> Union[str, List[str]]:
    """
    Limpieza básica mejorada: maneja tanto strings como listas,
    corrige errores comunes de OCR y normaliza el texto.
    
    Args:
        text: Puede ser un string o lista de strings a limpiar
        
    Returns:
        Mismo tipo que el input (str o List[str]) pero limpio
    """
    is_list = isinstance(text, list)
    inputs = text if is_list else [text]
    cleaned = []
    
    for item in inputs:
        if not isinstance(item, str):
            item = str(item)
            
        # Correcciones específicas para OCR primero
        for wrong, right in OCR_CORRECTIONS.items():
            item = item.replace(wrong, right)
            
        # Eliminar caracteres especiales pero mantener ñ/Ñ y tildes
        item = re.sub(r'[^\wáéíóúÁÉÍÓÚñÑüÜ\s]', '', item)
        
        # Normalizar espacios
        item = ' '.join(item.split())
        
        cleaned.append(item)
    
    return cleaned if is_list else cleaned[0]

def clean(text: str) -> str:
    """
    Limpieza avanzada para texto de documentos de identidad.
    Conserva formatos importantes como fechas y números de documento.
    """
    if not text:
        return ""
    
    # Corrección de patrones comunes en documentos
    text = re.sub(r'(\d)\s*([/-])\s*(\d)', r'\1\2\3', text)  # Fechas: 10 / 07 / 2023 → 10/07/2023
    text = re.sub(r'([A-Z])\s+([A-Z])', r'\1\2', text)  # Siglas: D N I → DNI
    
    # Eliminar espacios duplicados pero conservar saltos de línea si son importantes
    text = ' '.join(text.split())
    
    return text.strip()

def remove_noise(text_list: List[str], min_length: int = 2) -> List[str]:
    """
    Filtrado mejorado de ruido en OCR.
    Elimina palabras cortas pero conserva siglas importantes.
    """
    filtered = []
    for text in text_list:
        # Conservar siglas aunque sean cortas (DNI, CI, etc.)
        if text.isupper() and len(text) >= 2:
            filtered.append(text)
        elif len(text) >= min_length:
            filtered.append(text)
    return filtered

def normalize_name(name: str) -> str:
    """
    Normalización avanzada de nombres y apellidos.
    Maneja casos especiales como "Maria Del Carmen", "Juan De Dios", etc.
    """
    if not name:
        return ""
    
    # Primera pasada: normalizar espacios y casos mixtos
    name = ' '.join(name.split())
    words = name.split()
    
    normalized = []
    for i, word in enumerate(words):
        lower_word = word.lower()
        
        # Manejar prefijos compuestos (del, de la, etc.)
        if lower_word in MINUSCULA_EXCEPTIONS:
            # Verificar si es parte de un prefijo compuesto (ej. "de la")
            if (i > 0 and words[i-1].lower() in {'de', 'a'}):
                normalized.append(word.lower())
            else:
                normalized.append(word.capitalize() if len(word) > 2 else word.lower())
        else:
            # Capitalización inteligente para nombres compuestos (ej. McDonald)
            if any(word.lower().startswith(prefix) for prefix in {'mc', 'mac', 'van', 'von'}):
                if len(word) > 2:
                    normalized.append(word[:2].capitalize() + word[2:].lower())
                else:
                    normalized.append(word.capitalize())
            else:
                normalized.append(word.capitalize())
    
    # Unir y corregir casos especiales
    result = ' '.join(normalized)
    
    # Corregir casos como "Maria Del Carmen" → "Maria del Carmen"
    for exception in MINUSCULA_EXCEPTIONS:
        result = re.sub(
            rf'\b{exception.capitalize()}\b',
            exception.lower(),
            result
        )
    
    return result

def extract_document_number(text: str) -> str:
    """
    Extrae número de documento de un texto, manejando diferentes formatos.
    """
    # Busca patrones como: 1.234.567-8 o 12345678 o 12.345.678
    matches = re.findall(r'[\d]{1,3}(?:\.?[\d]{3}){2}-?[\d]?', text)
    if matches:
        # Eliminar puntos y guiones
        return matches[0].replace('.', '').replace('-', '')
    return ""

def normalize_date(date_str: str) -> str:
    """
    Normaliza diferentes formatos de fecha a YYYY-MM-DD.
    Maneja formatos comunes en documentos de identidad con tolerancia a errores de OCR.
    
    Args:
        date_str: String con la fecha en cualquier formato (dd/mm/yyyy, dd-mm-yy, etc.)
        
    Returns:
        str: Fecha en formato YYYY-MM-DD o cadena vacía si no se puede parsear
        
    Ejemplos:
        >>> normalize_date("10/05/1990")
        '1990-05-10'
        >>> normalize_date("15-03-85")
        '1985-03-15'
        >>> normalize_date("3 de abril de 2020")
        '2020-04-03'
    """
    if not date_str or not isinstance(date_str, str):
        return ""
    
    # Limpieza inicial del string
    date_str = date_str.lower().strip()
    date_str = re.sub(r'[^\wáéíóúñ/\\-]', ' ', date_str)  # Eliminar caracteres raros
    date_str = re.sub(r'\s+', ' ', date_str).strip()
    
    # Correcciones comunes de OCR
    ocr_corrections = {
        'o': '0', 'q': '0', 'i': '1', 'l': '1', 's': '5', 
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    for wrong, right in ocr_corrections.items():
        date_str = date_str.replace(wrong, right)
    
    # Patrones de fecha con orden de prioridad
    patterns = [
        # Formatos numéricos
        (r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', lambda d, m, y: (d, m, y)),  # dd/mm/yyyy o dd-mm-yyyy
        (r'(\d{2})(\d{2})(\d{2,4})', lambda d, m, y: (d, m, y)),               # ddmmyyyy
        (r'(\d{4})[/-](\d{2})[/-](\d{2})', lambda y, m, d: (d, m, y)),        # yyyy-mm-dd
        
        # Formatos con texto
        (r'(\d{1,2})\s*(?:de)?\s*(\d{1,2}|[a-z]{3,})\s*(?:de)?\s*(\d{4})',    # 10 de mayo de 1990
            lambda d, m, y: (d, str(m).zfill(2), y)),
        
        # Formatos sin año (asume año actual)
        (r'(\d{1,2})[/-](\d{1,2})', lambda d, m: (d, m, str(datetime.now().year))),
    ]
    
    for pattern, handler in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                groups = match.groups()
                day, month, year = handler(*groups) if len(groups) >= 3 else (*handler(*groups), str(datetime.now().year))
                
                # Asegurar 2 dígitos para día y mes
                day = day.zfill(2)
                month = month.zfill(2)
                
                # Manejar años de 2 dígitos
                if len(year) == 2:
                    current_year = datetime.now().year
                    century = current_year // 100
                    year = f"{century}{year}" if int(year) <= (current_year % 100) else f"{century-1}{year}"
                
                # Validar valores
                day_int, month_int, year_int = int(day), int(month), int(year)
                if 1 <= month_int <= 12 and 1 <= day_int <= 31 and year_int > 1900:
                    # Construir fecha y validar (por ejemplo, no 31 de abril)
                    try:
                        parsed_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
                        return parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
            except (ValueError, TypeError):
                continue
    
    # Si no se pudo parsear, devolver string vacío
    return ""