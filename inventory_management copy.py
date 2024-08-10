import streamlit as st
import pandas as pd
from database import get_session
from models import Inventory, Suppliers
from utils import format_dataframe

def get_supplier_dict(session):
    suppliers = session.query(Suppliers).all()
    return {s.SupplierID: s.SupplierName for s in suppliers}

def display_inventory():
    st.header("Inventory")
    
    session = get_session()
    
    try:
        # Fetch supplier data
        supplier_dict = get_supplier_dict(session)
        
        inventory_data = session.query(Inventory).all()
        inventory_df = pd.DataFrame([{c.name: getattr(item, c.name) for c in item.__table__.columns} for item in inventory_data])
        
        inventory_df = format_dataframe(inventory_df)
        
        # Create a copy of the dataframe for display, excluding the ID column
        display_df = inventory_df.drop(columns=['ID'])
        
        # Create a reverse mapping of SupplierID to SupplierName
        id_to_name = {v: k for k, v in supplier_dict.items()}
        
        # Create column configuration
        column_config = {
            'SupplierID': st.column_config.SelectboxColumn(
                'SupplierID',
                help="Select the supplier",
                width="medium",
                options=list(supplier_dict.values()),
                required=True
            )
        }
        
        # Convert SupplierID to SupplierName for display
        display_df['SupplierID'] = display_df['SupplierID'].map(id_to_name)
        
        # Display the editable dataframe
        edited_df = st.data_editor(
            display_df,
            column_config=column_config,
            hide_index=True,
            num_rows="dynamic"
        )
        
        if st.button("Save Changes"):
            # Add back the ID column
            edited_df['ID'] = inventory_df['ID']
            
            # Convert SupplierName back to SupplierID
            edited_df['SupplierID'] = edited_df['SupplierID'].map(supplier_dict)
            
            save_changes(Inventory, edited_df, session)
    
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