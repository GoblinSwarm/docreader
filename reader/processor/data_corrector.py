import spacy
import re
from datetime import datetime
from typing import Dict

# Carga del modelo NER (asegúrate de tenerlo descargado con spacy)
nlp = spacy.load("es_core_news_sm")  # O el modelo adecuado para tu idioma

class DataCorrector:
    def __init__(self):
        # Inicialización si es necesario
        pass

    def correct(self, raw_text: str) -> Dict[str, str]:
        """
        Procesa el texto crudo y devuelve un diccionario con los datos corregidos.
        """
        # Primero aplicamos NER para identificar entidades
        doc = nlp(raw_text)
        
        # Extracción básica con NER
        entities = {
            "PER": [],  # Nombres de personas
            "LOC": [],  # Lugares (nacionalidad, lugar de nacimiento)
            "DATE": [],  # Fechas
            "ORG": [],  # Organizaciones (a veces aparece en documentos)
        }
        
        for ent in doc.ents:
            if ent.label_ in entities:
                entities[ent.label_].append(ent.text)
        
        # Procesamiento estructurado
        result = {
            "document_type": self._extract_document_type(raw_text),
            "document_number": self._extract_document_number(raw_text),
            "first_names": self._extract_names(entities["PER"]),
            "last_names": self._extract_last_names(entities["PER"]),
            "birth_date": self._extract_birth_date(raw_text, entities["DATE"]),
            "nationality": self._extract_nationality(raw_text, entities["LOC"]),
            "birth_place": self._extract_birth_place(raw_text, entities["LOC"]),
            "expiration_date": self._extract_expiration_date(raw_text, entities["DATE"]),
        }
        
        # Filtra solo los campos que no sean None
        return {k: v for k, v in result.items() if v is not None}

    def _extract_document_type(self, raw_text: str) -> str:
        """
        Extrae el tipo de documento del texto.
        Ejemplo: 'Cédula de Identidad', 'Pasaporte', etc.
        """
        document_types = ["Cédula", "Pasaporte", "Licencia", "DNI", "Tarjeta de Identidad"]
        
        for doc_type in document_types:
            if doc_type.lower() in raw_text.lower():
                return doc_type
        
        return None

    def _extract_names(self, names: list) -> str:
        """
        Extrae los primeros nombres de la lista de entidades 'PER'.
        """
        if names:
            return names[0]
        
        return None

    def _extract_last_names(self, names: list) -> str:
        """
        Extrae los apellidos de la lista de entidades 'PER'.
        """
        if len(names) > 1:
            return " ".join(names[1:])
        
        return None

    def _extract_birth_date(self, raw_text: str, dates: list) -> str:
        """
        Extrae la fecha de nacimiento del texto.
        """
        if dates:
            return dates[0]
        
        return None

    def _extract_nationality(self, raw_text: str, locations: list) -> str:
        """
        Extrae la nacionalidad del texto.
        """
        nationalities = [
                        "Afganistán", "Albania", "Argelia", "Andorra", "Angola", "Antigua y Barbuda", "Argentina", "Armenia", "Australia", "Austria", 
                        "Azerbaiyán", "Bahamas", "Bahréin", "Bangladesh", "Barbados", "Belice", "Benín", "Bután", "Bolivia", "Bosnia y Herzegovina", 
                        "Botsuana", "Brasil", "Brunéi", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Camboya", "Camerún", "Canadá", "Catar", 
                        "Chile", "China", "Chipre", "Colombia", "Comoras", "Congo (República del Congo)", "Corea del Norte", "Corea del Sur", "Costa de Marfil", 
                        "Costa Rica", "Croacia", "Cuba", "Curazao", "Chipre", "Dinamarca", "Dominica", "Ecuador", "Egipto", "El Salvador", "Emiratos Árabes Unidos", 
                        "Eritrea", "Eslovaquia", "Eslovenia", "España", "Estados Unidos", "Estonia", "Eswatini", "Etiopía", "Fiji", "Filipinas", "Finlandia", 
                        "Francia", "Gabón", "Gambia", "Georgia", "Ghana", "Grecia", "Granada", "Guatemala", "Guinea", "Guinea-Bisáu", "Guinea Ecuatorial", "Guyana", 
                        "Haití", "Honduras", "Hungría", "India", "Indonesia", "Irán", "Irak", "Irlanda", "Islandia", "Israel", "Italia", "Jamaica", "Japón", 
                        "Jordania", "Kazajistán", "Kenia", "Kirguistán", "Kiribati", "Kuwait", "Laos", "Lesoto", "Letonia", "Líbano", "Liberia", "Libia", 
                        "Liechtenstein", "Lituania", "Luxemburgo", "Macedonia del Norte", "Madagascar", "Malawi", "Malasia", "Maldivas", "Mali", "Malta", 
                        "Marruecos", "Mauricio", "Mauritania", "México", "Micronesia", "Mónaco", "Mongolia", "Mozambique", "Namibia", "Nauru", "Nepal", "Nicaragua", 
                        "Níger", "Nigeria", "Noruega", "Nueva Zelanda", "Omán", "Países Bajos", "Pakistán", "Palau", "Panamá", "Papúa Nueva Guinea", "Paraguay", 
                        "Perú", "Polonia", "Portugal", "Reino Unido", "República Checa", "República del Congo", "República Dominicana", "Ruanda", "Rumanía", "Rusia", 
                        "Samoa", "San Cristóbal y Nieves", "San Marino", "San Vicente y las Granadinas", "Santa Lucía", "Santo Tomé y Príncipe", "Senegal", "Serbia", 
                        "Seychelles", "Sierra Leona", "Singapur", "Siria", "Somalia", "Sri Lanka", "Sudáfrica", "Sudán", "Sudán del Sur", "Suecia", "Suiza", 
                        "Surinam", "Siria", "Tailandia", "Tanzania", "Togo", "Tokelau", "Tonga", "Trinidad y Tobago", "Túnez", "Turkmenistán", "Turquía", 
                        "Tuvalu", "Uganda", "Ucrania", "Uruguay", "Uzbekistán", "Vanuatu", "Vaticano", "Venezuela", "Vietnam", "Yemen", "Yibuti", "Zambia", "Zimbabue"
                    ]
        
        for location in locations:
            for nationality in nationalities:
                if nationality.lower() in location.lower():
                    return nationality
        
        return None

    def _extract_birth_place(self, raw_text: str, locations: list) -> str:
        """
        Extrae el lugar de nacimiento del texto.
        """
        if locations:
            return locations[0]
        
        return None

    def _extract_expiration_date(self, raw_text: str, dates: list) -> str:
        """
        Extrae la fecha de expiración del texto.
        """
        if dates:
            return dates[-1]
        
        return None

    def _extract_document_number(self, raw_text: str) -> str:
        """
        Extrae el número de documento del texto.
        """
        # Aquí se puede agregar lógica para extraer el número de documento, por ejemplo con una regex
        match = re.search(r'\d{7,8}', raw_text)  # Por ejemplo, 7 o 8 dígitos
        if match:
            return match.group(0)
        
        return None
    
def correct(text: str) -> Dict[str, str]:
    return DataCorrector().correct(text)
