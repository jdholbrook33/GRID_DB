import streamlit as st
import pandas as pd
from sqlalchemy import join
from database import get_session
from models import OrderDetail, Employee
from utils import format_dataframe
import colorsys

def get_color_for_date(date, base_hue=0.6, saturation=0.2, value=0.2):
    """Generate a color based on the date."""
    # Use the day of the year to slightly adjust the hue
    day_of_year = pd.to_datetime(date).dayofyear
    hue_adjust = (day_of_year % 10) / 100  # Small adjustment based on day
    hue = (base_hue + hue_adjust) % 1.0
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return f'rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})'

def display_order_details():
    # Add instructions
    st.info("""
    How to use this grid:
            
    1. Select a Work Order ID from the dropdown menu below.
    2. The details of the selected order will be displayed in the grid below.
    3. You can not edit data here.
    """)

    st.header("Order Details")
    
    session = get_session()
    
    try:
        order_ids = [row[0] for row in session.query(OrderDetail.OrderID).distinct()]
        
        if not order_ids:
            st.error("No OrderIDs found in the OrderDetail table.")
            return

        selected_order_id = st.selectbox("Select Work Order ID", order_ids)
        
        # Join OrderDetail and Employee tables
        query = session.query(OrderDetail, Employee.EmployeeName).\
            join(Employee, OrderDetail.EmployeeID == Employee.EmployeeID).\
            filter(OrderDetail.OrderID == selected_order_id)
        
        results = query.all()
        
        if results:
            data = []
            for order_detail, employee_name in results:
                row = {c.name: getattr(order_detail, c.name) for c in order_detail.__table__.columns}
                row['EmployeeName'] = employee_name
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Remove unnecessary columns and rename EmployeeName
            display_df = df.drop(columns=['ID', 'OrderDetailID', 'EmployeeID'])
            display_df = display_df.rename(columns={'EmployeeName': 'Employee'})
            
            # Sort by DateAdded to ensure consistent color assignment
            display_df = display_df.sort_values('DateAdded')
            
            # Assign colors based on unique dates
            unique_dates = display_df['DateAdded'].unique()
            color_map = {date: get_color_for_date(date) for date in unique_dates}
            
            # Create a style function for the entire dataframe
            def style_df(row):
                return [f'background-color: {color_map[row.DateAdded]}'] * len(row)
            
            # Apply the style
            styled_df = display_df.style.apply(style_df, axis=1)
            
            st.subheader(f"Order Items for Order ID: {selected_order_id}")
            st.dataframe(styled_df, use_container_width=True)
            
            total_items = display_df['Quantity'].sum()
            unique_items = len(display_df['ProductID'].unique())
            st.write(f"**Total Items:** {total_items}")
            st.write(f"**Unique Items:** {unique_items}")
            
            # if st.button("Export to CSV"):
            #     csv = display_df.to_csv(index=False)
            #     st.download_button(
            #         label="Download CSV",
            #         data=csv,
            #         file_name=f"order_details_{selected_order_id}.csv",
            #         mime="text/csv",
            #     )
        else:
            st.warning("No details found for this order.")

        # Add the Advanced Order View button
        if st.button("Advanced Order View"):
            display_advanced_order_view()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Debug: Full error details:")
        st.write(e)
    
    finally:
        session.close()

def display_advanced_order_view():
    st.subheader("Advanced Order View")
    
    session = get_session()
    
    try:
        # Fetch all OrderDetail data
        order_details = session.query(OrderDetail).all()
        
        # Convert to DataFrame
        df = pd.DataFrame([{c.name: getattr(detail, c.name) for c in OrderDetail.__table__.columns} for detail in order_details])
        
        # Display the raw data
        st.dataframe(df)
        
        # Add an export option
        # if not df.empty:
        #     csv = df.to_csv(index=False)
        #     st.download_button(
        #         label="Export CSV",
        #         data=csv,
        #         file_name="order_details_raw.csv",
        #         mime="text/csv",
        #     )
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    
    finally:
        session.close()