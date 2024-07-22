import os
import tqdm
import datetime
from SequenceData import SequenceData


class FragAnalyzer:
    def __init__(self, input_file, min_frags):
        identifier = str(datetime.datetime.now())[:-5]
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"
        self.input_file = input_file
        self.output_file = f"Fragment_Results_{identifier}"
        self.min_matched_frags = min_frags
        self.realigned_seqs = {}

        # self.ref_file = toml["minimap2"]["reference-file"]
        # self.args_minimap = toml["minimap2"]["options"]

    # def realign_fragments(self):
    #     print("Running minimap2 to realign reads")
    #     subprocess.run(
    #         f"{self.parent_dir}/Tools/minimap2-2.28_x64-linux/minimap2 {self.args_minimap} -a --sam-hit-only "
    #         f"{self.ref_file} {self.temp_dir}/unaligned_seq_frags.fasta > {self.temp_dir}/realigned.sam",
    #         shell=True)
    #     print("Completed realignment")

    def recollect_fragments(self):
        print("Analyzing realigned fragments")
        with tqdm.tqdm(total=os.path.getsize(f"{self.input_file}")) as pbar:
            with open(f"{self.input_file}", "r") as infile:
                for line in infile:
                    pbar.update(len(line))

                    if line[0] != '@':
                        line = line.split('\t')
                        seq_name = line[0]
                        genome = line[2]
                        if genome == '*':
                            continue
                        try:
                            alignment_score = int(line[13][5:])
                        except Exception as e:
                            print("Error processing alignment score for: " + genome)

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
