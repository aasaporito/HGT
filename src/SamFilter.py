import pprint

import tqdm
import os
import pickle


class SamFilter:
    def __init__(self, input_sam, ref_fasta, output_fasta):
        self.write_buffer = []
        self.relevant_genomes = set()
        self.reference_fasta = ref_fasta
        self.output_sam = output_fasta
        self.input_sam = input_sam

        # self.relevant_genomes = pickle.load(open("samfilt.pkl", 'rb'))
        # pprint.pprint(self.relevant_genomes)

    def extract_relevant_genomes(self):
        with tqdm.tqdm(total=os.path.getsize(self.input_sam)) as pbar:
            with open(self.input_sam, "r") as infile:
                for line in infile:
                    pbar.update(len(line))
                    line = line[:-1]
                    self.relevant_genomes.add(line)
                    # if line[0] != '@':
                    #     split_line = line.split('\t')
                    #     genome = split_line[2]
                    #
                    #
                    #     if genome != '*':
                    #         self.relevant_genomes.add(genome)
        print('Created filter set from aligned SAM')
        print(f"{len(self.relevant_genomes)} genomes to filter")
        
        # with open("samfilt.pkl", "wb") as f:
        #     pickle.dump(self.relevant_genomes, f)
        # pprint.pprint(self.relevant_genomes)
    def filter_ref_file(self):
        with tqdm.tqdm(total=os.path.getsize(self.reference_fasta)) as pbar:
            with open(self.reference_fasta, "r") as infile:
                with open(self.output_sam, "w") as outfile:
                    input_buffer = ""
                    reading_line = False
                    pbar_buffer = 0
                    while True:  # TODO : Read multi line at once
                        next_line = infile.readline()
                        if not next_line:
                            break
                        next_char = next_line[0]

                        if next_char == '>':
                            reading_line = not reading_line
                            input_buffer += next_line
                            next_char = ""

                        if next_char != '>' and reading_line:
                            input_buffer += next_line
                        else:
                            line = "".join(input_buffer.splitlines(True)[:-1])
                            if line[0] == '>' and reading_line is False:
                                # print(line)
                                pbar_buffer += len(line)
                                if pbar_buffer > 1_000_000:
                                    pbar.update(pbar_buffer)
                                    pbar_buffer = 0
                                input_buffer = "".join(input_buffer.splitlines(True)[-1:])
                                reading_line = not reading_line

                                split_line = line[1:-1]
                                genome = split_line.split(' ')[0]
                                # print(genome)
                                # Read char by char until >, treat that as input buffer?
                                if genome in self.relevant_genomes:
                                    pbar.update(pbar_buffer)
                                    pbar_buffer = 0

                                    # print("Adding to relevant genomes!")
                                    # print(genome)
                                    write_out = line[:-1]
                                    if write_out[-1] != "\n":
                                        write_out += "\n"

                                    self.write_buffer.append(write_out)
                            else:
                                write_out = line
                                print(write_out)
                                print("Head up!")

                            if len(self.write_buffer) > 100:
                                outfile.write("".join(self.write_buffer))
                                self.write_buffer = []
                    if len(self.write_buffer) > 0:
                        outfile.write("".join(self.write_buffer))
                        self.write_buffer = []


filt = SamFilter("/media/aaron/T9/HGT/testing/genomes_to_filt.txt", "/media/aaron/T9/all_bacteria.fasta",
                 'PB644_EB813_REF.fasta')
filt.extract_relevant_genomes()
filt.filter_ref_file()
