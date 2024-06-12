import io
from django.template.loader import get_template
from django.core.files.uploadedfile import InMemoryUploadedFile
from xhtml2pdf import pisa
from common.models import File

def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if pdf.err:
        return None
    return result.getvalue()

def save_pdf_to_file(pdf_content, filename):
    buffer = io.BytesIO(pdf_content)
    file_instance = InMemoryUploadedFile(
        buffer, None, filename, 'application/pdf', len(pdf_content), None)
    file_obj = File(name=filename[0:250], description=filename, file=file_instance)
    file_obj.save()
    return file_obj