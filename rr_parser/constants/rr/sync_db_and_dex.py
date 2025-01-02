import json

def main():
    with open('./_pokemon.json') as f:
        pkm_db = json.load(f)

    with open('./_pokedex.py', 'w') as f:
        for idx, info in pkm_db.items():
            name = info['name'].upper().replace('-', '__').replace(' ', '_')
            f.write(f'NATIONAL_DEX_{name}: int = {idx}\n')

if __name__ == "__main__":
    main()