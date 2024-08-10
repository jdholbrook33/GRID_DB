import streamlit as st
import streamlit.components.v1 as components

def display_keypad():
    # Custom CSS for the keypad
    custom_css = """
    <style>
        #keypad {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            max-width: 500px;
            margin: auto;
        }
        .key {
            font-size: 24px;
            padding: 20px;
            text-align: center;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .number {
            background-color: white;
            color: black;
        }
        .function {
            background-color: #007bff;
            color: white;
        }
        #done {
            background-color: #ffd700;
            color: black;
            font-weight: bold;
            grid-column: span 3;
            font-size: 28px;
        }
        #display {
            grid-column: span 3;
            background-color: #f0f0f0;
            padding: 20px;
            font-size: 28px;
            text-align: right;
            margin-bottom: 10px;
            border-radius: 10px;
        }
    </style>
    """

    # HTML for the keypad
    keypad_html = """
    <div id="keypad">
        <div id="display"></div>
        <button class="key number">7</button>
        <button class="key number">8</button>
        <button class="key number">9</button>
        <button class="key number">4</button>
        <button class="key number">5</button>
        <button class="key number">6</button>
        <button class="key number">1</button>
        <button class="key number">2</button>
        <button class="key number">3</button>
        <button class="key function" id="clear">C</button>
        <button class="key number">0</button>
        <button class="key function" id="backspace">⌫</button>
        <button class="key" id="done">DONE</button>
    </div>
    """

    # JavaScript for keypad functionality
    keypad_js = """
    <script>
        const display = document.getElementById('display');
        const keys = document.querySelectorAll('.key');
        let currentValue = '';

        keys.forEach(key => {
            key.addEventListener('click', () => {
                const value = key.textContent;
                if (value === 'C') {
                    currentValue = '';
                } else if (value === '⌫') {
                    currentValue = currentValue.slice(0, -1);
                } else if (value === 'DONE') {
                    // Here you can add code to submit the value
                    console.log('Submitted:', currentValue);
                } else {
                    currentValue += value;
                }
                display.textContent = currentValue;
            });
        });
    </script>
    """

    # Combine all HTML, CSS, and JavaScript
    full_html = f"{custom_css}<div style='padding: 20px;'>{keypad_html}</div>{keypad_js}"

    # Render the custom component
    components.html(full_html, height=600)

    # Add a link to the checkout section
    if st.button("Go to Checkout", key="checkout_button"):
        st.session_state.page = "checkout"

# Remove the if __name__ == "__main__": block as it's not needed here