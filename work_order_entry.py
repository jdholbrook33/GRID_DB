import streamlit as st
from database import get_session
from models import Orders
import streamlit.components.v1 as components

def work_order_entry():
    st.title("Enter Work Order")

    st.write("Please enter the 8-digit Monday Work Order Number")

    # JavaScript to handle input events and submit form
    js = """
    <script>
        function setFocus() {
            const input = window.parent.document.querySelector('.stTextInput input');
            if (input) {
                input.focus();
                input.addEventListener('input', function(e) {
                    if (this.value.length === 8) {
                        const form = this.closest('form');
                        if (form) {
                            form.dispatchEvent(new Event('submit'));
                        }
                    }
                });
            }
        }
        setFocus();
        setTimeout(setFocus, 500);
    </script>
    """
    components.html(js, height=0)

    # Initialize session state for work_order if it doesn't exist
    if 'work_order' not in st.session_state:
        st.session_state.work_order = ''

    # Use a form to control input submission
    with st.form(key='work_order_form'):
        work_order = st.text_input("Work Order", value=st.session_state.work_order, max_chars=8, key="work_order_input")
        submit_button = st.form_submit_button("Submit")

    if submit_button or (work_order and len(work_order) == 8):
        validate_work_order(work_order)

    # Create a 3x4 grid for the keypad
    cols = st.columns(3)
    for i in range(1, 10):
        if cols[i % 3].button(str(i), key=f"btn_{i}"):
            st.session_state.work_order += str(i)
            st.rerun()
    
    # Last row with 0, Clear, and Done
    if cols[0].button("Clear", key="btn_clear"):
        st.session_state.work_order = ''
        st.rerun()
    if cols[1].button("0", key="btn_0"):
        st.session_state.work_order += '0'
        st.rerun()
    if cols[2].button("Done", key="btn_done"):
        validate_work_order(st.session_state.work_order)

def validate_work_order(work_order):
    work_order = work_order.strip()
    
    if len(work_order) != 8 or not work_order.isdigit():
        st.error("Please enter an 8-digit Monday Work Order Number")
        return

    session = get_session()
    try:
        # Check if the work order exists
        order = session.query(Orders).filter(Orders.MondayOrderID == int(work_order)).first()
        
        if order:
            st.success(f"Valid Work Order: {work_order}")
            st.session_state.work_order = work_order
            st.session_state.page = 'part_checkout'
            st.session_state.work_order_validated = True
        else:
            st.error(f"Invalid Work Order Number: {work_order}. Please try again.")
            st.session_state.work_order = ''  # Reset the input
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    work_order_entry()