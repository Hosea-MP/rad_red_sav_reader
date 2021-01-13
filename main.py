import rr_parser
from rr_parser import FireRed

GEN3_FILENAME = "savs/gen3_savs/fr.sav"
RR_FILENAME = "savs/rr_savs/rr_i.sav"

RR_OUTPUT_SAVE = "output/savs/GAMEV2.sav"
GEN3_OUTPUT_SAVE = "output/savs/USA_PokemonFireRed.sav"


def test_gen3():
    with open(GEN3_FILENAME, "rb") as f:
        b = f.read()
        pass
    g = FireRed(b)
    print(g)
    rr_parser.export_first_team_pkm(g, "output/pkms/CHARIZARD.bin")
    rr_parser.create_and_insert_pokemon(
        game=g,
        species="zapdos",
        shiny=True
    )
    rr_parser.save_game(g, GEN3_OUTPUT_SAVE)
    pass


def test_rr():
    g = rr_parser.load_radical_red_game(RR_FILENAME)
    print(g)

    rr_parser.clone_first_team_pkm(g)
    rr_parser.export_first_team_pkm(g, "output/pkms/Articuno.bin")
    rr_parser.create_and_insert_pokemon(
        game=g,
        species="zapdos",
        shiny=True,
        ability=3
    )
    rr_parser.create_and_insert_pokemon(
        game=g,
        species="mimikyu",
        shiny=True,
        ability=3,
        nature="Adamant"
    )
    rr_parser.save_game(g, RR_OUTPUT_SAVE)
    pass


if __name__ == '__main__':
    test_gen3()
    test_rr()
    pass
