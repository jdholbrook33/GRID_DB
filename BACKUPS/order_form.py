import streamlit as st
import pandas as pd
from database import get_session
from models import Orders
from utils import format_dataframe

def display_orders():
    st.info("""
    How to use this grid:

    1. Edit any data directly in the grid below.
    2. To add a new record, click the '+' icon on the upper right of the grid.
                
    Note: All edits are temporary until you click 'Save Changes'.
    """)

    st.header("Orders")
    
    session = get_session()
    
    try:
        orders_data = session.query(Orders).all()
        orders_df = pd.DataFrame([{c.name: getattr(order, c.name) for c in order.__table__.columns} for order in orders_data])
        
        orders_df = format_dataframe(orders_df)
        
        # Create a copy of the dataframe for display, excluding the ID column
        display_df = orders_df.drop(columns=['ID'])
        
        edited_df = st.data_editor(display_df, num_rows="dynamic")
        
        if st.button("Save Changes"):
            # Add back the ID column
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