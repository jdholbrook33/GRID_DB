import streamlit as st
import pandas as pd
from database import get_session
from models import Employee
from utils import validate_and_format_phone, validate_zip_code, validate_email, validate_and_format_dataframe, format_dataframe

def validate_employee_id(df):
    if 'EmployeeID' in df.columns:
        invalid_ids = df[~df['EmployeeID'].astype(str).str.match(r'^\d{4}$')]
        if not invalid_ids.empty:
            return "EmployeeID must be exactly 4 digits."
    return None

def validate_and_format_employee_data(df):
    validations = [
        {'func': validate_employee_id},
        {'func': validate_and_format_phone, 'args': ['EmployeePhone']},
        {'func': validate_zip_code, 'args': ['EmployeeZipcode']},
        {'func': validate_email, 'args': ['EmployeeEmail']},
    ]
    return validate_and_format_dataframe(df, validations)

def display_employee_form():
    st.info("""
        How to use this grid:

        1. Edit any data directly in the grid below.
        2. To add a new record, click the '+' icon on the upper right of the grid.
                    
        Note: All edits are temporary until you click 'Save Changes'.
        """)
    
    st.header("Employees")
    
    session = get_session()
    
    try:
        employees_data = session.query(Employee).all()
        employees_df = pd.DataFrame([{c.name: getattr(emp, c.name) for c in emp.__table__.columns} for emp in employees_data])
        
        # Format the dataframe
        employees_df = format_dataframe(employees_df)
        
        # Create a copy of the dataframe for display, excluding the ID column
        display_df = employees_df.drop(columns=['ID'])
        
        # Create column configuration
        column_config = {
            'EmployeeActive': st.column_config.CheckboxColumn(
                'Employee Active',
                help="Is the employee currently active?",
                default=True
            )
        }
        
        # Display the editable dataframe
        edited_df = st.data_editor(
            display_df,
            column_config=column_config,
            hide_index=True,
            num_rows="dynamic"
        )
        
        if st.button("Save Changes"):
            # Add back the ID column
            edited_df['ID'] = employees_df['ID']
            
            formatted_df, errors = validate_and_format_employee_data(edited_df)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                save_changes(Employee, formatted_df, session)
                st.success("Changes saved successfully!")
                
                # Re-query the database to display the actual saved state
                updated_employees_data = session.query(Employee).all()
                updated_employees_df = pd.DataFrame([{c.name: getattr(emp, c.name) for c in emp.__table__.columns} for emp in updated_employees_data])
                updated_employees_df = format_dataframe(updated_employees_df)
                
                # Remove ID column for display
                updated_display_df = updated_employees_df.drop(columns=['ID'])
                st.write("Updated data from database:", updated_display_df)
    
    finally:
        session.close()

def save_changes(model, edited_df, session):
    try:
        for index, row in edited_df.iterrows():
            item = session.query(model).filter_by(ID=row['ID']).first()
            if item:
                for column in row.index:
                    setattr(item, column, row[column])
            else:
                new_item = model(**row.to_dict())
                session.add(new_item)
        
        session.commit()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        session.rollback()