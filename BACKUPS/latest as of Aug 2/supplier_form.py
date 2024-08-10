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

def sortable_data_editor(df, key, column_config=None):
    col1, col2, col3 = st.columns([2, 2, 4])
    
    with col1:
        sort_column = st.selectbox(
            "Sort by",
            options=["None"] + list(df.columns),
            key=f"{key}_sort_column"
        )
    
    if sort_column != "None":
        with col2:
            sort_order = st.radio(
                "Sort order",
                options=["Ascending", "Descending"],
                horizontal=True,
                key=f"{key}_sort_order"
            )
        
        ascending = sort_order == "Ascending"
        df = df.sort_values(by=sort_column, ascending=ascending)
    
    edited_df = st.data_editor(
        df,
        key=f"{key}_editor",
        column_config=column_config,
        num_rows="dynamic"
    )
    
    return edited_df

def display_supplier_form():
    st.info("""
    How to use this grid:

    1. Edit any data directly in the grid below.
    2. To add a new record, click the '+' icon on the upper right of the grid.
    3. Use the 'Sort by' dropdown to sort the data by a specific column.
    4. Use the 'Sort order' radio buttons to choose ascending or descending order.
                
    Note: All edits are temporary until you click 'Save Changes'.
    """)
    st.header("Suppliers")
    
    session = get_session()
    
    try:
        suppliers_data = session.query(Suppliers).all()
        suppliers_df = pd.DataFrame([{c.name: getattr(sup, c.name) for c in sup.__table__.columns} for sup in suppliers_data])
        
        suppliers_df = format_dataframe(suppliers_df)
        
        display_df = suppliers_df.drop(columns=['ID'])
        
        edited_df = sortable_data_editor(
            display_df,
            key="supplier_data",
            column_config=None
        )
        
        if st.button("Save Changes"):
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