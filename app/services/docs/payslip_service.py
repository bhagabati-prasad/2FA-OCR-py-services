import re
import pdfplumber


def get_payslip_info(pdf_file):
    employer_name = ""
    employee_name = ""
    designation = ""
    employment_start_date = ""
    monthly_income = ""

    with pdfplumber.open(pdf_file) as pdf:
        payslip_data = pdf.pages[0].extract_table()

        # Iterate over each list in payslip_data to find the required details
        for item in payslip_data:
            # Extract employer name
            if item[0] and "PAYSLIP FOR THE MONTH OF" in item[0]:
                employer_name = item[0].split("\n")[0]

            # Extract employee name
            if "Emp Name" in item or "Employee Name" in item:
                emp_name_index = (
                    item.index("Emp Name")
                    if "Emp Name" in item
                    else item.index("Employee Name")
                )
                employee_name = item[emp_name_index + 1]

            # Extract designation
            if "Designation" in item:
                designation_index = item.index("Designation")
                designation = item[designation_index + 1]

            # Extract employment start date
            # if (
            #     "Date Of Joining" in item
            #     or "Date of Joining" in item
            #     or "Joining" in item
            # ):
            #     employment_start_date_index = (
            #         item.index("Date Of Joining")
            #         if "Date Of Joining" in item
            #         else item.index("Date of Joining")
            #     )
            #     employment_start_date = item[employment_start_date_index + 2]

            if not employment_start_date:
                selfItem = None
                for txt in item:
                    if txt:
                        if "joining" in txt.lower():
                            selfItem = item
                if selfItem is not None:
                    for text in selfItem:
                        if text:
                            doj_match = re.search(
                                "[0-9 ]{2}[A-Za-z ]{3,9}[0-9]{4}", text
                            )
                            if doj_match:
                                employment_start_date = doj_match.group(0)

            # Extract monthly income
            if any("Net Pay:" in str(sub_item) for sub_item in item):
                for sub_item in item:
                    if isinstance(sub_item, str) and "Net Pay:" in sub_item:
                        monthly_income_match = re.search(
                            r"Rs\.\s([\d,]+.\d+)", sub_item
                        )
                        if monthly_income_match:
                            monthly_income = monthly_income_match.group(1)

        return {
            "employerName": employer_name,
            "employeeName": employee_name,
            "designation": designation,
            "employmentStartDate": employment_start_date,
            "monthlyIncome": monthly_income,
        }
