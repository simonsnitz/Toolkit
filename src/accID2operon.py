import requests
import re
from pprint import pprint
import xmltodict
import time

#TODO:
# Return a legit error message for the frontend if an error comes up

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'} 

def acc2MetaData(access_id: str):
    
    result = requests.get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id={access_id}&rettype=ipg")
    if result.status_code != 200:
            print("non-200 HTTP response. eFetch failed")

    parsed = xmltodict.parse(result.text)

    protein = parsed["IPGReportSet"]["IPGReport"]["ProteinList"]["Protein"]

    if isinstance(protein, list):
        protein = protein[0]

    if "CDSList" not in protein.keys():
        return "EMPTY"

    CDS = protein["CDSList"]["CDS"]

        #CDS is a list if there is more than 1 CDS returned, otherwise it's a dictionary
    if isinstance(CDS, list):
        CDS = CDS[0]

    proteinDict = {
        "accver":CDS["@accver"],
        "start":CDS["@start"],
        "stop":CDS["@stop"],
        "strand":CDS["@strand"],
    }

    return proteinDict








def NC2genome(genome_id, operon):

    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore"
    startPos = operon[0]["start"]
    stopPos = operon[-1]["stop"]
    response = requests.get(base_url+"&id="+str(genome_id)+"&seq_start="+str(startPos)+"&seq_stop="+str(stopPos)+"&rettype=fasta")


    if response.ok:
        genome = response.text.split("\n")
        genome = "".join(i for i in genome[0:-2] if i[0] != ">")


        ### GENOME FRAGMENT ANNOTATION FUNCTION ###

            ### This deals with one-sided gene overlaps (beginning or end)

            ### It does NOT YET deal with double-sided overlaps (begining AND end)


        out = {}
        counter = 0
        for index in range(0, len(operon)):

            # reset overlap seq
            overlap_seq = ""

            # if you're not at the end...
            if index != len(operon)-1:
                # if END of gene overlaps with START of next gene...
                if operon[index+1]["start"] < operon[index]["stop"]:
                    # truncated gene
                    gene_seq = genome[operon[index]["start"]-startPos : operon[index+1]["start"]-startPos]
                    # overlap region
                    overlap_seq = genome[operon[index+1]["start"]-startPos : operon[index]["stop"]-startPos+1]

                # if you're not at the beginning...
                elif index != 0:
                    # if START of gene overlaps with END of prior gene...
                    if operon[index-1]["stop"] > operon[index]["start"]:
                        # truncated gene
                        gene_seq = genome[operon[index-1]['stop']-startPos+1 : operon[index]['stop']-startPos+1]    
                    else:
                        # full gene
                        gene_seq = genome[operon[index]["start"]-startPos : operon[index]["stop"]-startPos+1]

                # if you're at the beginning
                elif index == 0:     
                    # full gene
                    gene_seq = genome[operon[index]["start"]-startPos : operon[index]["stop"]-startPos+1]  

            # if you ARE at the end...
            elif index == len(operon)-1:
                # see if START of gene overlaps with END of prior gene
                if operon[index-1]["stop"] > operon[index]["start"]:
                    # truncated gene
                    gene_seq = genome[operon[index-1]['stop']-startPos+1 : operon[index]['stop']-startPos+1]    
                else:
                    # full gene
                    gene_seq = genome[operon[index]["start"]-startPos : ]                


            out["gene"+str(counter)] = gene_seq 
            if len(overlap_seq) > 0:
                out["overlap"+str(counter)] = overlap_seq 

            # Append the spacer
            try:
                spacer_seq = genome[operon[index]["stop"]-startPos+1 : operon[index+1]["start"]-startPos]
            except:
                spacer_seq = genome[operon[index]["stop"]-startPos+1 : len(genome)]
            
            
            
            if len(spacer_seq) != 0:
                out["spacer"+str(counter)] = spacer_seq
            
            counter += 1
        
        reconstruct = "".join(i for i in out.values())
        if reconstruct == genome:
            print("matches")
        else:
            print("does not match")


        return out








def getGenes(genome_id, startPos, stopPos):

    # Fetch the genome fragment
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore"
    try:
        response = requests.get(base_url+"&id="+str(genome_id)+"&seq_start="+str(startPos-10000)+"&seq_stop="+str(stopPos+10000)+"&rettype=fasta_cds_aa")
        genome = response.text.split("\n")
    except:
        try:
            response = requests.get(base_url+"&id="+str(genome_id)+"&seq_start="+str(startPos-5000)+"&seq_stop="+str(stopPos+5000)+"&rettype=fasta_cds_aa")
            genome = response.text.split("\n")
        except: 
            try:
                response = requests.get(base_url+"&id="+str(genome_id)+"&seq_start="+str(startPos)+"&seq_stop="+str(stopPos+5000)+"&rettype=fasta_cds_aa")
                genome = response.text.split("\n")
            except:
                try:
                    response = requests.get(base_url+"&id="+str(genome_id)+"&seq_start="+str(startPos-5000)+"&seq_stop="+str(stopPos)+"&rettype=fasta_cds_aa")
                    genome = response.text.split("\n")
                except:
                    print("error fetching the genome fragment")


    re1 = re.compile(str(startPos))
    re2 = re.compile(str(stopPos))
    geneIndex = 0
    regIndex = None
    genes = []
    for i in genome:
        if len(i) != 0:
            if i[0] == '>':
                if re1.search(i):
                    if re2.search(i):
                        regIndex = geneIndex
                geneIndex += 1
                genes.append(i)
    if regIndex == None:
        print("regulator not found in genome")
        return None, None
    else:
        return genes, regIndex





