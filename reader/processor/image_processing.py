import base64, os, cv2
import numpy as np
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def process2(image: np.ndarray):
    """
    Procesa una imagen ya cargada (matriz OpenCV), 
    no recibe path, recibe directamente la imagen.
    """

    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Aplicar filtro bilateral (reduce ruido pero mantiene bordes)
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)

    # Aumentar el contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(filtered)

    # Umbral adaptativo para mejorar las letras
    thresh = cv2.adaptiveThreshold(contrast, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    #Aca le mando la imagen en gris solamente para ir probando, lo otro es proceso bilateral y contraste
    return gray

def process_base64_image(image_data):
    """
    Decodifica la imagen base64, la guarda como archivo temporal 
    (opcional), y la procesa con OpenCV.
    """

    # Limpiar header "data:image/png;base64,..."
    format, imgstr = image_data.split(';base64,') 
    ext = format.split('/')[-1]  # png, jpg...

    # Guardar imagen temporal (opcional, para debugging o persistencia)
    file_name = f"captured_image.{ext}"
    file_path = default_storage.save('tmp/' + file_name, ContentFile(base64.b64decode(imgstr)))

    abs_path = os.path.abspath(file_path)
    print(f"Imagen guardada en: {abs_path}")

    # Leer imagen de forma robusta usando cv2.imdecode (evita errores de imread)
    file_bytes = np.frombuffer(base64.b64decode(imgstr), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError(f"No se pudo decodificar la imagen desde base64 en {abs_path}")
    
    print("Imagen leída correctamente con OpenCV")

    # Procesar la imagen con tus filtros
    processed = process(img)
    return processed

def process(image: np.ndarray, scale_factor=3.5):
    """
    Procesa una imagen ya cargada (matriz OpenCV),
    la escala a un tamaño más grande y luego la convierte a escala de grises.
    Este process es de prueba
    """

    # Escalar la imagen
    width = int(image.shape[1] * scale_factor)  # Calculamos el nuevo ancho
    height = int(image.shape[0] * scale_factor)  # Calculamos la nueva altura
    new_dim = (width, height)  # Dimensiones finales

    # Redimensionar la imagen
    scaled_image = cv2.resize(image, new_dim, interpolation=cv2.INTER_LINEAR)

    # Convertir la imagen escalada a escala de grises
    gray = cv2.cvtColor(scaled_image, cv2.COLOR_BGR2GRAY)

    return gray