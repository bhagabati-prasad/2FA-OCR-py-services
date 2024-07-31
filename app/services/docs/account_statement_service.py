import re
from datetime import datetime
from collections import defaultdict


# Get Date
def __get_date(text):
    day = month = year = None
    if "Statement" not in text:
        date = re.search("[0-9]{2,}/[0-9]{2,}/[0-9]{2,}", text)
        if date:
            date = date.group(0)
            splitted_date = date.split("/")
            day = splitted_date[0][-2:]
            month = splitted_date[1]
            year = (
                splitted_date[2][0:4]
                if len(splitted_date[2]) >= 4
                else splitted_date[2][0:2]
            )
            year = year[-2:] if len(year) == 4 else year

    return f"{day}/{month}/{year}"


# Group all transactions by month
def __group_transactions_by_month(transactions):
    grouped_transactions = defaultdict(list)
    for transaction in transactions:
        try:
            transaction_date = datetime.strptime(transaction["date"], "%d/%m/%y")
            month_year = (transaction_date.year, transaction_date.month)
            grouped_transactions[month_year].append(transaction)
        except:
            raise
    return grouped_transactions


# REGEX Patterns to extract accountNumber, customerName, ifscCode, bankCode, branchCode
def extract_basic_info(input_data):
    account_number_pattern = re.compile(r"(Account No|Account Number)\s*[: ]\s*(\d+)")
    customer_name_pattern_1 = re.compile(r"(MR|MRS|MS)\s+(.+)")
    customer_name_pattern_2 = re.compile(r"Name\s+(.+)")

    pincode_index = None
    for entry in input_data:
        text = entry["text"]
        pincode_match = re.search("[0-9]{6}", text)
        if pincode_match:
            pincode_index = input_data.index(entry)

    # Extracting details
    prefix = None
    account_number = None
    customer_name = None
    bank_code = None
    branch_code = None
    ifsc_code = None

    for data in reversed(input_data[0:pincode_index]):
        text = data["text"]
        # Customer Name
        if customer_name is None:
            customer_match = customer_name_pattern_1.search(text)
            if customer_match:
                customer_name = customer_match.group(0).strip()
            elif "Name" in text:
                customer_match_2 = customer_name_pattern_2.search(text)
                if customer_match_2:
                    customer_name = customer_match_2.group(1).strip()

    for entry in input_data:
        text = entry["text"]

        # Account Number
        if account_number is None:
            account_match = account_number_pattern.search(text)
            if account_match:
                account_number = account_match.group(2)

        # Customer Name
        if customer_name is None:
            customer_match = customer_name_pattern_1.search(text)
            if customer_match:
                customer_name = customer_match.group(0).strip()
            elif "Name" in text:
                customer_match_2 = customer_name_pattern_2.search(text)
                if customer_match_2:
                    customer_name = customer_match_2.group(1).strip()

        # IFSC, Bank and Branch Codes
        if ifsc_code is None or bank_code is None or branch_code is None:
            if "ifsc" in text.lower():
                ifsc_match = re.search(r"[A-Za-z]{4}[0-9]{7}", text.lower())
                if ifsc_match:
                    # IFSC Code
                    ifsc_code = ifsc_match.group(0)
                    if ifsc_code is not None:
                        ifsc_code = ifsc_code.upper()
                    # Bank Code
                    bank_code = ifsc_code[0:4]
                    # Branch Code
                    branch_code = ifsc_code[5:]

    if customer_name and prefix == None:
        customer_name = customer_name.upper()
        if customer_name.startswith("MR"):
            prefix = "MR"
            # customer_name = customer_name.replace("MR", "")
            # customer_name = customer_name.replace(".", "")
            # customer_name = customer_name.strip()
        if customer_name.startswith("MS"):
            prefix = "MS"
            # customer_name = customer_name.replace("MS", "")
            # customer_name = customer_name.replace(".", "")
            # customer_name = customer_name.strip()

    return {
        "accountNumber": account_number,
        "prefix": prefix,
        "customerName": customer_name,
        "ifscCode": ifsc_code,
        "bankCode": bank_code,
        "branchCode": branch_code,
    }


