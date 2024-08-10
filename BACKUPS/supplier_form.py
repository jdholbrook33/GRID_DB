import streamlit as st
import pandas as pd
from database import get_session
from models import Suppliers
from utils import validate_and_format_phone, validate_zip_code, validate_email, validate_and_format_dataframe, format_dataframe

def validate_and_format_supplier_data(df):
    validations = [
        {'func': validate_and_format_phone, 'args': ['ContactPhone1']},
        {'func': validate_and_format_phone, 'args': ['ContactPhone2']},
        {'func': validate_zip_code, 'args': ['SupplierZipCode']},
        {'func': validate_email, 'args': ['ContactEmail1']},
        {'func': validate_email, 'args': ['ContactEmail2']},
    ]
    return validate_and_format_dataframe(df, validations)

def display_supplier_form():
    st.info("""
    How to use this grid:

    1. Edit any data directly in the grid below.
    2. To add a new record, click the '+' icon on the upper right of the grid.
                
    Note: All edits are temporary until you click 'Save Changes'.
    """)
    st.header("Suppliers")
    
    session = get_session()
    
    try:
        suppliers_data = session.query(Suppliers).all()
        suppliers_df = pd.DataFrame([{c.name: getattr(sup, c.name) for c in sup.__table__.columns} for sup in suppliers_data])
        
        suppliers_df = format_dataframe(suppliers_df)
        
        # Create a copy of the dataframe for display, excluding the ID column
        display_df = suppliers_df.drop(columns=['ID'])
        
        edited_df = st.data_editor(display_df, num_rows="dynamic")
        
        if st.button("Save Changes"):
            # Add back the ID column
            edited_df['ID'] = suppliers_df['ID']
            
            formatted_df, errors = validate_and_format_supplier_data(edited_df)
            if errors:
                for error in errors:
                    st.error(error)
            else:
                save_changes(Suppliers, formatted_df, session)
    
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
        st.success("Changes saved successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")
        session.rollback()