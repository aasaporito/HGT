import os
import tqdm
import datetime


class RollingWindow:
    def __init__(self, input_file, step_size, output_file):
        id = "".join(str(datetime.datetime.now())[:-5].split(":"))

        self.parent_dir = os.path.dirname(os.getcwd())
        self.temp_dir = os.path.dirname(os.getcwd()) + "/tmp/"
        self.realigned_seqs = {}
        self.genomes = []
        self.output_buf = []
        self.sequences = {}
        if output_file:
            self.output_file = f"Window_Results_{output_file}"
        else:
            self.output_file = f"Window_results_{id}"

        self.output_file = output_file
        self.tmp_file = self.parent_dir + "/tmp/rolling_window.fasta"
        self.input_file = input_file
        self.step_size = step_size
        self.splits = RollingWindow.generate_splits(self.step_size)

    def write_splits(self):
        with open(f"{self.tmp_file}", "a") as f:
            for id, sequence in self.sequences.items():
                j = 0
                for percents in self.splits:
                    seq_splits = RollingWindow.split_string(sequence, percents)
                    if j < len(self.splits) // 2:
                        labels = [f"0-{percents[0]}", f"{100 - percents[1]}-100"]
                    else:
                        labels = [f"{100 - percents[1]}-100", f"0-{percents[0]}"]
                    j += 1
                    full_ids = [f"{id}_percents_{labels[0]}", f"{id}_percents_{labels[1]}"]

                    for i in range(len(full_ids)):
                        f.write(f">{full_ids[i]}\n{seq_splits[i]}\n")

    def generate_rolling_splits(self):
        with open(self.tmp_file, "w") as f:
            pass
        with tqdm.tqdm(total=os.path.getsize(f"{self.input_file}")) as pbar:
            with open(self.input_file, "r") as f:
                for line in f:
                    pbar.update(len(line))
                    if not line.startswith('@'):
                        fields = line.split("\t")
                        full_id = fields[0]
                        sequence = fields[9]
                        genome = fields[2]

                        id = full_id  #  full_id.split("/ccs")[0]
                        if genome == "*" and sequence != '*':  # TODO : Reexamine this, why was it set to only when known genome?
                            self.sequences[id] = sequence
                            self.genomes.append(genome + "\n")

                    if len(self.sequences) > 50_000:
                        print("Writing splits to file.")
                        self.write_splits()
                        self.sequences = {}

                if len(self.sequences) > 0:
                    self.write_splits()
                    self.sequences = {}

        print(f"Generated splits for realignment at: {self.tmp_file}")
        with open(f"{self.parent_dir}/tmp/genomes_to_filter.txt", "w") as f:
            f.write("".join(self.genomes))
        print(f"Generated filter file to reduce reference genome at /tmp/genomes_to_filter.txt")

    @staticmethod
    def generate_keys(split_step):
        i = split_step
        results = []
        while i <= 50:
            p1 = f"{0}-{i}"
            p2 = f"{i}-{100}"
            p3 = f"{0}-{100 - i}"
            p4 = f"{100 - i}-{100}"
            i += split_step
            results.append(p1)
            results.append(p2)
            results.append(p3)
            results.append(p4)

        return results[:-2]

    @staticmethod
    def generate_splits(split_step):
        results = []
        for i in range(split_step, 100, split_step):
            results.append([i, 100 - i])

        return results

    @staticmethod
    def parse_split_index(id):
        parts = id.split("/_percents_")
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

    def parse_results(self, sam_file):
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

                if star_count < 5 and len(known_genomes) >= 2:  # TODO : Star count is dependent on %'s
                    valid_tables[key] = subdict
                    continue

        # Sort key options and parse out the best pairing
        # valid_keys = ["0-5", "5-100", "0-15", "15-100", "0-25", "25-100", "0-35", "35-100", "0-50", "50-100"]
        valid_keys = RollingWindow.generate_keys(self.step_size)

        output_buffer = []
        for identifier in tqdm.tqdm(valid_tables.keys()):
            for i in range(0, len(valid_keys) - 1, 2):
                key1 = valid_keys[i]
                key2 = valid_keys[i + 1]
                try:
                    genomes = [valid_tables[identifier][key1], valid_tables[identifier][key2]]
                    if "*" not in genomes and genomes[0] != genomes[1]:
                        output_buffer.append(identifier)
                        output_buffer.append(key1 + "%\t" + genomes[0])
                        output_buffer.append(key2 + "%\t" + genomes[1] + "\n")
                        break
                except Exception as e:
                    # print(e)
                    # pprint.pprint(valid_tables[identifier])
                    pass

        with open(os.path.dirname(os.getcwd()) + f"/Output/{self.output_file}.txt",
                  "w") as f:
            f.write("\n".join(output_buffer))
        print(
            f"Output Generated at ./Output/{self.output_file}.txt")


