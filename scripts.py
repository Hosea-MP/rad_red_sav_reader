import mmap
import json
import argparse

import pokebase as pb

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
    FP = './Complete-Fire-Red-Upgrade/asm_defines.s'
    OUT_FP = './rr_parser/constants/rr/_items.py'

    items = {}
    with open(FP, 'r') as f_in, \
        mmap.mmap(f_in.fileno(), 0, access=mmap.ACCESS_READ) as s:

        i = s.find(b'@;Items')
        if i == -1:
            raise LookupError('Couldn\'t find items list in asm_defines.s')
        print('Found items header, creating items list')
        s.seek(i)

        while True:
            line = s.readline().decode('utf-8')
            if line[:4] != '.equ':
                continue

            if line[5:9] != 'ITEM':
                break

            st, end = 10, line.find(',')
            name = line[st: end].replace('_', ' ').title()
            n = line[end+2:line.rfind('@')]
            number = int(n, 16) if n.startswith('0x') else int(n, 10)

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