import io
from django.template.loader import get_template
from django.core.files.uploadedfile import InMemoryUploadedFile
from xhtml2pdf import pisa
from common.models import File
from libs.utils import get_config_value
from ..models import Invoice

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

def get_tenant_info():
    return {
        'name': get_config_value('tenant_name', 'BNK ERP'),
        'address': get_config_value('tenant_address', 'Menara 165 lantai 14 Unit E Jl. TB Simatupang No.Kav. 1, Cilandak Timur, Kec. Ps. Minggu, Kota Jakarta Selatan, 12560.'),
        'contact': get_config_value('tenant_contact', 'contact@arnatech.id'),
        'currency_symbol': get_config_value('tenant_default_currency_symbol', 'IDR'),
    }

def generate_invoice_pdf_for_instance(instance):
    invoice = Invoice.objects.filter(order=instance).last()
    if not invoice:
        return
    context = {'tenant_info': get_tenant_info(), 'invoice': invoice}
    pdf_content = render_to_pdf('document/invoice.html', context)
    if pdf_content:
        filename = f"Invoice_{invoice.id32}.pdf"
        file = save_pdf_to_file(pdf_content, filename)
        invoice.attachment = file
        invoice.save()
        return file
    return None

def generate_invoice_pdf_for_instances(instances):
    invoices = Invoice.objects.filter(order__in=instances)
    if not invoices.exists():
        return
    context = {'tenant_info': get_tenant_info(), 'invoices': invoices}
    pdf_content = render_to_pdf('document/invoices.html', context)
    if pdf_content:
        invoice_id32s = ''.join(invoices.values_list('id32', flat=True))
        filename = f"Invoices_{invoice_id32s}.pdf"
        return save_pdf_to_file(pdf_content, filename)
    return None
