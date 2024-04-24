from django.utils.translation import gettext_lazy as _

# Transaction constants
SALES_ORDER= 'sales_order'
SALES_PAYMENT= 'sales_payment'
PURCHASE= 'purchase'
TRANSFER= 'transfer'  # For transferring funds between accounts
ADJUSTMENT= 'adjustment'  # For corrections or modifications
EXPENSE= 'expense'  # For general expenses
INCOME= 'income'  # For general income, other than sales
DEPOSIT= 'deposit'  # For deposits into accounts
WITHDRAWAL= 'withdrawal'  # For withdrawals from accounts
REFUND= 'Refund'  # For processing refunds
RECONCILIATION= 'reconciliation'  # For reconciliation adjustments
LOAN_PAYMENT= 'loan_payment'  # For repaying loans
LOAN_RECEIPT= 'loan_receipt'  # For receiving loan amounts
TAX_PAYMENT= 'tax_payment'  # For specific tax payments
TAX_REFUND= 'tax_refund'  # For receiving tax refunds
INTEREST_INCOME= 'interest_income'  # For interest received
INTEREST_EXPENSE= 'interest_expense'  # For interest paid out
DIVIDEND= 'dividend'  # For dividend income
FEE= 'fee'  # For any fees charged or paid
COMMISSION= 'commission'  # For commissions received or paid
WRITE_OFF= 'write_off'  # For bad debts or uncollectible amounts

TRANSACTION_CHOICES = (
    (SALES_ORDER, _('Sales Order')),
    (SALES_PAYMENT, _('Sales Payment')),
    (PURCHASE, _('Purchase')),
)

# Journal Constants
CREDIT = 'CREDIT'
DEBIT = 'DEBIT'

DEBIT_CREDIT_CHOICES = (
    (DEBIT, _('Debit')),
    (CREDIT, _('Credit'))
)

CASH_IN = "cash_in"
CASH_OUT = "cash_out"

# Transaction Module
SALES_ORDER_CREDIT = 'sales_order_credit'
SALES_ORDER_DEBIT = 'sales_order_debit'
SALES_ADVANCE_PAYMENT = 'sales_advance_payment'
PURCHASING_ADVANCE_PAYMENT = 'purchasing_advance_payment'

TRANSACTION_MODULE_CHOICES = (
    (SALES_ORDER_CREDIT, _('Sales order credit')),
    (SALES_ORDER_DEBIT, _('Sales order debit')),
    (SALES_ADVANCE_PAYMENT, _('Sales advance payment')),
    (SALES_ORDER_DEBIT, _('Purchasing advance payment')),
)