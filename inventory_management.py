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

def display_inventory():
    st.info("""
    How to use this grid:

    1. Edit any data directly in the table below.
    2. To change a Supplier, use the dropdown in the 'Supplier' column.
    3. The SupplierID will update automatically when you save.
    4. To add a new record, click the '+' icon on the upper right of the grid.
    5. Use the 'Sort by' dropdown to sort the data by a specific column.
    6. Use the 'Sort order' radio buttons to choose ascending or descending order.

    Note: All edits are temporary until you click 'Save Changes'.
    """)

    st.header("Inventory")
    
    suppliers_df, inventory_df = load_data()

    supplier_dict = dict(zip(suppliers_df.SupplierID, suppliers_df.SupplierName))
    reverse_supplier_dict = {v: k for k, v in supplier_dict.items()}

    if 'display_df' not in st.session_state:
        st.session_state.display_df = inventory_df.copy()
        st.session_state.display_df['SupplierName'] = st.session_state.display_df['SupplierID'].map(supplier_dict)

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
            format="%d",
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

    edited_df = sortable_data_editor(
        st.session_state.display_df,
        key="inventory_data",
        column_config=column_config
    )

    if st.button('Save Changes'):
        for idx, row in edited_df.iterrows():
            if 'SupplierName' in row:
                new_supplier_name = row['SupplierName']
                new_supplier_id = reverse_supplier_dict.get(new_supplier_name)
                if new_supplier_id is not None:
                    edited_df.at[idx, 'SupplierID'] = new_supplier_id
        
        save_df = edited_df.drop('SupplierName', axis=1)
        
        save_df.to_sql('Inventory', engine, if_exists='replace', index=False)
        st.success("Changes saved successfully!")
        
        st.session_state.display_df = edited_df
        
        st.rerun()

# We don't need the __main__ block here as this will be called from app.py