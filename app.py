import streamlit as st
from employee_form import display_employee_form
from inventory_management import display_inventory
from supplier_form import display_supplier_form
from order_form import display_orders
from order_details import display_order_details
from emp_login import emp_login

def main():
    st.set_page_config(page_title="Inventory Management", layout="wide")
    st.title("Inventory Management")

    # Sidebar navigation
    pages = {
        "Inventory": display_inventory,
        "Employees": display_employee_form,
        "Suppliers": display_supplier_form,
        "Orders": display_orders,
        "Order Details": display_order_details,
        "Employee Login (Test)": emp_login  # Added emp_login for testing
    }
    
    selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))

    # Display the selected page
    pages[selected_page]()

if __name__ == "__main__":
    main()