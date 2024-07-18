import tqdm
import os


class SequenceData:
    def __init__(self, sequence):
        self.sequence = sequence
        self.genomes = set()
        self.fragments = set()
        self.pairs = []


class SplitPoint:
    def __init__(self):
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"
        self.realigned_seqs = {}
        self.output_file = "split2.sam"
        self.input_file = "split1_crop.sam"

    def filter_by_genome_count(self, min_genomes):
        with tqdm.tqdm(total=os.path.getsize(f"{self.temp_dir}/{self.input_file}")) as pbar:
            with open(f"{self.temp_dir}/{self.input_file}", "r") as infile:
                for line in infile:
                    pbar.update(len(line))

                    if line[0] != '@':
                        raw_line = line
                        line = line.split('\t')
                        seq_name = line[0]
                        genome = line[2]
                        alignment_score = int(line[13][5:])

                        if seq_name in self.realigned_seqs.keys():
                            old_score = self.realigned_seqs[seq_name][1]
                            if alignment_score > old_score:
                                self.realigned_seqs[seq_name] = [genome, alignment_score, raw_line]
                                continue
                            else:
                                continue
                        else:
                            self.realigned_seqs[seq_name] = [genome, alignment_score, raw_line]

        seq_dict = {}
        for frag_name, entry in self.realigned_seqs.items():
            seq_name = frag_name.split("/ccs_frag_")[0]
            genome = self.realigned_seqs[frag_name][0]
            alignment_score = self.realigned_seqs[frag_name][1]
            raw_line = self.realigned_seqs[frag_name][2]

            if seq_name not in seq_dict.keys():
                seq_dict[seq_name] = SequenceData(seq_name)

            seq_dict[seq_name].genomes.add(genome)
            seq_dict[seq_name].fragments.add(frag_name)
            seq_dict[seq_name].pairs.append([frag_name, genome, alignment_score, raw_line])

        # print(seq_dict)
        output = ""
        total_single_genome = 0
        multi_genomes = 0
        for entry in seq_dict.values():
            genome_count = len(entry.genomes)

            # Not enough aligned fragments or not enough species -> no results
            if genome_count < min_genomes:
                continue

            for pair in sorted(entry.pairs, key=lambda pair: pair[1]):
                output_str = f"{pair[3]}"
                output += output_str

        with open(f"{self.temp_dir}/{self.output_file}", "w") as f:
            f.write(output)
        # print(total_single_genome)
        # print(multi_genomes)

sp = SplitPoint()
sp.filter_by_genome_count(2)

