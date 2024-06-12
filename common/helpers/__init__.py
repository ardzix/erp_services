from libs.utils import get_config_value

def get_tenant_info():
    return {
        'name': get_config_value('tenant_name', 'BNK ERP'),
        'address': get_config_value('tenant_address', 'Menara 165 lantai 14 Unit E Jl. TB Simatupang No.Kav. 1, Cilandak Timur, Kec. Ps. Minggu, Kota Jakarta Selatan, 12560.'),
        'contact': get_config_value('tenant_contact', 'contact@arnatech.id'),
        'currency_symbol': get_config_value('tenant_default_currency_symbol', 'IDR'),
    }