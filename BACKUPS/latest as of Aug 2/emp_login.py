import streamlit as st
from database import get_session
from models import Employee

def emp_login():
    st.title("Employee Login")
    
    # Initialize session state for employee_id if it doesn't exist
    if 'employee_id_input' not in st.session_state:
        st.session_state.employee_id_input = ''

    # Function to update employee_id_input
    def update_input(value):
        if len(st.session_state.employee_id_input) < 4:
            st.session_state.employee_id_input += value

    # Function to clear input
    def clear_input():
        st.session_state.employee_id_input = ''

    # Display current input
    st.text_input("Employee ID", value=st.session_state.employee_id_input, max_chars=4, key="display", disabled=True)

    # Create keypad
    col1, col2, col3 = st.columns(3)
    for i, col in enumerate([col1, col2, col3], 1):
        for j in range(3):
            num = i + j * 3
            if num < 10:
                col.button(str(num), on_click=update_input, args=(str(num),), key=f"btn_{num}")

    # Last row of keypad
    col1, col2, col3 = st.columns(3)
    col1.button("Clear", on_click=clear_input)
    col2.button("0", on_click=update_input, args=("0",))
    col3.button("Enter", on_click=validate_employee)

def validate_employee():
    employee_id = st.session_state.employee_id_input
    if len(employee_id) != 4:
        st.error("Please enter a 4-digit Employee ID")
        return

    session = get_session()
    try:
        employee = session.query(Employee).filter(Employee.EmployeeID == employee_id).first()
        if employee:
            st.session_state.employee_id = employee_id
            st.session_state.employee_name = employee.EmployeeName
            st.session_state.page = 'work_order'
            st.session_state.login_success = True
        else:
            st.error("Invalid Employee ID. Please try again.")
            st.session_state.employee_id_input = ''  # Reset the input
    finally:
        session.close()

# Check if login was successful and display a message
if st.session_state.get('login_success'):
    st.success(f"Welcome, {st.session_state.employee_name}!")
    st.session_state.pop('login_success')