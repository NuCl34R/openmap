"""Boss pins' data (Data/Forever/DungeonBosses.lua) against the maps and boss lists it's for:
python -P tools/offline-test/bosses.py

Each boss's place must be on one of its instance's floors (Data/DungeonMaps.lua's, else
Data/DungeonDrawn.lua's, as Map/Dungeons.lua's FloorsOf picks them), inside the picture (0..1),
and a boss the game lists for it (Places.lua) or one placed by hand (tools/map-dungeons/bosses.json).
(The pins themselves, on the dungeon's map, and the placer need the game: the stub has no world map.)
"""
from pathlib import Path
import json
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "OpenMap" / "Data" / "Forever"


def load():
    lua = LuaRuntime(unpack_returned_tuples=True)
    ns = lua.eval("{ Media = { tex = '' } }")
    for name in ("Places.lua", "DungeonMaps.lua", "DungeonDrawn.lua", "DungeonMinimap.lua", "DungeonBosses.lua"):
        fn = lua.eval("function(src, ns) return assert(loadstring(src))('OpenMap', ns) end")
        fn((DATA / name).read_text(encoding="utf-8"), ns)
    return ns


class Bosses(unittest.TestCase):
    def test_places(self):
        ns = load()
        places = ns.MapPlaces
        placed = json.loads((ROOT / "tools" / "map-dungeons" / "bosses.json").read_text(encoding="utf-8")) \
            if (ROOT / "tools" / "map-dungeons" / "bosses.json").exists() else {}
        n = 0
        for key, bosses in ns.MapDungeonBosses.items():
            base = int(key[8:]) if isinstance(key, str) and key.startswith("minimap:") else key
            floors = ns.MapDungeonMinimap[base] if base != key else (ns.MapDungeonMaps[key] or ns.MapDungeonDrawn[key])
            self.assertTrue(floors, "%s: bosses for a dungeon with no map" % key)
            listed = set((places.bosses[base] or {}).values()) if isinstance(base, int) else set()
            listed |= set(placed.get(str(key), {}))
            for name, p in bosses.items():
                n += 1
                self.assertIn(name, listed, "%s: %s isn't one of its bosses" % (key, name))
                self.assertTrue(1 <= p[1] <= len(floors), "%s: %s on floor %s of %d" % (key, name, p[1], len(floors)))
                self.assertTrue(0 <= p[2] <= 1 and 0 <= p[3] <= 1, "%s: %s off its picture" % (key, name))
        self.assertGreater(n, 100, "fewer bosses placed than the journals alone give")


if __name__ == "__main__":
    unittest.main()
