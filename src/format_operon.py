import streamlit as st
from src.accID2operon import acc2operon
import pandas as pd
import re


def format_operon(acc):
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
    if operon["reassembly_match"]:
        st.write("Reassembly matches")
    else:
        st.write("Reassembly DOES NOT match")