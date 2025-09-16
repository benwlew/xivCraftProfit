import streamlit as st

st.title("Test GUI")
st.text("stuff")
st.markdown("""
# I love markdown #
            
            
            
            """)

with st.form("form"):
    st.write("stuff inside form")
    slider_val = st.slider("form slider")
    checkbox_val = st.checkbox("form checkbox")

    submitted = st.form_submit_button("submit")
    if submitted:
        st.write("slider", slider_val, "checkbox", checkbox_val)


tab1, tab2, tab3 = st.tabs(["1","2","3"])

with tab1:
    st.header("1")
    st.markdown("""wow!!!!!!!!""")

st.container()
st.toggle("yes","no")
st.balloons()
st.download_button("yes","no")