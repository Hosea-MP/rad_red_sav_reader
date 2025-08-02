from pathlib import Path
from rr_parser import RadicalRed
import sys
inp = Path(sys.argv[1])
outp = Path(sys.argv[2])
box = int(sys.argv[3])
slot = int(sys.argv[4])
species = int(sys.argv[5])
game = RadicalRed(inp.read_bytes())
pkm = game.game_save.pc.boxes[box].pokemon[slot]
pkm.set_species(species)
game.set_pc_pokemon(pkm, box, slot)
outp.write_bytes(game.savegame)
