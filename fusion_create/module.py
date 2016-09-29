
import sys
import os
#import gzip
import gffutils
import fusions
import seqobjs
from Bio import SeqIO


def run_module(genome_file, gtf_file, numEvents):

    # Converting GTF file into a database
    database_filename = '.'.join([os.path.basename(gtf_file).rstrip('.gtf'), 'sqlite3'])     

    if os.path.isfile(database_filename):
        # Connect to an already-existing db
        db = gffutils.FeatureDB(database_filename)
    else:
        # Or, create a new one
#        db = gffutils.create_db(gtf_file,database_filename)
        db = gffutils.create_db(gtf_file,database_filename,disable_infer_genes=True, disable_infer_transcripts=True)

    # Filter the gene types to consider, e.g. protein-coding
    protein_coding_genes = list()
    allGenesIter = db.features_of_type("gene")
    for item in allGenesIter:
        if item['gene_biotype'][0] == 'protein_coding':
            protein_coding_genes.append(item.id)

    # Get the number of genes available after filtering     
    print(' '.join(['Number of protein-coding genes:', str(len(protein_coding_genes))]))
    
    hg19 = seqobjs.readGenome(sys.argv[1])    

    with open('test.gtf','w') as gtf, open('test.bedpe','w') as bedpe:
    # Get fusion events as tuples of Bio.Seq objects
    # Need to simplify return objects, possibly returning one event at a time instead of list
       for event in fusions.getRandomFusions(db=db, names=protein_coding_genes, num=numEvents):
           fObj = seqobjs.makeFusionSeqObj(donorExonSeq=event['donorExons'], acceptorExonSeq=event['acceptorExons'], dJunc=event['dJunction'],aJunc=event['aJunction'],genomeObj=hg19)
           print(len(fObj))
#           print(fObj)
           seqobjs.writeGTF(fObj,gtf)
           seqobjs.writeBEDPE(fObj,bedpe)
           SeqIO.write(fObj, ''.join([fObj.id,'.fasta']), "fasta")
    
    
    
if __name__ == '__main__':
    run_module(genome_file=sys.argv[1], gtf_file=sys.argv[2],numEvents=int(sys.argv[3]))