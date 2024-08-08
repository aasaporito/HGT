import os
import tqdm
import datetime
from SequenceData import SequenceData






class FragAnalyzer:
    def __init__(self, input_file, frag_size, min_frags, output_file, post_proc):
        identifier = "".join(str(datetime.datetime.now())[:-5].split(":"))
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"
        self.input_file = input_file
        self.post_proc = post_proc

        if output_file:
            self.output_file = f"Fragment_Results_{output_file}"
        else:
            self.output_file = f"Fragment_Results_{identifier}"
        self.min_matched_frags = min_frags
        self.frag_size = frag_size
        self.realigned_seqs = {}

    @staticmethod
    def get_fragment_number(record):
        return int(record[0].split('_')[-1])

    @staticmethod
    def check_consecutive_references(dataset):
        # Extract reference sequences
        references = [line.split("\t")[1] for line in dataset]

        # Check if the references are grouped together without interruptions
        unique_references = sorted(set(references))
        for ref in unique_references:
            indices = [i for i, x in enumerate(references) if x == ref]
            if indices != list(range(indices[0], indices[-1] + 1)):
                return False

        return True

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
                            # print("Error processing alignment score for: " + genome)
                            # print(line)
                            alignment_score = -1

                        if seq_name in self.realigned_seqs.keys():
                            old_score = self.realigned_seqs[seq_name][1]
                            if alignment_score > old_score:
                                self.realigned_seqs[seq_name] = [genome, alignment_score]
                                continue
                            else:
                                continue
                        else:
                            # alignment_score = -1
                            self.realigned_seqs[seq_name] = [genome, alignment_score]

        seq_dict = {}
        for frag_name, entry in self.realigned_seqs.items():
            seq_name = frag_name.split("_frag_")[0]
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

            for pair in sorted(entry.pairs, key=FragAnalyzer.get_fragment_number):
                output_str = f"{pair[0]}\t{pair[1]}\tAS:i:{str(pair[2])}\n"
                output += output_str
            output += "\n"

        with open(f"{self.parent_dir}/Output/{self.output_file}.txt", "w") as f:
            f.write(output)

        print(f"Results generated at: HGT/Output/{self.output_file}.txt")

        if self.post_proc:
            self.post_process()
            print(f"Completed post processing @ {self.parent_dir}/Output/Post_Proc_{self.output_file}.txt")

    def post_process(self):
        def read_file():
            with (open(f"{self.parent_dir}/Output/{self.output_file}.txt", "r") as f):
                valid_res = []
                while True:
                    entry = []
                    genomes = set()
                    for i in range(self.frag_size):
                        line = f.readline()
                        if not line:
                            return valid_res

                        line = line.split("\t")
                        entry.append(line)
                        genomes.add(line[1])
                    if True:
                        entry = sorted(entry, key=FragAnalyzer.get_fragment_number)
                        str_entry = ["\t".join(a) for a in entry]
                        if FragAnalyzer.check_consecutive_references(str_entry):
                            valid_res.append(entry)
                    f.readline()

        results = read_file()
        prepped_results = []
        for read in results:
            rows = []
            for row in read:
                row = "\t".join(row)
                rows.append(row)
            prepped_results.append("".join(rows))

        with open(f"{self.parent_dir}/Output/Post_Proc_{self.output_file}.txt", "w") as out:
            out.write("\n".join(prepped_results))


