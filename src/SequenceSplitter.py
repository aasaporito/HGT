import os
import tqdm
import pprint

# TODO : USER PARAMRS: step size, start size,
# TODO : Rerun whole process without 50 50 split
# TODO : Sequence in output
# Minimum genome hits to be considered in ref space

class SequenceSplitter:
    def __init__(self):
        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"
        self.realigned_seqs = {}
        self.output_file = self.parent_dir + "/testing/sp2.fasta"
        self.input_file = self.parent_dir + "/testing/" + "813_fresh.sam"
        self.genomes = []
        # self.splits = [[5, 95], [15, 85], [25, 75], [35, 65], [50, 50], [65, 35], [75, 25], [85, 15], [95, 5]]

        self.splits = SequenceSplitter.generate_splits(5) # TODO : Configure splits

        self.output_buf = []
        self.sequences = {}

        with tqdm.tqdm(total=os.path.getsize(f"{self.input_file}")) as pbar:
            with open(self.input_file, "r") as f:
                for line in f:
                    pbar.update(len(line))
                    if not line.startswith('@'):
                        fields = line.split("\t")
                        full_id = fields[0]
                        sequence = fields[9]
                        genome = fields[2]

                        id = full_id.split("/ccs")[0]
                        if genome != "*":
                            self.sequences[id] = sequence
                            self.genomes.append(genome + "\n")
                        # WARN : Only needed for resplicing 50s, should remove
            #             percents, id = SequenceSplitter.parse_split_index(full_id)
            #
            #             if id in self.sequences.keys():
            #                 if percents[0] == 0:
            #                     self.sequences[id][1] = sequence
            #                 else:
            #                     self.sequences[id][0] = sequence
            #             else:
            #                 self.sequences[id] = [None, None]
            #                 if percents[0] == 0:
            #                     self.sequences[id][1] = sequence
            #                 else:
            #                     self.sequences[id][0] = sequence
            #
            # # Remove pairings that are missing a second half # TODO : Why are some missing? 1 half didn't align?

        # pairings = []
        # count = 0
        # for id, pairing in self.sequences.items():
        #     if None not in pairing:
        #         pairings.append([id, "".join(pairing)])

        # TODO : Bug here prevents high % targets
        with open(f"{self.output_file}", "w") as f:
            for id, sequence in self.sequences.items():
                j = 0
                for percents in self.splits:
                    seq_splits = SequenceSplitter.split_string(sequence, percents)
                    if j < len(self.splits)//2:
                        labels = [f"0-{percents[0]}", f"{100 - percents[1]}-100"]
                    else:
                        labels = [f"{100 - percents[1]}-100", f"0-{percents[0]}"]
                    j += 1
                    full_ids = [f"{id}_percents_{labels[0]}", f"{id}_percents_{labels[1]}"]

                    for i in range(len(full_ids)):
                        f.write(f">{full_ids[i]}\n{seq_splits[i]}\n")

        with open(f"{self.parent_dir}/testing/genomes_to_filt.txt", "w") as f:
            f.write("".join(self.genomes))

            # for pair in self.output_buf:
            #     full_id = pair[0]
            #     sequence = pair[1]
            #     f.write(f">{full_id}\n{sequence}\n")

    @staticmethod
    def generate_splits(split_step):
        results = []
        for i in range(split_step, 100, split_step):
            results.append([i, 100 - i])

        return results
    @staticmethod
    def parse_split_index(id):
        parts = id.split("/ccs_frag_")
        percents = [int(float(i)) for i in parts[1].split("-")]
        return percents, parts[0]

    @staticmethod
    def split_string(seq, percentages):
        if sum(percentages) != 100:
            raise ValueError("Percentages must add up to 100.")

        # Calculate the lengths of each chunk
        lengths = [int(len(seq) * (p / 100)) for p in percentages]

        # Adjust the last chunk to ensure the total length matches the string length
        lengths[-1] += len(seq) - sum(lengths)

        # Split the string into chunks
        chunks = []
        start = 0
        for length in lengths:
            chunks.append(seq[start:start + length])
            start += length

        return chunks

    @staticmethod
    def parse_results(sam_file):
        identifiers = {}
        genomes = {}
        split_tables = {}  # dict[identifier] = subdict[percentage as key] = genome
        with tqdm.tqdm(total=os.path.getsize(f"{sam_file}")) as pbar:
            with open(sam_file, "r") as f:
                for line in f:
                    pbar.update(len(line))
                    if not line.startswith("@"):
                        fields = line.split("\t")

                        identifier = fields[0].split("_percents_")[0]
                        split_percent = fields[0].split("_percents_")[1]
                        genome = fields[2]

                        if identifier not in split_tables.keys():
                            split_tables[identifier] = {}

                        split_tables[identifier][split_percent] = genome

                        identifiers[identifier] = "*"
                        genomes[genome] = "*"

        valid_tables = {}
        for key, subdict in tqdm.tqdm(split_tables.items()):
            known_genomes = set()
            star_count = 0

            for subkey, value in subdict.items():
                known_genomes.add(value)
                if "*" == value:
                    star_count += 1
                try:
                    known_genomes.remove("*")
                except:
                    pass

                if star_count < 5 and len(known_genomes) >= 2:
                    valid_tables[key] = subdict
                    continue

        # Sort key options and parse out the best pairing
        # valid_keys = ["0-5", "5-100", "0-15", "15-100", "0-25", "25-100", "0-35", "35-100", "0-50", "50-100"]
        valid_keys = [
            "0-5", "5-100", "0-95", "95-100", "0-90", "90-100", "0-10", "10-100", "0-15",
            "15-100", "0-85", "85-100", "0-20", "20-100", "0-80", "80-100", "0-25", "25-100",
            "0-75", "75-100", "0-30", "30-100", "0-70", "70-100", "0-35", "35-100", "0-65",
            "65-100", "0-40", "40-100", "0-60", "60-100", "0-45", "45-100", "0-55", "55-100",
            "0-50", "50-100"
        ]

        # Do both (4) at once
        # What about inconsistency? -> TODO :

        output_buffer = []
        for identifier in tqdm.tqdm(valid_tables.keys()):
            for i in range(0, len(valid_keys)-1, 2):
                key1 = valid_keys[i]
                key2 = valid_keys[i+1]
                try:
                    genomes = [valid_tables[identifier][key1], valid_tables[identifier][key2]]
                    if "*" not in genomes and genomes[0] != genomes[1]:
                        output_buffer.append(identifier)
                        output_buffer.append(key1 + "%\t" + genomes[0])
                        output_buffer.append(key2 + "%\t" + genomes[1] + "\n")
                        break
                except Exception as e:
                    print(e)
                    pprint.pprint(valid_tables[identifier])
                    pass

        with open(os.path.dirname(os.getcwd()) + "/testing/split_point_results.txt", "w") as f:
            f.write("\n".join(output_buffer))


#SequenceSplitter()
SequenceSplitter.parse_results(os.path.dirname(os.getcwd()) + "/testing/813_fresh.sam") # Use sams with unaligned
