import streamlit as st
from src.accID2operon import accID2sequence
from src.fetch_metadata import getUniprotData
import pandas as pd




def format_metadata(acc):



        top = st.container()
        top1, spacer, top3, top4 = top.columns((3,0.2, 2,1))


        # Try to fetch data from Uniprot first. If that fails, get it from NCBI
        try:
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


        except:
            # Display the protein sequence
            seq = accID2sequence(acc)
            top1.subheader("Protein seqeunce")
            top1.write(seq)
