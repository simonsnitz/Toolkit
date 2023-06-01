import streamlit as st
from src.accID2operon import acc2operon, accID2sequence
from src.fetch_metadata import getUniprotData
import pandas as pd
import re

st.set_page_config(page_title="Ligify", layout='wide', initial_sidebar_state='auto')


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


    top = st.container()
    top1, top2, top3 = top.columns((2,1,1))
    # Fetch protein sequence

    metadata = getUniprotData(acc)

    #seq = accID2sequence(acc)
    top1.subheader("Protein seqeunce")
    top1.write(metadata['seq'])

    taxonomy_names = ["Domain", "Phylum", "Class", "Order", "Family", "Genus"]
    lineageDict = {}
    for i in range(0, len(metadata['lineage'])):
        lineageDict[taxonomy_names[i]] = metadata['lineage'][i]

    lineageDF = pd.DataFrame(lineageDict, index=["Lineage",])
    lineageDF = lineageDF.T
    top2.dataframe(lineageDF)

    st.divider()


    # Fetch operon data
    operon = acc2operon(acc)

    # create color-coded alias map
    colors = ["#ff9e9e", "#b9abff", "#8fffa3", "#ffc38f", "#8ffff4", "#fdff8f", "#c3ccfa", "#ffabf7"]
        #colors = ["#red", "#purple", "#green", "#orange", "lightblue", "yellow", "blue", "pink"]
    cmap = {}
    c = 0
    for i in operon["operon"]:
        cmap[i["alias"]] = str(colors[c % len(colors)])
        c += 1

    # Color and display the operon data table
    def color_survived(val):
        color = cmap[val]
        return f'background-color: {color}'


    op = st.container()
    operon1, operon2 = op.columns(2)

    operon1.subheader("Operon table")
    df = pd.DataFrame(operon["operon"])
    operon1.dataframe(df.style.applymap(color_survived, subset=["alias"]))

    operon2.subheader("Predicted promoter")
    operon2.write(operon["promoter"]['regulated_seq'])


    # Create and display the color-annotated genome fragment
    operon_seq = ""

    c = 0
    for seq in operon["operon_seq"]:
        sequence = operon["operon_seq"][seq]

        if re.compile(r"spacer").search(seq):
            html = "<span style='color: grey;'>"+str(sequence)+"</span>"
        elif re.compile(r"overlap").search(seq):
            html = "<span style='color: red;'>"+str(sequence)+"</span>"
        else:
            html = f"<span style='background: {colors[c % len(colors)]};'>"+str(sequence)+"</span>"
            c += 1
        operon_seq += html

        
    st.subheader("Operon sequence")
    st.markdown(operon_seq, unsafe_allow_html=True)
