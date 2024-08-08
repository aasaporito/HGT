import argparse
from FragAnalyzer import FragAnalyzer
from Fragmenter import Fragmenter
from RollingWindow import RollingWindow


def setup_parser():
    parser = argparse.ArgumentParser(description='Horizontal Gene Transfer Launcher')

    mut_group = parser.add_mutually_exclusive_group(required=True)
    mut_group.add_argument("-f", "--frag", help="Fragmenting mode", action="store_true")
    mut_group.add_argument("-r", "--rolling", help="Rolling Window mode", action="store_true")

    parser.add_argument("--results", help="Result processing mode", action='store_true')
    parser.add_argument("-o", "--output", help="Output file name", action='store')
    parser.add_argument("-i", "--input",
                        help="Input file. Either initial sam file or results to process (with --results)",
                        required=True)

    group = parser.add_argument_group('Fragmenting Options')
    group.add_argument("-s", "--size", help="Fragments per sequence [default: 10]", type=int,
                       default=10, action="store")
    group.add_argument("-m", "--min-frags", help="Minimum matched fragments for candidacy [default: Equal to -s]",
                       type=int, default=None, action="store")
    group.add_argument("-pp", help="Post processing for fragment mode. Filters out non-sequential genomes in results.", default=None, action="store_true")

    group = parser.add_argument_group('Rolling Window Options')
    group.add_argument("-w", "--window", help="Window step size [default: 10 percent]", type=int, default=10,
                       action="store")

    args = parser.parse_args()
    return args


def fragment_launcher(args):
    frag_size = args.size
    min_frags = args.min_frags
    result_mode = args.results is True
    input_file = args.input
    output_file = args.output
    post_proc = args.pp

    if result_mode:
        print("Launching result processor")
        frag_analyzer = FragAnalyzer(input_file, frag_size, min_frags, output_file, post_proc)
        frag_analyzer.recollect_fragments()
    else:
        print("Launching fragment slicer")
        frag = Fragmenter(input_file, frag_size, min_frags)
        frag.find_unaligned_seqs()
        frag.fragment_seq()
    pass


def rolling_window_launcher(args):
    window_step = args.window
    result_mode = args.results is True
    input_file = args.input
    output_file = args.output

    if result_mode:
        print("Launching result processor")
        rolling_window = RollingWindow(input_file, window_step, output_file)
        rolling_window.parse_results(input_file)
    else:
        print("Launch window slicer")
        window = RollingWindow(input_file, window_step, output_file)
        window.generate_rolling_splits()


args = setup_parser()

# Range Checking
if args.size <= 1:
    print("Error: -s/--size: Value must be greater than 1.")
    exit()
if args.window <= 1:
    print("Error: -s/--window: Value must be greater than 1.")
    exit()

if args.frag:
    if args.min_frags is None:
        args.min_frags = args.size

    if args.min_frags > args.size:
        print("Error: -m/--min_frags: Value must be greater than or equal to -s/--size.")
        exit()

    fragment_launcher(args)
elif args.rolling:
    rolling_window_launcher(args)
