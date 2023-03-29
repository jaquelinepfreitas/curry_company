import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
)

image_path = 'vetor.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width=180)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('# Curry Company Growth Dahsboard')