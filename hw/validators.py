import magic
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

ALLOWED_EXTENSIONS = [

    'py', 'cpp', 'c', 'h', 'hpp', 'cc', 'cxx',
    'java', 'cs', 'js', 'ts', 'jsx', 'tsx', 'pas',
    'pp', 'p', 'jl', 'ipynb', 'r', 'rb', 'php', 
    'go', 'rs', 'kt', 'kts', 'swift', 'scala',     
    'sh', 'bash', 'zsh', 'sql','html', 'css', 'scss',
    'json', 'xml', 'yaml', 'yml','txt', 'pdf', 'md',
    'zip', '7z', 'tar', 'gz', 'bz2', 'xz'
]

# 2. Povolené MIME typy
ALLOWED_MIME_TYPES = [
    'text/plain',
    'text/x-python',
    'text/x-c',
    'text/x-c++',
    'text/x-java-source',
    'text/x-pascal',
    'text/x-julia',
    'text/html',
    'text/css',
    'application/json',
    'application/x-ipynb+json',
    'application/pdf',
    'application/zip',
    'application/x-zip-compressed',
    'application/x-7z-compressed',
    'application/x-tar',
    'application/gzip',
    'application/octet-stream',  
]

def validate_file_type(file):
    file_sample = file.read(2048) # čtení bajtů v hlavičce
    file.seek(0) 

    # Zjištění reálného MIME typu
    mime_type = magic.from_buffer(file_sample, mime=True)

    if mime_type not in ALLOWED_MIME_TYPES and not mime_type.startswith('text/'):
        raise ValidationError(
            _("Nepovolený typ souboru (%s). Nahrajte prosím pouze zdrojové kódy, Jupyter notebooky, dokumenty nebo archivy.") % mime_type
        )

