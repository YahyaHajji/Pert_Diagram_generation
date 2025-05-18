import streamlit as st

st.title("Streamlit Test App")
st.write("If you can see this, Streamlit is working correctly!")

number = st.slider("Select a number", 0, 100, 50)
st.write(f"You selected: {number}")

if st.button("Click me"):
    st.success("Button clicked!")
