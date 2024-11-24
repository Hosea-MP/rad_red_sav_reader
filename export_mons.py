import argparse
from rr_parser.functions import export_pkm_sets_for_calc
from rr_parser import load_radical_red_game

def parse_args():
    parser = argparse.ArgumentParser(description='Export of radical red save data for use in showdown calcs')
    parser.add_argument('sav_filename', type=str)
    parser.add_argument('output_directory', type=str)
    parser.add_argument('--skip_boxes', nargs='*', type=int)
    parser.add_argument('--box_min', type=int, default=0)
    parser.add_argument('--box_max', type=int, default=25) # TODO Update with max boxes

    args = parser.parse_args()

    box_range = None
    if args.box_min <= args.box_max:
        box_range = (args.box_min, args.box_max)

    print(f'Loading sav file from `{args.sav_filename}`')
    g = load_radical_red_game(args.sav_filename)
    return [
        g,
        args.output_directory,
        box_range,
        args.skip_boxes
    ]

def main(g, output_dir, box_range, skip_boxes):
    export_pkm_sets_for_calc(g, output_dir, box_range, skip_boxes)


if __name__ == '__main__':
    args = parse_args()
    main(*args)