import streamlit as st
from database import get_session
from models import Inventory, OrderDetail
import streamlit.components.v1 as components
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
import time

def part_checkout():
    st.title("Part Check-out")

    st.write(f"Logged in as: {st.session_state.get('employee_name', 'Unknown')}")
    st.write(f"Work Order: {st.session_state.get('work_order', 'Unknown')}")

    # Display current work order
    work_order = st.session_state.get('work_order', 'No work order selected')
    st.write(f"Current Work Order: {work_order}")

    # Initialize session state variables
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
    if 'focus_counter' not in st.session_state:
        st.session_state.focus_counter = 0
    if 'confirmation_mode' not in st.session_state:
        st.session_state.confirmation_mode = False

    # Create placeholders for dynamic content
    error_placeholder = st.empty()
    input_placeholder = st.empty()
    cart_placeholder = st.empty()
    button_placeholder = st.empty()

    # Input for barcode scanning
    barcode = input_placeholder.text_input("Scan or enter item barcode", key=f"barcode_input_{st.session_state.focus_counter}")

    if barcode:
        process_barcode(barcode)
        st.session_state.focus_counter += 1
        st.rerun()

    # Display cart as a grid
    if st.session_state.cart:
        display_cart(cart_placeholder)

    # Checkout button logic
    if not st.session_state.confirmation_mode:
        if button_placeholder.button("DONE / TERMINADO", key="part_checkout_button"):
            if st.session_state.cart:
                st.session_state.confirmation_mode = True
                st.rerun()
            else:
                st.error("Cart is empty. Please add items before checking out.")
                st.rerun()
    else:
        col1, col2 = button_placeholder.columns(2)
        if col1.button("CONFIRM / CONFIRMAR", key="confirm_button"):
            checkout()
        if col2.button("CANCEL / CANCELAR", key="cancel_button"):
            st.session_state.confirmation_mode = False
            st.rerun()

    # JavaScript to set focus on the input box
    components.html(
        """
        <script>
            function setFocus() {
                var input = window.parent.document.querySelector('.stTextInput input');
                if (input) {
                    input.focus();
                    input.select();
                }
            }
            setFocus();
            setTimeout(setFocus, 100);
        </script>
        """,
        height=0
    )


def process_barcode(barcode):
    barcode = barcode.strip()
    if not barcode:
        return

    if barcode in st.session_state.cart:
        # Increment quantity if already in cart
        st.session_state.cart[barcode]['Quantity'] += 1
        st.success(f"Added 1 more {st.session_state.cart[barcode]['ProductName']} to cart")
    else:
        session = get_session()
        try:
            # Query the inventory for the scanned item
            item = session.query(Inventory).filter(Inventory.productID == barcode).first()
            if item:
                st.session_state.cart[barcode] = {
                    'ProductID': item.productID,
                    'ProductName': item.ProductName,
                    'Quantity': 1
                }
                st.success(f"Added {item.ProductName} to cart")
            else:
                st.error(f"Item not found: {barcode}. Please try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
        finally:
            session.close()

def display_cart(placeholder):
    with placeholder.container():
        st.subheader("Current Cart")
        if not st.session_state.cart:
            st.write("Cart is empty")
            return

        # Create a list to hold the rows of our "table"
        table_data = []

        # Prepare the data for each row
        for product_id, item in st.session_state.cart.items():
            table_data.append({
                "Product ID": product_id,
                "Product Name": item['ProductName'],
                "Quantity": item['Quantity'],
                "Remove": product_id  # We'll use this to create unique keys for buttons
            })

        # Convert to DataFrame for easy display
        df = pd.DataFrame(table_data)

        # Display each row of the DataFrame
        for index, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 4, 1, 1])
            with col1:
                st.write(row["Product ID"])
            with col2:
                st.write(row["Product Name"])
            with col3:
                st.write(row["Quantity"])
            with col4:
                if st.button("X", key=f"remove_{row['Remove']}"):
                    remove_item(row['Remove'])
                    st.rerun()

def remove_item(product_id):
    if product_id in st.session_state.cart:
        if st.session_state.cart[product_id]['Quantity'] > 1:
            st.session_state.cart[product_id]['Quantity'] -= 1
        else:
            del st.session_state.cart[product_id]
    st.session_state.focus_counter += 1  # Increment to refocus input

