import mmap
import json
import argparse

#import pokebase as pb

# NOTE: This constructs a db based on base game abilities
def create_pokemon_db():
    OUT_FP = 'rr_parser/constants/rr/_pokemon.json'

    db = {}
    for name in pb.APIResourceList('pokemon').names:
        print(f'Creating entry for {name}')
        pkm = pb.pokemon(name)
        abilities = [ab.ability.name for ab in pkm.abilities]

        pokemon = {
            'id': pkm.id,
            'name': pkm.name,
            'abilities': abilities
        }
        db[pkm.id] = pokemon

    with open(OUT_FP, 'w') as f:
        json.dump(db, f)


def create_items_list():
    FP = './rr_parser/constants/rr/_items.txt'
    OUT_FP = './rr_parser/constants/rr/_items.py'

    items = {}
    unknown = int('FFFF', 16)
    with open(FP, 'r') as f_in:

        for line in f_in:
            hex_code = line.rfind('\t')
            name = line[:hex_code].strip()
            hex_code = line[hex_code+1:].strip()
            

            if name == '':
                continue

            if hex_code == '':
                number = unknown
                unknown -= 1
            else:
                number = int(hex_code, 16)

            items[number] = name

            
    with open(OUT_FP, 'w') as f_out:
        f_out.write('items_dict = ')
        json.dump(items, f_out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('script', type=str)

    args = parser.parse_args()

    if args.script.lower() in ['items', 'items_list', 'create_items_list']:
        create_items_list()

    if args.script.lower() in ['pokemon']:
        create_pokemon_db()