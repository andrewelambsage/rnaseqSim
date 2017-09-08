#!/usr/bin/env python

import subprocess
import argparse
import os
#import gzip
import gffutils
import fusions
import seqobjs
import random
import time
from Bio import SeqIO

def run_module(genome_file, gtf_file, numEvents, simName, 
               add_mid_exon_fusions = False, 
               add_sense_antisense_fusions = False,
               add_exon_duplications_and_deletions = False,
               add_fusion_events_in_UTR = False):

    # Converting GTF file into a database
    database_filename = '.'.join([os.path.basename(gtf_file).rstrip('.gtf'), 'sqlite3'])     
    dbPath = os.path.join(os.path.dirname(gtf_file),database_filename)
    print(dbPath)

    if os.path.isfile(dbPath):
        # Connect to an already-existing db
        db = gffutils.FeatureDB(dbPath)
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
    
    hg19 = seqobjs.readGenome(genome_file)
    fastaFilenames = list()    

    with open(''.join([simName, '.gtf']),'w') as gtf, open(''.join([simName, '_filtered.bedpe']),'w') as bedpe:
    # Get fusion events as tuples of Bio.Seq objects
    # TODO: Simplify return objects, possibly returning one event at a time instead of list
        for fusion_event in fusions.getRandomFusions(
            db = db, names = protein_coding_genes, num = numEvents):
            if add_mid_exon_fusions:
                fusion_event.add_mid_exon_fusion_breakpoints()
            if add_sense_antisense_fusions:
                fusion_event.add_sense_antisense_fusions()
            if add_exon_duplications_and_deletions:
                fusion_event.add_exon_duplications_and_deletions()
            if add_fusion_events_in_UTR:
                fusion_event.add_fusion_events_in_UTR()
            print(fusion_event)
            fObj = seqobjs.makeFusionSeqObj(
                donorExonSeq = fusion_event['donorExons'], 
                acceptorExonSeq = fusion_event['acceptorExons'],
                dJunc = fusion_event['dJunction'],
                aJunc = fusion_event['aJunction'],
                genomeObj = hg19)
            print("---")
            print(fObj)
            print("---")
            #print(len(fObj))
            seqobjs.writeGTF(fObj,gtf)
            seqobjs.writeBEDPE(fObj,bedpe)
            SeqIO.write(fObj, ''.join([fObj.id,'.fasta']), "fasta")
            fastaFilenames.append(''.join([fObj.id,'.fasta']))
    
    return(fastaFilenames)
    
    

def makeFusionReference(fastaList, simName, numEvents):
   '''Runs RSEM to make reference for fusion events.'''
   
   cmd = ' '.join(['rsem-prepare-reference --gtf', simName+'.gtf', '--star --num-threads 4', ','.join(fastaList), '_'.join([simName, str(numEvents), 'ev'])])
   print(cmd)
   subprocess.call(cmd, shell=True)


    
if __name__ == '__main__':


    parser = argparse.ArgumentParser("Runs workflow to generate fusion events and truth file.")
    parser.add_argument('--genome', default='/external-data/Genome/genomes/Hsapiens_Ensembl_GRCh37/primary_nomask/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa', help='Reference Genome.', type=str, required=False)
    parser.add_argument('--gtf', default='/external-data/Genome/gene_models/Hsapiens_Ensembl_v75_refonly.gtf', help='Gene models in GTF format.', type=str, required=False)
    parser.add_argument('--numEvents', default=5, help='Number of filtered fusion events to generate.', type=int, required=False)
    parser.add_argument('--minLength', default=400, help='Minimum length of fusion transcript.', type=int, required=False)
    parser.add_argument("--simName", help="Prefix for the simulation filenames.", default='testSimulation', required=False)
    parser.add_argument("--seed", 
                        help = "Seed number to use for RSEM read simulation.", 
                        type = int, 
                        required = False, 
                        default = None)
    parser.add_argument('--mid_exon_fusions', 
                        action = 'store_true', 
                        help = 'whether to add mid exon fusions')   
    args = parser.parse_args()
    
    # set seed to seed arument, otherwise to time
    if isinstance(args.seed, (int, long)):
        random.seed(args.seed)
    else: 
        random.seed(time.time)
    
    fastaFN = run_module(genome_file = args.genome, 
                         gtf_file = args.gtf,
                         numEvents = args.numEvents, 
                         simName = args.simName,
                         add_mid_exon_fusions = args.mid_exon_fusions)
                         
    makeFusionReference(fastaList = fastaFN, 
                        simName = args.simName, 
                        numEvents = args.numEvents)
