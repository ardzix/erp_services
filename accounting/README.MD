# Accounting Models Explained

## Account

- Purpose: Represents an account in your accounting system. In accounting, an account records transactions of a specific type, like sales, purchases, cash, bank, expenses, etc.

- Usage: You'll create various accounts to track different types of financial transactions. For example, you might have an account for "Sales," another for "Cash," one for "Accounts Receivable," etc.

## Tax

- Purpose: Used to record different types of taxes that your company might deal with, like VAT, sales tax, etc.

- Usage: Whenever a transaction involves a tax (like a sale or purchase), a Tax object can be associated with that transaction to apply the correct tax rate.

## Transaction

- Purpose: Represents a financial transaction in your business. This could be anything from a sale, a purchase, a transfer of funds between accounts, an expense, etc.

- Usage: Every time a financial event occurs (like receiving payment for an invoice or buying office supplies), a Transaction is recorded. Each transaction is linked to an Account to show which account is affected.

## JournalEntry

- Purpose: Used in double-entry bookkeeping to record changes in different accounts as a result of a transaction. Each transaction leads to at least two journal entries: a debit in one account and a credit in another.

- Usage: When a transaction is recorded, corresponding JournalEntry objects are created to record the debit and credit sides. For example, when recording a sale, you might debit "Accounts Receivable" and credit "Sales."

## GeneralLedger

- Purpose: A record of all the transactions that affect each account. Essentially, it's a detailed report of all transactions for each account.

- Usage: As transactions occur and are recorded in JournalEntry, the GeneralLedger gets updated to reflect these changes, showing the current balance of each account.

## FinancialStatement

- Purpose: Used to create various financial reports like balance sheets, income statements, etc.

- Usage: This model can be used to generate reports that summarize the financial performance and status of the business. For example, an income statement would be a type of FinancialStatement.

## FinancialEntry

- Purpose: Records individual entries in a FinancialStatement. Each entry would usually be linked to an Account and show amounts relevant to that financial statement.

- Usage: When creating a financial statement, FinancialEntry objects are used to record specific details from various accounts. For example, in an income statement, you would have entries for different revenue and expense accounts.