def fasta2MetaData(fasta):
    metaData = {}
    regulator = fasta.split(' [')
    
    for i in regulator:
        if i[:10] == 'locus_tag=':
            metaData['alias'] = i[10:-1]
        elif i[:8] == 'protein=':
            metaData['description'] = i[8:-1].replace("'", "")
        elif i[:11] == 'protein_id=':
            metaData['accession'] = i[11:-1]
        elif i[:9] == 'location=':
            if i[9:20] == 'complement(':
                metaData['direction'] = '-'
                location = i[20:-2]
                location = location.split('..')
                metaData['start'] = int(re.sub("\D", "", location[0]))
                metaData['stop'] = int(re.sub("\D", "", location[1]))
            else:
                metaData['direction'] = '+'
                location = i[9:-1]
                location = location.split('..')
                metaData['start'] = int(re.sub("\D", "", location[0]))
                metaData['stop'] = int(re.sub("\D", "", location[1]))

    if 'accession' not in metaData.keys():
        metaData['accession'] = ""
    
    return metaData





def getOperon(allGenes, index, seq_start, strand):
    '''
    Rules for inclusion/exclusion of genes from operon:
        - always take immediately adjacent genes
        - if query gene is in same direction as regulator, include it.
        - if query gene is expressed divergently from regulator, 
                grab all adjacent genes that are expressed divergently (change strand direction for next genes)
        - if query gene is expressed divergently from a co-transcribed neighbor of the regulaor, 
                grab that gene. (it may be another regulator. Important to know).
        - if query gene direction converges with regulator, exclude it.
    '''

    def getGene(geneStrand, direction, nextGene, geneList, index):
        
        while geneStrand == nextGene['direction']:
            if direction == '+':
                nextIndex = index+1
            elif direction == '-':
                nextIndex = index-1
                
            try:
                nextGene = fasta2MetaData(allGenes[nextIndex])
                
                if abs(seq_start - nextGene['start']) > 8000:       #added this. break if too far away
                    break

                elif geneStrand == '-' and nextGene['direction'] == '+' and direction == '+':
                    geneList.append(nextGene)
                elif geneStrand == '+' and nextGene['direction'] == '-' and direction == '-':
                    geneList.append(nextGene)
                elif geneStrand == nextGene['direction']:
                    geneList.append(nextGene)
                index = nextIndex
            except:
                break

    geneStrand = strand
    
    #attempt to get downstream genes, if there are any genes downstream
    try:
        indexDOWN = index-1
        downGene = fasta2MetaData(allGenes[indexDOWN])
        #if seq_start > downGene['start']:
        if strand == '+' and downGene['direction'] == '-':
            geneStrand = downGene['direction']
    
        downgenes = [downGene]
        getGene(geneStrand,'-',downGene, downgenes, indexDOWN)
    
        geneArray = list(reversed(downgenes))
    except:
        geneArray = []

    geneArray.append(fasta2MetaData(allGenes[index]))
    regulatorIndex = (len(geneArray)-1)

    geneStrand = strand
    
    #attempt to get upstream genes, if there are any genes upstream
    try:
        indexUP = index+1
        upGene = fasta2MetaData(allGenes[indexUP])
        #if seq_start > upGene['start']:
        if strand == '-' and upGene['direction'] == '+':
            geneStrand = upGene['direction']
        
        geneArray.append(upGene)

        getGene(geneStrand, '+', upGene, geneArray, indexUP)
    except:
        return geneArray, regulatorIndex


    return geneArray, regulatorIndex






def acc2operon(accession):


    metaData = acc2MetaData(accession)


    if metaData != "EMPTY":
        genes, index = getGenes(metaData["accver"], int(metaData["start"]), int(metaData["stop"]))

        if index != None:
            reg = fasta2MetaData(genes[index])

            operon, regIndex = getOperon(genes, index, reg['start'], reg['direction'])
            # operon_sequence = NC2genome(metaData["accver"], operon[0]["start"], operon[-1]["stop"])
            operon_sequence = NC2genome(metaData["accver"], operon)

            data = {"operon": operon, "protein_index": regIndex, "operon_seq": operon_sequence }

            # For recording process speeds
            # print("acc2MetaData time: "+str(acc2MetaData_end - acc2MetaData_start))
            # print("getGenes time: "+str(getGenes_end - acc2MetaData_start))
            # print("fasta2MetaData time: "+str(fasta2MetaData_end - getGenes_end))
            # print("getOperon time: "+str(getOperon_end - fasta2MetaData_end))
            
            return data
        else:
            return "EMPTY"
    else:
        return "EMPTY"



    # Input protein accession ID, output sequence in fasta format
def accID2sequence(accID: str):
    URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi/?db=protein&id="+accID+"&rettype=fasta"
    response = requests.get(URL)
    if response.ok:
        fasta = response.text.split("\n")
        fasta = [i for i in fasta if len(i) != 0]
        fasta = "".join(i for i in fasta if i[0] != ">")

        return fasta
    else:
        print("FATAL: Bad eFetch request "+ str(response.status_code))
        return None



if __name__ == "__main__":
    
    #pprint(acc2operon("WP_187140699.1"))

    #print(NC2genome("CP006763.1", 3531534, 3540271))

    #data = acc2operon("AAK24363")

    #print(data["operon_seq"])

    # print(NC2genome("CP006763.1", operon, colors))

    accID2sequence("AGY77480")



