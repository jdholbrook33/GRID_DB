import re
import pandas as pd

def validate_employee_id(df):
    if 'EmployeeID' in df.columns:
        invalid_ids = df[~df['EmployeeID'].astype(str).str.match(r'^\d{4}$')]
        if not invalid_ids.empty:
            return "EmployeeID must be exactly 4 digits."
    return None

def validate_and_format_phone(df, column_name):
    if column_name in df.columns:
        def format_phone(phone):
            digits = re.sub(r'\D', '', str(phone))
            if len(digits) == 10:
                return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
            return phone

        df[column_name] = df[column_name].apply(format_phone)
        invalid_phones = df[df[column_name].str.match(r'\d{3}-\d{3}-\d{4}') == False]
        if not invalid_phones.empty:
            return f"Some {column_name} are invalid. Please enter 10-digit phone numbers."
    return None

def validate_zip_code(df, column_name):
    if column_name in df.columns:
        invalid_zips = df[~df[column_name].astype(str).str.match(r'^\d{5}(-\d{4})?$')]
        if not invalid_zips.empty:
            return f"Some {column_name} are invalid. Please enter 5-digit or 9-digit (ZIP+4) zip codes."
    return None

def validate_email(df, column_name):
    if column_name in df.columns:
        invalid_emails = df[~df[column_name].str.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')]
        if not invalid_emails.empty:
            return f"Some {column_name} are invalid."
    return None

def validate_and_format_dataframe(df, validations):
    errors = []
    formatted_df = df.copy()

    for validation in validations:
        error = validation['func'](formatted_df, *validation.get('args', []))
        if error:
            errors.append(error)

    return formatted_df, errors