from easyocr import Reader
import numpy as np

# Inicializar el lector una sola vez (mejor performance)
reader = Reader(['es'], gpu=False)  # Desactiva GPU si no está disponible

def read(image):
    """
    Recibe una imagen procesada (como matriz de OpenCV o archivo de imagen)
    y devuelve el texto detectado como un string unificado.
    
    Args:
        image: Puede ser una ruta de archivo o una matriz numpy (OpenCV)
    
    Returns:
        str: Texto detectado unificado
    """
    try:
        # Asegurarse que la imagen es compatible con EasyOCR
        if isinstance(image, str):
            # Es una ruta de archivo
            results = reader.readtext(image, detail=0)
        elif isinstance(image, np.ndarray):
            # Es una matriz de OpenCV
            results = reader.readtext(image, detail=0)
        else:
            raise ValueError("Formato de imagen no soportado")
        
        # Unificar todos los resultados en un solo string
        unified_text = ' '.join(results)
        
        # Limpieza básica
        unified_text = ' '.join(unified_text.split())  # Elimina espacios múltiples
        
        return unified_text
    
    except Exception as e:
        print(f"Error en OCR: {str(e)}")
        return ""