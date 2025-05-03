from django.db import models

# Create your models here.
from django.db import models

class DocumentImage(models.Model):
    image = models.ImageField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagen {self.id} subida el {self.uploaded_at}"

class DocumentData(models.Model):
    document_image = models.ForeignKey(DocumentImage, on_delete=models.CASCADE) 
    document_type = models.CharField(max_length=100)
    document_number = models.CharField(max_length=100)
    first_names = models.CharField(max_length=100)
    last_names = models.CharField(max_length=100)
    birth_date = models.DateField()
    nationality = models.CharField(max_length=100)
    birth_place = models.CharField(max_length=100)
    expiration_date = models.DateField()

    def __str__(self):
        return f"Documento {self.document_number}"
    
    