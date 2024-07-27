import os
import tqdm
import gzip


class Fragmenter:
    def __init__(self, input_file, fragments_per_seq, min_matched_frags):
        self.sequence_dict = {}
        self.unaligned_seq_list = []
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"

        self.sam_file = input_file
        self.fragments_per_seq = fragments_per_seq

    def find_unaligned_seqs(self):
        print("Processing SAM input:")
        if self.sam_file.endswith(".sam"):
            with tqdm.tqdm(total=os.path.getsize(self.sam_file)) as pbar:
                with open(self.sam_file, "r") as infile:
                    for line in infile:
                        pbar.update(len(line))
                        if line[0] != '@':
                            line = line.split('\t')
                            sequence_name = line[0]
                            is_aligned = (line[2] != '*')
                            sequence = line[9]

                            if sequence_name in self.sequence_dict:
                                self.sequence_dict[sequence_name] = [(is_aligned and self.sequence_dict[sequence_name][0]),
                                                                     sequence, sequence_name]

                                # If sequence is aligned we don't need to store its sequence.
                                if self.sequence_dict[sequence_name][0]:
                                    self.sequence_dict[sequence_name][1] = None

                            else:
                                if sequence != '*':
                                    self.sequence_dict[sequence_name] = [is_aligned, sequence, sequence_name]
        # elif self.sam_file.endswith(".gz"): # TODO REWRITE cleaner
        #     with tqdm.tqdm(total=os.path.getsize(self.sam_file)) as pbar:
        #         with gzip.open(self.sam_file, "r") as infile:
        #             for line in infile:
        #                 line = line.decode()
        #                 pbar.update(len(line))
        #
        #                 if line[0] != '@':
        #                     line = line.split('\t')
        #                     sequence_name = line[0]
        #                     is_aligned = (line[2] != '*')
        #                     sequence = line[9]
        #                     if sequence == "*":
        #                         continue
        #
        #                     if sequence_name in self.sequence_dict:
        #                         self.sequence_dict[sequence_name] = [(is_aligned and self.sequence_dict[sequence_name]),
        #                                                              sequence, sequence_name]
        #                         # If sequence is aligned we don't need to store its sequence.
        #                         if self.sequence_dict[sequence_name][0]:
        #                             self.sequence_dict[sequence_name][1] = None
        #
        #                     else:
        #                         self.sequence_dict[sequence_name] = [is_aligned, sequence, sequence_name]

        for sequence in self.sequence_dict.values():
            is_aligned = sequence[0]
            seq_name = sequence[2]
            sequence = sequence[1]
            if not is_aligned:
                self.unaligned_seq_list.append((seq_name, sequence))

        del self.sequence_dict
        print("Completed SAM Processing")

    def fragment_seq(self):
        print("Slicing unaligned sequences:")
        with open(f"{self.temp_dir}/fragments.fasta", "w") as outfile:
            for sequence_name, sequence in tqdm.tqdm(self.unaligned_seq_list):
                frag_len = len(sequence) // self.fragments_per_seq

                for i in range(self.fragments_per_seq):
                    start_idx = i * frag_len
                    end_idx = start_idx + frag_len if i != self.fragments_per_seq - 1 else len(sequence)

                    label = i + 1
                    outfile.write(f">{sequence_name}_frag_{label}\n")
                    outfile.write(f"{sequence[start_idx:end_idx]}\n")

        del self.unaligned_seq_list
        print("Completed Fragment Sequence Processing")
        print(f"Fasta for alignment generated at: {self.temp_dir}/fragments.fasta")

    #  Will always be given a .sam file processed to only include aligned sequences (--sam-hit-only)





# Standard run of X chunks fragmenter version.
# finder = Fragmenter("/media/aaron/T91/splits/part_0.sam", 10, 10)
# finder.find_unaligned_seqs()
# finder.fragment_seq()
# del finder
#
# fragAnalyzer = FragAnalyzer()
# fragAnalyzer.realign_fragments()
# fragAnalyzer.recollect_fragments()
