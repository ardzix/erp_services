import io
from django.template.loader import get_template
from django.core.files.uploadedfile import InMemoryUploadedFile
from xhtml2pdf import pisa
from common.models import File
from ..models import Invoice

def generate_invoice_pdf_for_instance(instance):
    # Use Django's template system to generate HTML for the PDF
    template = get_template('document/invoice.html')
    try:
        invoice = Invoice.objects.get(order=instance)
    except:
        return
    context = {
        'invoice': invoice,
        'items': instance.order_items.all()
    }
    html = template.render(context)
    
    # Convert the HTML to PDF
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    
    # Check if the conversion is successful
    if not pdf.err:
        
        buffer = io.BytesIO(result.getvalue())

        filename = f"Invoice_{invoice.id32}.pdf"
        # Create an InMemoryUploadedFile from the buffer
        in_memory_file = InMemoryUploadedFile(
            buffer,
            None,
            filename,
            'application/pdf',
            buffer.getbuffer().nbytes,
            None
        )

        # Save the PDF to a File instance
        file = File(name=filename, file=in_memory_file)
        file.save()
        
        # Associate the PDF with the Invoice's attachment field
        invoice.attachment = file
        invoice.save()
