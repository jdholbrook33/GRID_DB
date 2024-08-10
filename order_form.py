import streamlit as st
import pandas as pd
from sqlalchemy import select
from database import get_session
from models import Orders
from utils import format_dataframe

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

def display_orders():
    st.info("""
    How to use this grid:

    1. Edit any data directly in the grid below.
    2. To add a new record, click the '+' icon on the upper right of the grid.
    3. Use the 'Sort by' dropdown to sort the data by a specific column.
    4. Use the 'Sort order' radio buttons to choose ascending or descending order.
                
    Note: All edits are temporary until you click 'Save Changes'.
    """)

    st.header("Orders")
    
    session = get_session()
    
    try:
        # Use a select statement to explicitly choose columns
        stmt = select(Orders.ID, Orders.MondayOrderID, Orders.OrderDate, 
                      Orders.WorkDescription, Orders.WorkAddress, 
                      Orders.WorkState, Orders.WorkZipCode)
        result = session.execute(stmt)
        orders_data = result.fetchall()
        
        # Convert to dataframe
        orders_df = pd.DataFrame(orders_data, columns=['ID', 'MondayOrderID', 'OrderDate', 
                                                       'WorkDescription', 'WorkAddress', 
                                                       'WorkState', 'WorkZipCode'])
        
        orders_df = format_dataframe(orders_df)
        
        display_df = orders_df.drop(columns=['ID'])
        
        edited_df = sortable_data_editor(
            display_df,
            key="order_data",
            column_config=None
        )
        
        if st.button("Save Changes"):
            edited_df['ID'] = orders_df['ID']
            save_changes(Orders, edited_df, session)
    
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