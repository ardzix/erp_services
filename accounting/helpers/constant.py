# Transaction constants
SALE= 'Sale'
PURCHASE= 'Purchase'
TRANSFER= 'Transfer'  # For transferring funds between accounts
ADJUSTMENT= 'Adjustment'  # For corrections or modifications
EXPENSE= 'Expense'  # For general expenses
INCOME= 'Income'  # For general income, other than sales
DEPOSIT= 'Deposit'  # For deposits into accounts
WITHDRAWAL= 'Withdrawal'  # For withdrawals from accounts
REFUND= 'Refund'  # For processing refunds
RECONCILIATION= 'Reconciliation'  # For reconciliation adjustments
LOAN_PAYMENT= 'Loan Payment'  # For repaying loans
LOAN_RECEIPT= 'Loan Receipt'  # For receiving loan amounts
TAX_PAYMENT= 'Tax Payment'  # For specific tax payments
TAX_REFUND= 'Tax Refund'  # For receiving tax refunds
INTEREST_INCOME= 'Interest Income'  # For interest received
INTEREST_EXPENSE= 'Interest Expense'  # For interest paid out
DIVIDEND= 'Dividend'  # For dividend income
FEE= 'Fee'  # For any fees charged or paid
COMMISSION= 'Commission'  # For commissions received or paid
WRITE_OFF= 'Write Off'  # For bad debts or uncollectible amounts
OTHER= 'Other'

# Journal Constants
CREDIT = 'CREDIT'
DEBIT = 'DEBIT'

# Account name constants
CASH_ACCOUNT =  "Cash and Cash Equivalents"  # Cash in hand and demand deposits
AR_ACCOUNT = "Accounts Receivable"  # Amounts owed by customers
INVENTORY_ACCOUNT = "Inventory"  # Goods available for sale
PREPAID_EXP_ACCOUNT = "Prepaid Expenses"  # Expenses paid in advance for future periods
ST_INVESTMENT_ACCOUNT = "Short-Term Investments"  # Investments that will be converted to cash within a year"
TANGIBLE_ASSET_ACCOUNT = "Property, Plant, and Equipment"  # Tangible fixed assets
INTANGIBLE_ASSET = "Intangible Assets"  # Non-physical assets like patents and copyrights
LT_INVESTMENT_ACCOUNT = "Long-Term Investments"  # Investments held for longer than a year
AP_ACCOUNT = "Accounts Payable"  # Amounts owed to suppliers"
ACCRUED_LIAB_ACCOUNT = "Accrued Liabilities"  # Liabilities for expenses incurred but not yet paid
ST_DEBT_ACCOUNT = "Short-Term Debt"  # Debts due within one year"
LT_DEBT_ACCOUNT = "Long-Term Debt"  # Debts due in more than one year"
COMMON_STOCK_ACCOUNT = "Common Stock"  # Value of issued common shares"
RETAINED_EARNING_ACCOUNT = "Retained Earnings"  # Cumulative earnings kept for reinvestment
ADD_PAID_IN_CAPITAL_ACCOUNT = "Additional Paid-In Capital"  # Amount received from the issuance of shares above par value
SALES_ACCOUNT = "Sales Revenue"  # Income from primary operations
COGS_ACCOUNT = "Cost of Goods Sold"  # Cost associated with producing goods
OPERATING_EXP_ACCOUNT = "Operating Expenses"  # General and administrative expenses
INTEREST_EXP_ACCOUNT = "Interest Expense"  # Cost of borrowing money
TAX_EXP_ACCOUNT = "Tax Expense"  # Taxes on profits
TAX_LIAB_ACCOUNT = "Tax Liability"  # Taxes that should be paid
ROUNDING_ACCOUNT = "Rounding"  # Small discrepancies between the account amount and the amount actually received.
OTHER_ACCOUNT = "Other"  # Small discrepancies between the account amount and the amount actually received.

JOURNAL_DEBIT_MAP = (
    (SALE, AR_ACCOUNT),
    (PURCHASE, AP_ACCOUNT),
)