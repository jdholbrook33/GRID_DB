import streamlit as st
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set page config once, as the first Streamlit command
st.set_page_config(page_title="Inventory Check-out System", layout="wide")

def tablet_main():
    logger.debug("Entering tablet_main function")
    # Lazy imports
    from emp_login import emp_login
    from work_order_entry import work_order_entry
    from part_checkout import part_checkout

    # Debug output
    st.sidebar.write("Debug Info:")
    st.sidebar.write(f"Session State: {st.session_state}")
    logger.debug(f"Session State: {st.session_state}")

    # Initialize the page if it's not set
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
        logger.debug("Initialized page to 'login'")
        
    # Get the current page from session state
    current_page = st.session_state.page
    logger.debug(f"Current Page: {current_page}")

    st.sidebar.write(f"Current Page: {current_page}")

    # Page routing
    if current_page == 'login':
        logger.debug("Routing to login page")
        emp_login()
    elif current_page == 'work_order':
        logger.debug("Routing to work order page")
        work_order_entry()
    elif current_page == 'part_checkout':
        logger.debug("Routing to part checkout page")
        part_checkout()
    else:
        logger.error(f"Unknown page: {current_page}")
        st.error(f"Unknown page: {current_page}. Redirecting to login.")
        st.session_state.page = 'login'

    # Check if work order was validated and redirect
    if st.session_state.get('work_order_validated'):
        logger.debug("work_order_validated flag detected. Triggering rerun.")
        st.session_state.pop('work_order_validated')
        st.rerun()

    # Add a logout button
    if current_page != 'login':
        if st.sidebar.button("Logout"):
            logger.debug("Logout button pressed")
            st.session_state.clear()
            st.rerun()

    # Display current user info
    if 'employee_name' in st.session_state:
        st.sidebar.write(f"Logged in: {st.session_state.employee_name}")
        logger.debug(f"Logged in user: {st.session_state.employee_name}")

if __name__ == "__main__":
    tablet_main()