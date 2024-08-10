import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from database import get_session
from models import Inventory, Suppliers

# Database connection
engine = create_engine('sqlite:///data/CNC_DB.db')

@st.cache_data
def load_data():
    suppliers_df = pd.read_sql('SELECT * FROM Suppliers', engine)
    inventory_df = pd.read_sql('SELECT * FROM Inventory', engine)
    return suppliers_df, inventory_df

def display_inventory():
    st.info("""
    How to use this grid:

    1. Edit any data directly in the table below.
    2. To change a Supplier, use the dropdown in the 'Supplier' column.
    3. The SupplierID will update automatically when you save.
    4. To add a new record, click the '+' icon on the upper right of the grid.

    Note: All edits are temporary until you click 'Save Changes'.
    """)

    st.header("Inventory")
    
    suppliers_df, inventory_df = load_data()

    # Create dictionaries for supplier lookup
    supplier_dict = dict(zip(suppliers_df.SupplierID, suppliers_df.SupplierName))
    reverse_supplier_dict = {v: k for k, v in supplier_dict.items()}

    # Prepare the inventory dataframe
    if 'display_df' not in st.session_state:
        st.session_state.display_df = inventory_df.copy()
        st.session_state.display_df['SupplierName'] = st.session_state.display_df['SupplierID'].map(supplier_dict)

    # Define column_config before using it
    column_config = {
        "SupplierName": st.column_config.SelectboxColumn(
            "Supplier",
            help="Select the supplier",
            width="medium",
            options=list(supplier_dict.values()),
            required=True
        ),
        "SupplierID": st.column_config.NumberColumn(
            "SupplierID",
            help="SupplierID (will update on save)",
            width="small",
            format="%d",  # This ensures the number is displayed without commas
            disabled=True
        ),
        "ID": st.column_config.Column(
            "ID",
            disabled=True, 
        ),
        "Notes": st.column_config.TextColumn(
            "Notes",
            width="large"
        )
    }

    # Create an editable dataframe
    edited_df = st.data_editor(
        st.session_state.display_df,
        key="data_editor",
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button('Save Changes'):
        # Update SupplierID based on selected SupplierName
        for idx, row in edited_df.iterrows():
            if 'SupplierName' in row:
                new_supplier_name = row['SupplierName']
                new_supplier_id = reverse_supplier_dict.get(new_supplier_name)
                if new_supplier_id is not None:
                    edited_df.at[idx, 'SupplierID'] = new_supplier_id
        
        # Remove the SupplierName column before saving
        save_df = edited_df.drop('SupplierName', axis=1)
        
        # Save to database
        save_df.to_sql('Inventory', engine, if_exists='replace', index=False)
        st.success("Changes saved successfully!")
        
        # Update the session state
        st.session_state.display_df = edited_df
        
        # Rerun to reflect changes
        st.rerun()

    # Instruction bubble


# We don't need the __main__ block here as this will be called from app.py