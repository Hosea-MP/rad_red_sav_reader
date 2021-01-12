from typing import Union, Optional

from rr_parser import RadicalRed, FireRed, Pokemon
from rr_parser.pkm_builder import pkm_builder

# FILENAME = "rr_2.1.sav"

GEN3_FILENAME = "savs/gen3_savs/fr.sav"
RR_FILENAME = "savs/rr_savs/rr_i.sav"
# FILENAME = "rrv2.sav"
# FILENAME ="GAMEV2.sav"

RR_OUTPUT_SAVE = "output/savs/GAMEV2.sav"
GEN3_OUTPUT_SAVE = "output/savs/USA_PokemonFireRed.sav"


def simple_update(game: Union[RadicalRed, FireRed], o: str):
    game.update_from_data()
    game.save(o)
    pass


def export_first_pkm(game: Union[RadicalRed, FireRed]):
    pkm = game.game_save.team.team_pokemon_list[0]
    pkm.encrypt()
    nick = pkm.nickname
    pkm_filename = "output/pkms/{}.bin".format(nick)
    with open(pkm_filename, 'wb') as f:
        f.write(pkm.data)
        pass
    pass


def change_species(
        game: Union[RadicalRed, FireRed],
        o: str,
        species: str,
        ability: Optional[int] = None
):
    if game.game_save.team.team_size < 6:
        # pk0: Pokemon = game.game_save.team.team_pokemon_list[0]
        # pk0.set_species(no)
        # _pkm_builder(game.gt, no)

        pk0 = pkm_builder(
            game.gt,
            species,
            ot_name=game.game_save.trainer_info.player_name,
            ot_id=game.game_save.trainer_info.trainer_id,
            ot_gender=game.game_save.trainer_info.player_gender,
            ability=ability
        )
        d0 = game.savegame
        game.set_pokemon(pk0, game.game_save.team.team_size)
        df = game.savegame
        assert (d0 != df)
        game.save(o)
    pass


def duplicate(game: Union[RadicalRed, FireRed], o: str):
    if game.game_save.team.team_size < 6:
        pk0: Pokemon = game.game_save.team.team_pokemon_list[0]
        d0 = game.savegame
        game.set_pokemon(pk0, game.game_save.team.team_size)
        df = game.savegame
        assert (d0 != df)
        game.save(o)
    pass


def test_gen3():
    with open(GEN3_FILENAME, "rb") as f:
        b = f.read()
        pass
    g = FireRed(b)
    print(g)
    simple_update(g, GEN3_OUTPUT_SAVE)
    export_first_pkm(g)
    change_species(g, GEN3_OUTPUT_SAVE, "zapdos")
    pass


def test_rr():
    with open(RR_FILENAME, "rb") as f:
        b = f.read()
        pass
    g = RadicalRed(b)
    print(g)
    for s_id, s in g.game_save.sections.items():
        print(s.checksum)
    simple_update(g, RR_OUTPUT_SAVE)
    duplicate(g, RR_OUTPUT_SAVE)
    export_first_pkm(g)
    change_species(g, RR_OUTPUT_SAVE, "zapdos", ability=3)
    change_species(g, RR_OUTPUT_SAVE, "mimikyu")
    pass


if __name__ == '__main__':
    test_gen3()
    test_rr()
    pass
