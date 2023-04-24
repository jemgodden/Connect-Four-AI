import streamlit as st


num_cols = 7

for col in st.columns(num_cols):
    with col:
        st.button('Drop counter')

col = st.columns(1)


