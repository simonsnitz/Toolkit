import requests
import json
from pprint import pprint


def getUniprotData(acc):
    response = requests.get("https://rest.uniprot.org/uniprotkb/search?query="+str(acc)+"&format=json")
    if response.ok:
        data = json.loads(response.text)['results'][0]

        # pprint(data)

        annotationScore = data['annotationScore']
        try:
            annotation = data['proteinDescription']['recommendedName']['fullName']['value']
        except:
            annotation = ""
        uniprotID = data['primaryAccession']
        organism = data['organism']['scientificName']
        lineage = data['organism']['lineage']
        seq = data['sequence']['value']
        try:
            orf_name = data['genes'][0]['orfNames'][0]['value']
        except:
            orf_name = ""

        refseq = ""
        embl = ""
        for i in data['uniProtKBCrossReferences']:
            if i['database'] == "RefSeq":
                refseq = i['id']
            elif i['database'] == "EMBL":
                embl = i['id']

        try:
            dois = []
            for ref in data["references"]:
                for citation in ref["citation"]["citationCrossReferences"]:
                    if citation['database'] == 'DOI':
                        dois.append({"doi":citation['id'], "title": ref["citation"]["title"]})
        except:
            dois = []

        out = {
            "annotationScore": annotationScore,
            "annotation": annotation,
            "uniprotID": uniprotID,
            "refseq": refseq,
            "EMBL": embl,
            "organism": organism,
            "lineage": lineage,
            "seq": seq,
            "orf_name": orf_name,
            "references": dois
        }
        return out

    else:
        response.raise_for_status()
        print('Error with HTTPS request for UniprotKB')



if __name__ == "__main__":

    getOrgAndSeq('AGY77480')