import os
import docx2txt
from pdfminer.high_level import extract_text

def extract_content(file_path):
    # Obtenir l'extension du fichier
    file_extension = os.path.splitext(file_path)[1].lower()
    
    # Lecture du contenu en fonction de l'extension du fichier
    if file_extension == '.pdf':
        # Si le fichier est un PDF
        content = extract_text(file_path)
    elif file_extension == '.docx':
        # Si le fichier est un document Word (DOCX)
        content = docx2txt.process(file_path)
    else:
        # Pour d'autres types de fichiers, vous pouvez ajouter d'autres méthodes d'extraction ici
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    
    return content
