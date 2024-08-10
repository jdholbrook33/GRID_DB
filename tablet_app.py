import streamlit as st

# Set page config once, as the first Streamlit command
st.set_page_config(page_title="Inventory Check-out System", layout="wide")

def tablet_main():
    # Lazy imports
    from emp_login import emp_login
    from work_order_entry import work_order_entry
    from part_checkout import part_checkout

    # Initialize the page if it's not set
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
        
    # Get the current page from session state
    current_page = st.session_state.page

    # Page routing
    if current_page == 'login':
        emp_login()
    elif current_page == 'work_order':
        work_order_entry()
    elif current_page == 'part_checkout':
        part_checkout()
    else:
        st.error(f"Unknown page: {current_page}. Redirecting to login.")
        st.session_state.page = 'login'

    # Check if work order was validated and redirect
    if st.session_state.get('work_order_validated'):
        st.session_state.pop('work_order_validated')
        st.rerun()

    # Add a logout button
    if current_page != 'login':
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # Display current user info
    if 'employee_name' in st.session_state:
        st.sidebar.write(f"Logged in: {st.session_state.employee_name}")

if __name__ == "__main__":
    tablet_main()