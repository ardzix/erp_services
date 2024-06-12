from common.helpers import get_tenant_info
from libs.pdf import render_to_pdf, save_pdf_to_file
from ..models import Invoice

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
