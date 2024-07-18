import argparse


def setup_parser():
    parser = argparse.ArgumentParser(description='Horizontal Gene Transfer Launcher')
    parser.add_argument("--results", help="Result processing mode", action='store_true')

    mut_group = parser.add_mutually_exclusive_group(required=True)
    mut_group.add_argument("-f", "--frag", help="Fragmenting mode", action="store_true")
    mut_group.add_argument("-r", "--rolling", help="Rolling Window mode", action="store_true")

    group = parser.add_argument_group('Fragmenting Options')
    group.add_argument("-s", "--size", help="Size of chunks for fragmenting mode [default: 10 percent]", type=int,
                       default=10, action="store")
    group.add_argument("-m", "--min-frags", help="Minimum matched fragments for candidacy [default: Equal to -s]", type=int, default=None, action="store")

    group = parser.add_argument_group('Rolling Window Options')
    group.add_argument("-w", "--window", help="Window step size [default: 10 percent]", type=int, default=10,
                       action="store")

    args = parser.parse_args()
    return args


def fragment_launcher(args):
    print("Frag Launch")
    frag_size = args.size
    min_frags = args.min_frags
    result_mode = args.results is True

    if result_mode:
        print("Launch result processor")
    else:
        print("Launch fragment creator for alignment")
    pass


def rolling_window_launcher(args):
    print("Roll Launch")
    window_step = args.window
    result_mode = args.results is True

    if result_mode:
        print("Launch result processor")
    else:
        print("Launch window slice creator for alignment")
    pass

    pass


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
