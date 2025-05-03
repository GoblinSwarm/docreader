import base64, io
from PIL import Image
from django.shortcuts import render, redirect, get_object_or_404
from .models import DocumentImage, DocumentData
from django.http import HttpResponse
from datetime import datetime
from .processor import image_processing, ocr_reader, text_cleaner, data_corrector
from reader.processor.data_corrector import correct
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
# Create your views here.

def photo_capture_view(request):
    return render(request, 'reader/photo_capture.html')
    
def edit_data(request):
    document_id = request.session.get('document_id')
    extracted_data = request.session.get('extracted_data')

    if not document_id or not extracted_data:
        return redirect('photo_capture')

    document = DocumentImage.objects.get(id=document_id)

    if request.method == 'POST':
        # Si se presionó Guardar ➡️ guardar en la BD
        if 'save' in request.POST:
            data = {
                'document_type': request.POST.get('document_type'),
                'document_number': request.POST.get('document_number'),
                'first_names': request.POST.get('first_names'),
                'last_names': request.POST.get('last_names'),
                'birth_date': request.POST.get('birth_date'),
                'nationality': request.POST.get('nationality'),
                'birth_place': request.POST.get('birth_place'),
                'expiration_date': request.POST.get('expiration_date'),
                'document_image': document
            }
            # Guardar en tu modelo de datos (ajustá a tu modelo real)
            DocumentData.objects.create(**data)

            # ✅ limpiar sesión si querés
            del request.session['extracted_data']
            del request.session['document_id']

            return redirect('photo_capture')  # o a una página de éxito

    return render(request, 'reader/edit_data.html', {
        'document': document,
        'data': extracted_data
    })

def save_document_data(request):
    if request.method == 'POST':
        # Obtenemos la imagen relacionada
        document_id = request.POST.get('document_id')
        document_image = get_object_or_404(DocumentImage, id=document_id)

        # Parseo seguro de fechas
        birth_date_str = request.POST.get('birth_date')
        expiration_date_str = request.POST.get('expiration_date')

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d').date() if expiration_date_str else None
        except ValueError:
            return HttpResponse("Invalid date format.", status=400)

        # Guardamos el objeto DocumentData
        document_data = DocumentData.objects.create(
            document_image=document_image,
            document_type=request.POST.get('document_type'),
            document_number=request.POST.get('document_number'),
            first_names=request.POST.get('first_names'),
            last_names=request.POST.get('last_names'),
            birth_date=birth_date,
            nationality=request.POST.get('nationality'),
            birth_place=request.POST.get('birth_place'),
            expiration_date=expiration_date
        )

        return redirect('success') 

    else:
        return HttpResponse("Invalid request method.", status=405)
    
def success_view(request):
    return render(request, 'reader/success.html')

def error_view(request):
    return render(request, 'reader/error.html')

def upload_image(request):
    if request.method == 'POST' and 'captured_image' in request.POST:
        try:
            # Obtener la imagen en base64 desde la solicitud
            image_data = request.POST['captured_image']
            
            # Paso 1: Guardar la imagen ORIGINAL sin procesar
            # Convertir base64 a imagen PIL directamente
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1]
            image_file = ContentFile(base64.b64decode(imgstr), name=f'original_image.{ext}')
            
            # Guardar la imagen original en la base de datos
            document = DocumentImage.objects.create(image=image_file)
            request.session['document_id'] = document.id
            
            # Paso 2: Procesar la imagen para OCR
            processed_image = image_processing.process_base64_image(image_data)
            
            # Paso 3: Leer con OCR la imagen procesada
            raw_text = ocr_reader.read(processed_image)
            print(f"Texto OCR: {raw_text}")
            
            # Paso 4: Limpiar el texto
            cleaned_text = text_cleaner.basic_cleaning(raw_text)
            fully_cleaned_text = text_cleaner.clean(cleaned_text)
            
            # Paso 5: Corregir los datos
            corrector = data_corrector.DataCorrector()
            extracted_data = corrector.correct(fully_cleaned_text)

            # Guardar en sesión los datos extraídos
            request.session['extracted_data'] = extracted_data
            
            # Paso 6: Renderizar la página de edición con la imagen original y los datos extraídos
            return render(request, 'reader/edit_data.html', {
                'data': extracted_data,
                'document': document  # Esto contiene la imagen original
            })
            
        except Exception as e:
            print(f"Error completo: {str(e)}")
            return render(request, 'reader/error.html', {
                'error_message': f"Error al procesar el documento: {str(e)}"
            }, status=500)
    return render(request, 'reader/photo_capture.html')