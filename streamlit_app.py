import streamlit as st
from src.accID2operon import acc2operon, accID2sequence
from src.fetch_metadata import getUniprotData
import pandas as pd
import re
from pprint import pprint

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
        top1, top2, top3, top4 = top.columns((3,0.2, 2,1))

        # Get protein metadata
        metadata = getUniprotData(acc)

        # Display the protein sequence
            #seq = accID2sequence(acc)
        top1.subheader("Protein seqeunce")
        top1.write(metadata['seq'])


        # Display associated publications
        top1.subheader("References")
        for ref in metadata["references"]:
            top1.caption(ref["title"])
            top1.markdown(f'- <a target="__blank">{"https://doi.org/"+ref["doi"]}</a>', unsafe_allow_html=True)



        # Create the metadata table
        metadata_dict = {}
        metadata_dict["Annotation"] = metadata["annotation"]
        metadata_dict["Annotation score"] = metadata["annotationScore"]
        metadata_dict["Uniprot ID"] = metadata["uniprotID"]
        metadata_dict["RefSeq"] = metadata["refseq"]
        metadata_dict["EMBL"] = metadata["EMBL"]
        metadata_dict["ORF name"] = metadata["orf_name"]
        metadata_dict["Organism"] = metadata["organism"]

        metadata_DF = pd.DataFrame(metadata_dict, index=["Protein metadata",])
        metadata_DF = metadata_DF.T
        top3.subheader("Protein metadata")
        top3.dataframe(metadata_DF, use_container_width=True)


        # Create the Phylogeny table
        taxonomy_names = ["Domain", "Phylum", "Class", "Order", "Family", "Genus"]
        lineage_dict = {}
        for i in range(0, len(metadata['lineage'])):
            lineage_dict[taxonomy_names[i]] = metadata['lineage'][i]

        lineage_DF = pd.DataFrame(lineage_dict, index=["Lineage",])
        lineage_DF = lineage_DF.T
        top4.subheader("Organism lineage")
        top4.dataframe(lineage_DF, use_container_width=True)




        st.divider()


    with st.spinner("Collecting genome context"):


        # Fetch operon data
        operon = acc2operon(acc)

        # create color-coded alias map
        colors = ["#ff9e9e", "#b9abff", "#8fffa3", "#ffc38f", "#8ffff4", "#fdff8f", "#c3ccfa", "#ffabf7"]
        #colors = ["#red", "#purple", "#green", "#orange", "lightblue", "yellow", "blue", "pink"]

        # Color and display the operon data table

        op = st.container()
        operon1, operon2 = op.columns(2)

        operon1.subheader("Operon table")
        df = pd.DataFrame(operon["operon"])
        # pprint(df)


        def bg_color_col(col):
            color = [colors[i % len(colors)] for i,x in col.items()]
            return ['background-color: %s' % color[i]
                        if col.name=='alias' or i==operon['protein_index']   # color column `Total` or row `4`
                        else ''
                    for i,x in col.items()]

        df = df.style.apply(bg_color_col)


        operon1.dataframe(df)

        operon2.subheader("Predicted promoter")
        try:
            operon2.write(operon["promoter"]['regulated_seq'])
        except:
            pass


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
