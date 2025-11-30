import streamlit as st
import pandas as pd

st.title("First page")
st.subheader("This is a subheader")

name = st.text_input("Enter a name")
if st.button("Submit"):
    st.success(f"Hello {name}")

df = pd.DataFrame({
    "User": ["Alice", "Bob", "Charlie"],
    "Score": [52, 60, 88]
})

st.dataframe(df)
