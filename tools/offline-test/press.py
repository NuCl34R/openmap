"""A left press that wandered isn't a click (#37, #64): python -P tools/offline-test/press.py."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


SOURCE = (Path(__file__).resolve().parents[2] / 'OpenMap/Map/WorldMap.lua').read_text(encoding='utf-8')


class PressTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute("""
            cx, cy = 100, 100
            sc = { mouseButtonInfo = { LeftButton = { down = false } } }
            function sc:GetCursorPosition() return cx, cy end
            function Down() sc.mouseButtonInfo.LeftButton.down = true PressDown(nil, 'LeftButton') end
            function MoveTo(x, y) cx, cy = x, y PressTrack() end
        """)
        helpers = SOURCE[SOURCE.index('local press = {'):SOURCE.index('local function OnCanvasClick(')]
        self.lua.execute(helpers + '\n_G.PressDown, _G.PressTrack, _G.WasDrag = PressDown, PressTrack, WasDrag\n')

    def check(self, code):
        self.lua.execute(code)

    def test_still_press_is_a_click(self):
        self.check("Down() MoveTo(101, 102) assert(not WasDrag())")

    def test_drag_out_and_back_is_not_a_click(self):
        self.check("Down() MoveTo(160, 100) MoveTo(101, 100) assert(WasDrag(), 'a drag back to the start counted as a click')")

    def test_next_press_starts_fresh(self):
        self.check("Down() MoveTo(160, 100) sc.mouseButtonInfo.LeftButton.down = false Down() assert(not WasDrag())")

    def test_right_button_leaves_left_press_alone(self):
        self.check("Down() MoveTo(160, 100) PressDown(nil, 'RightButton') assert(WasDrag())")

    def test_no_tracking_after_release(self):
        self.check("Down() sc.mouseButtonInfo.LeftButton.down = false MoveTo(300, 300) assert(not WasDrag())")


if __name__ == '__main__':
    unittest.main()
