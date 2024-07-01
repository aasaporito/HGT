import os
import subprocess
import tqdm
import tomllib


class FragAnalyzer:
    def __init__(self, output_file="results"):
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"

        with open(self.parent_dir + "/settings.toml", 'rb') as f:
            toml = tomllib.load(f)

        self.ref_file = toml["minimap2"]["reference-file"]
        self.output_file = output_file
        self.min_matched_frags = toml['settings']['min-matched-frags']
        self.args_minimap = toml["minimap2"]["options"]
        self.realigned_seqs = {}

    def realign_fragments(self):
        print("Running minimap2 to realign reads")
        subprocess.run(
            f"{self.parent_dir}/Tools/minimap2-2.28_x64/minimap2 {self.args_minimap} -a --sam-hit-only "
            f"{self.ref_file} {self.temp_dir}/unaligned_seq_frags.fasta > {self.temp_dir}/realigned.sam",
            shell=True)
        print("Completed realignment")

    def recollect_fragments(self):
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
            if genome_count < 2 or frag_count < self.min_matched_frags:
                continue

            for pair in sorted(entry.pairs, key=lambda pair: pair[1]):
                output_str = f"{pair[0]}\t{pair[1]}\tAS:i:{str(pair[2])}\n"
                output += output_str
            output += "\n"

        with open(f"{self.parent_dir}/Output/{self.output_file}.txt", "w") as f:
            f.write(output)

        print(f"Results generated at: HGT/Output/{self.output_file}.txt")


class Fragmenter():
    def __init__(self, output_file="results"):
        self.sequence_dict = {}
        self.unaligned_seq_list = []
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"

        with open(self.parent_dir + "/settings.toml", 'rb') as f:
            toml = tomllib.load(f)

        self.sam_file = toml["file-paths"]["input-sam"]

        self.fragments_per_seq = toml['settings']['frags-per-seq']

    def find_unaligned_seqs(self):
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
                            # If sequence is aligned we don't need to store its sequence.
                            if self.sequence_dict[sequence_name][0]:
                                self.sequence_dict[sequence_name][1] = None

                        else:
                            self.sequence_dict[sequence_name] = [is_aligned, sequence, sequence_name]

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
        with open(f"{self.temp_dir}/unaligned_seq_frags.fasta", "w") as outfile:
            for sequence_name, sequence in tqdm.tqdm(self.unaligned_seq_list):
                frag_len = len(sequence) // self.fragments_per_seq

                for i in range(self.fragments_per_seq):
                    start_idx = i * frag_len
                    end_idx = start_idx + frag_len if i != self.fragments_per_seq - 1 else len(sequence)

                    outfile.write(f">{sequence_name}_frag_{i + 1}\n")
                    outfile.write(f"{sequence[start_idx:end_idx]}\n")

        del self.unaligned_seq_list
        print("Completed Fragment Sequence Processing")

    #  Will always be given a .sam file processed to only include aligned sequences (--sam-hit-only)


class SequenceData:
    def __init__(self, sequence):
        self.sequence = sequence
        self.genomes = set()
        self.fragments = set()
        self.pairs = []

    def __repr__(self):
        return f"({self.sequence}, {self.genomes}, {self.fragments}, {self.pairs})"


finder = Fragmenter()
finder.find_unaligned_seqs()
finder.fragment_seq()
del finder

fragAnalyzer = FragAnalyzer()
fragAnalyzer.realign_fragments()
fragAnalyzer.recollect_fragments()