def get_daily_transactions(input_data):
    # List to hold transactions
    transactions_list = []
    prev_closing = None

    date = None
    amount = None
    closing_amount = None
    transaction_type = None

    for entry in input_data:
        text = entry["text"]

        date = __get_date(text)

        if "Cr" in text or "Dr" in text:
            closing_amount_type1 = re.search(
                r"(\d{1,}(?:,\d{4})*(?:\.\d{2})?)\s*\((Dr|Cr)\)$", text
            )
            if closing_amount_type1:
                closing_amount = float(closing_amount_type1.group(1).replace(",", ""))
        else:
            closing_amount_match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)$", text)
            if closing_amount_match:
                closing_amount = float(closing_amount_match.group(1).replace(",", ""))

        if closing_amount is not None:
            if prev_closing is not None:
                if closing_amount > prev_closing:
                    transaction_type = "Credit"
                else:
                    transaction_type = "Debit"
            else:
                transaction_type = (
                    "Unknown"  # For the first transaction, we cannot determine
                )
            amount = (
                abs(prev_closing - closing_amount) if prev_closing is not None else 0
            )

        if (
            "None" not in date
            and (amount is not None or amount is not 0 or amount is not False)
            and closing_amount is not None
            and transaction_type is not None
        ):
            transaction_obj = {
                "date": date,
                "amount": round(amount, 2),
                "transactionType": transaction_type,
                "closingBalance": closing_amount,
            }
            if amount is 0 and transaction_type is "Unknown":
                transaction_obj["openingBalance"] = closing_amount
                # del transaction_obj["amount"]
                del transaction_obj["closingBalance"]
                # del transaction_obj["transactionType"]
                transactions_list.append(transaction_obj)
            elif amount != 0:
                transactions_list.append(transaction_obj)
            # if transaction_obj["amount"] != 0 and transaction_type is "Unknown":
            #     transactions_list.append(transaction_obj)
            prev_closing = closing_amount

    return transactions_list


# REGEX Pattern to find Daily Transactions
def extract_daily_transactions(input_data):
    # Regular expression to match transaction details
    transaction_pattern = re.compile(
        r"(?P<date>\d{2}/\d{2}/\d{2})\s.*?(?P<ref_no>\d{12,})\s\d{2}/\d{2}/\d{2}\s(?P<amount>[0-9,]*\.\d{2})\s(?P<closing>[0-9,]*\.\d{2})"
    )

    # List to hold transactions
    transactions_list = []
    prev_closing = None

    # Extract transactions
    for entry in input_data:
        text = entry["text"]
        match = transaction_pattern.search(text)
        if match:
            current_closing = float(match.group("closing").replace(",", ""))
            if prev_closing is not None:
                if current_closing > prev_closing:
                    transaction_type = "Credit"
                else:
                    transaction_type = "Debit"
            else:
                transaction_type = (
                    "Unknown"  # For the first transaction, we cannot determine
                )
            transactions_list.append(
                {
                    "date": match.group("date"),
                    "Chq./Ref.No.": match.group("ref_no"),
                    "amount": float(match.group("amount").replace(",", "")),
                    "closing": float(match.group("closing").replace(",", "")),
                    "type": transaction_type,
                }
            )
            prev_closing = current_closing
    return transactions_list


# Get Monthly Expenses from daily transactions
def filter_monthly_expenses(input_data):
    grouped_transactions = __group_transactions_by_month(input_data)
    monthly_expenses_summary = []
    total_debit = 0
    total_credit = 0
    for month_year, transactions in grouped_transactions.items():
        # Total Expense
        total_expense = sum(
            transaction["amount"]
            for transaction in transactions
            if transaction["transactionType"] == "Debit"
        )
        total_expense = abs(total_expense)
        # Total Income
        total_income = sum(
            transaction["amount"]
            for transaction in transactions
            if transaction["transactionType"] == "Credit"
        )
        total_income = abs(total_income)
        # Month and Year
        year, month = month_year
        month_name = datetime(year, month, 1).strftime("%B")
        monthly_expenses_summary.append(
            {
                "year": year,
                "month": month_name,
                "totalExpense": round(total_expense, 2),
                "totalIncome": round(total_income, 2),
            }
        )

        total_debit += total_expense
        total_credit += total_income
    return [monthly_expenses_summary, round(total_debit, 2), round(total_credit, 2)]
