import os
import subprocess
import tqdm


class UnalignedSeqFinder:
    def __init__(self, sam_file, output_file="results"):
        self.sam_file = sam_file
        self.sequence_dict = {}
        self.unaligned_seq_list = []
        self.realigned_seqs = {}

        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"
        self.output_file = output_file

    def process_sam(self):
        print("Processing SAM input:")

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
                            self.sequence_dict[sequence_name] = [(is_aligned and self.sequence_dict[sequence_name]),
                                                                 sequence, sequence_name]
                            if self.sequence_dict[sequence_name][
                                0]:  # If sequence is aligned we don't need to store its sequence.
                                self.sequence_dict[sequence_name][1] = None

                        else:
                            self.sequence_dict[sequence_name] = [is_aligned, sequence, sequence_name]

        for sequence in self.sequence_dict.values():
            is_aligned = sequence[0]
            seq_name = sequence[2]
            sequence = sequence[1]
            if not is_aligned:
                self.unaligned_seq_list.append((seq_name, sequence))
                # if not is_aligned:
                #     with open(f"{self.temp_dir}/unaligned_seqs.gt", "a") as f:
                #         f.write(f"{sequence_name}\t{sequence}\n")
                # self.unaligned_seq_list.append((sequence_name, sequence))
        del self.sequence_dict
        print("Completed SAM Processing")

    def fragment_seq(self, slices=10):
        print("Slicing unaligned Sequences:")
        with open(f"{self.temp_dir}/unaligned_seq_frags.fasta", "w") as outfile:
            # with tqdm.tqdm(total=os.path.getsize(f"{self.temp_dir}/unaligned_seqs.gt")) as pbar:
            # with open(f"{self.temp_dir}/unaligned_seqs.gt", "r") as f:
            # for line in f:
            # pbar.update(len(line))
            # sequence_name, sequence = line.split('\t')
            for sequence_name, sequence in tqdm.tqdm(self.unaligned_seq_list):
                frag_len = len(sequence) // 10

                for i in range(slices):
                    start_idx = i * frag_len
                    end_idx = start_idx + frag_len if i != slices - 1 else len(sequence)

                    outfile.write(f">{sequence_name}_frag_{i + 1}\n")
                    outfile.write(f"{sequence[start_idx:end_idx]}\n")

        del self.unaligned_seq_list
        print("Completed Fragment Sequence Processing")

    def realign_fragments(self):
        print("Running minimap2 to realign reads")
        # f = open(f"{self.temp_dir}/realigned.sam", "w")
        # # minimap2-2.28_x64-linux/minimap2 -t 5 -I 2G -K 300M -w 25 -ax map-hifi --sam-hit-only all_bacteria.fasta.gz unaligned_seq_frags.fasta out> 'realigned.sam'
        # subprocess.run(
        #     [f"{self.parent_dir}/Tools/minimap2-2.28_x64/minimap2", "-t 5", "-I 1G", "-n 200M", "-w 25", "-ax",
        #      "map-hifi", "--sam-hit-only", "/media/aaron/FF7F-91E7/all_bacteria.fasta.gz",
        #      f"{self.temp_dir}/unaligned_seq_frags.fasta"], stdout=f)
        # f.close()
        subprocess.run(f"{self.parent_dir}/Tools/minimap2-2.28_x64/minimap2 -t 5 -I 3G -K 400M -w 25 -ax map-hifi --sam-hit-only /media/aaron/FF7F-91E7/all_bacteria.fasta.gz {self.temp_dir}/unaligned_seq_frags.fasta > '{self.temp_dir}/realigned.sam'", shell=True)
        print("Completed realignment")

    #  Will always be given a .sam file processed to only include aligned sequences (--sam-hit-only)
    def recollect_fragments(self, min_frags=10):
        print("Analyzing realigned fragments")
        with tqdm.tqdm(total=os.path.getsize(f"{self.temp_dir}/realigned.sam")) as pbar:
            with open(f"{self.temp_dir}realigned.sam", "r") as infile:
                for line in infile:
                    pbar.update(len(line))

                    if line[0] != '@':
                        line = line.split('\t')
                        seq_name = line[0]
                        genome = line[2]
                        alignment_score = int(line[13][5:])

                        if seq_name in self.realigned_seqs.keys():
                            old_score = self.realigned_seqs[seq_name][1]
                            if alignment_score > old_score:
                                self.realigned_seqs[seq_name] = [genome, alignment_score]
                                continue
                            else:
                                continue
                        else:
                            self.realigned_seqs[seq_name] = [genome, alignment_score]

        seq_dict = {}
        for frag_name, entry in self.realigned_seqs.items():
            seq_name = frag_name.split("/ccs_frag_")[0]
            genome = self.realigned_seqs[frag_name][0]
            alignment_score = self.realigned_seqs[frag_name][1]
            if seq_name not in seq_dict.keys():
                seq_dict[seq_name] = SequenceData(seq_name)

            seq_dict[seq_name].genomes.add(genome)
            seq_dict[seq_name].fragments.add(frag_name)
            seq_dict[seq_name].pairs.append([frag_name, genome, alignment_score])

        # print(seq_dict)
        output = ""
        for entry in seq_dict.values():
            frag_count = len(entry.fragments)
            genome_count = len(entry.genomes)

            # Not enough aligned fragments or not enough species -> no results
            if genome_count < 2 or frag_count < min_frags:
                continue

            for pair in sorted(entry.pairs, key=lambda pair: pair[1]):
                output_str = f"{pair[0]}\t{pair[1]}\tAS:i:{str(pair[2])}\n"
                output += output_str
                # print(output_str)
            output += "\n"
            # output_str = f"{seq_name}\t{genome}\tAS:i:{str(alignment_score)}\n"
            # output += output_str

        with open(f"{self.parent_dir}/Output/{self.output_file}.txt", "w") as f:
            f.write(output)

        print(f"Results generated at: HGT/Output/{self.output_file}.txt")

class SequenceData:
    def __init__(self, sequence):
        self.sequence = sequence
        self.genomes = set()
        self.fragments = set()
        self.pairs = []

    def __repr__(self):
        return f"({self.sequence}, {self.genomes}, {self.fragments}, {self.pairs})"


finder = UnalignedSeqFinder("/media/aaron/FF7F-91E7/Raw Data/PB644_EB813.hifi_reads.sam", "res1")
finder.process_sam()
finder.fragment_seq()
finder.realign_fragments()  # syscall
finder.recollect_fragments()

#CL:minimap2 -w 25 -ax map-hifi ../../../mnt/c/Users/sdouglass/Desktop/Research_Projects/Anne Metagenomics/all_complete_Gb_bac_MINUS_Corynebacterium_jeikeium_PLUS_OTHERS.fasta.gz ../../../mnt/c/Users/sdouglass/Desktop/Research_Projects/Metagenomics_Simulation/Raw_Data/PB644_EB813.hifi_reads.fasta.gz
