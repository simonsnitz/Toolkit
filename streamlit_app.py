import streamlit as st
from src.format_operon import format_operon
from src.format_metadata import format_metadata
from pprint import pprint

st.set_page_config(page_title="Toolkit", layout='wide', initial_sidebar_state='auto')


hide_streamlit_style = '''
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
'''
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# Removes border around forms
css = r'''
    <style>
        [data-testid="stForm"] {border: 0px}
    </style>
'''
st.markdown(css, unsafe_allow_html=True)


# Removes the full-screen button for various elements
style_fullscreen_button_css = """
    button[title="View fullscreen"] {
        display: none;
    }
    button[title="View fullscreen"]:hover {
        display: none;
        }
    """
st.markdown(
    "<style>"
    + style_fullscreen_button_css
    + "</styles>",
    unsafe_allow_html=True,
)



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
head2.markdown("<h3 style='text-align: center; color: black;'>Collect information on a regulator</h3>", unsafe_allow_html=True)

acc = head2.text_input("RefSeq ID", "AGY77480")



# FORM
with st.form(key='toolkit'):

    # SUBMIT BUTTON
    submit = st.container()
    submit_spacer_1, submit_button, submit_spacer_2 = submit.columns([5,1,5])
    submitted = submit_button.form_submit_button("Submit", use_container_width=True, on_click=_connect_form_cb, args=(True,))




if st.session_state.SUBMITTED:


    with st.spinner("Collecting protein metadata"):
    
        top = st.container()
        top1, spacer, top3, top4 = top.columns((3,0.2, 2,1))
        format_metadata(acc)

    st.divider()




    with st.spinner("Collecting genome context"):

        format_operon(acc)