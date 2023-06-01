import streamlit as st
from src.accID2operon import acc2operon
import pandas as pd

st.set_page_config(page_title="Ligify", layout='wide', initial_sidebar_state='auto')


hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Initialize state variables
if "data" not in st.session_state:
        st.session_state.data = False

if 'SUBMITTED' not in st.session_state:
    st.session_state.SUBMITTED =  False


def _connect_form_cb(connect_status):
    st.session_state.SUBMITTED = connect_status
    st.session_state.data = False




head = st.container()
head1, head2, head3 = head.columns(3)

head2.markdown("<h1 style='text-align: center; color: black;'>Toolkit</h1>", unsafe_allow_html=True)
head2.subheader('Collect information on a regulator')

acc = head2.text_input("RefSeq ID", "AGY77480")



# FORM
with st.form(key='toolkit'):

    # SUBMIT BUTTON
    submit = st.container()
    submit_spacer_1, submit_button, submit_spacer_2 = submit.columns([5,1,5])
    submitted = submit_button.form_submit_button("Submit", use_container_width=True, on_click=_connect_form_cb, args=(True,))





if st.session_state.SUBMITTED:

    operon = acc2operon(acc)
    df = pd.DataFrame(operon["operon"])
    st.write(df)
    st.write(operon["operon_seq"])