def checkout():
    if not st.session_state.cart:
        st.warning("Cart is empty. Please add items before checking out.")
        return

    if not st.session_state.get('work_order'):
        st.error("No work order selected. Please go back and select a work order.")
        return

    if not st.session_state.get('employee_id'):
        st.error("No employee ID found. Please log in again.")
        return

    session = get_session()
    try:
        current_date = date.today().isoformat()
        
        for product_id, item in st.session_state.cart.items():
            # Create new OrderDetail
            new_order_detail = OrderDetail(
                OrderID=st.session_state.work_order,
                EmployeeID=st.session_state.employee_id,
                ProductID=product_id,
                Quantity=item['Quantity'],
                DateAdded=current_date
            )
            session.add(new_order_detail)
            
            # Update Inventory
            inventory_item = session.query(Inventory).filter(Inventory.productID == product_id).first()
            if inventory_item:
                if inventory_item.QuantityOnHand >= item['Quantity']:
                    inventory_item.QuantityOnHand -= item['Quantity']
                else:
                    raise ValueError(f"Not enough inventory for {item['ProductName']}. Available: {inventory_item.QuantityOnHand}")
            else:
                raise ValueError(f"Product {product_id} not found in inventory.")

        session.commit()
        st.success("Check-out completed successfully!")
        
        # Clear the cart and reset focus
        st.session_state.cart = {}
        st.session_state.focus_counter += 1
        
        # Option to start a new checkout or return to main menu
        if st.button("Start New Checkout"):
            st.session_state.work_order = None
            st.rerun()
        elif st.button("Return to Main Menu"):
            st.session_state.page = 'login'
            st.rerun()

    except ValueError as e:
        session.rollback()
        st.error(str(e))
        st.error("The transaction has been rolled back. Please adjust quantities and try again.")
    except SQLAlchemyError as e:
        session.rollback()
        st.error(f"An error occurred during check-out: {str(e)}")
        st.error("The transaction has been rolled back. Please try again or contact support.")
    finally:
        session.close()

def display_checkout_confirmation():
    st.markdown(
        """
        <style>
        .fullscreen-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            z-index: 999999;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
        }
        .confirmation-content {
            background-color: white;
            color: black;
            padding: 2rem;
            border-radius: 10px;
            width: 80%;
            max-width: 600px;
        }
        .bilingual-button {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 10px;
            margin: 10px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.2rem;
            transition: background-color 0.3s;
        }
        .confirm-button { background-color: #4CAF50; }
        .confirm-button:hover { background-color: #45a049; }
        .cancel-button { background-color: #f44336; }
        .cancel-button:hover { background-color: #da190b; }
        </style>
        """,
        unsafe_allow_html=True
    )

    confirmation_html = f"""
    <div class="fullscreen-overlay">
        <div class="confirmation-content">
            <h2>Confirm Order / Confirmar Pedido</h2>
            <p>Please review your cart before confirming / Por favor revise su carrito antes de confirmar</p>
            <div style="max-height: 200px; overflow-y: auto;">
                {"".join(f"<p>{item['ProductName']} - Quantity: {item['Quantity']}</p>" for item in st.session_state.cart.values())}
            </div>
            <p>Total Items / Artículos Totales: {sum(item['Quantity'] for item in st.session_state.cart.values())}</p>
            <p>Auto-confirm in / Auto-confirmación en: <span id="countdown">{st.session_state.confirm_countdown}</span> seconds / segundos</p>
            <div style="display: flex; justify-content: space-between;">
                <button class="bilingual-button cancel-button" onclick="cancelCheckout()">
                    Cancel / Cancelar
                </button>
                <button class="bilingual-button confirm-button" onclick="confirmCheckout()">
                    Confirm / Confirmar
                </button>
            </div>
        </div>
    </div>
    <script>
        var countdown = {st.session_state.confirm_countdown};
        var countdownElement = document.getElementById('countdown');
        var countdownInterval = setInterval(function() {{
            countdown--;
            countdownElement.textContent = countdown;
            if (countdown <= 0) {{
                clearInterval(countdownInterval);
                confirmCheckout();
            }}
        }}, 1000);

        function cancelCheckout() {{
            clearInterval(countdownInterval);
            window.parent.postMessage({{action: 'cancel_checkout'}}, '*');
        }}

        function confirmCheckout() {{
            clearInterval(countdownInterval);
            window.parent.postMessage({{action: 'confirm_checkout'}}, '*');
        }}
    </script>
    """

    st.components.v1.html(confirmation_html, height=600)

    if st.session_state.confirm_countdown > 0:
        st.session_state.confirm_countdown -= 1
        time.sleep(1)
        st.rerun()

    # Handle messages from JavaScript
    message = st.experimental_get_query_params().get("message")
    if message:
        if message[0] == "cancel_checkout":
            st.session_state.confirm_checkout = False
            st.session_state.confirm_countdown = 120
        elif message[0] == "confirm_checkout":
            checkout()
        st.experimental_set_query_params()
        st.rerun()

if __name__ == "__main__":
    part_checkout()