"""Exercise the world-map renderer on dense route samples at two canvas zooms."""
from math import dist
from pathlib import Path
import runpy
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / '.test-deps'))
from lupa.lua51 import LuaRuntime


def render(scale):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((root / 'tests/wow.lua').read_text(encoding='utf-8'))
    lua.execute("""
        fakeUI()
        local create = CreateFrame
        regions = {}
        canvasScale = ...
        local canvas = WorldMapFrame:GetCanvas()
        canvas:SetSize(1000, 600)
        canvas.GetEffectiveScale = function() return canvasScale end
        CreateFrame = function(kind, name, parent, ...)
            local region = create(kind, name, parent, ...)
            if parent then region.GetEffectiveScale = function() return parent:GetEffectiveScale() end end
            if kind == 'Line' or kind == 'Texture' then table.insert(regions, region) end
            return region
        end
        A = {map=WorldMapFrame, db={showJourneyRoute=true}, Journey={}, Navigation={}}
    """, scale)
    for source in ['RouteProgress.lua', 'RouteStyle.lua', 'JourneyView.lua']:
        lua.execute('assert(loadstring(...))("Mapperly", A)', (root / source).read_text(encoding='utf-8'))
    return lua.execute("""
        local points = {}
        local function add(x, y, discontinuity)
            points[#points + 1] = {x=x/1000, y=y/600, mapID=1, breakBefore=discontinuity}
        end
        -- Two perpendicular roads with subpixel variations and duplicate samples.
        -- A second road starts after a real gap. None of these inputs may change.
        for x = 20, 260 do
            add(x, 40 + (x%2) * .1)
            if x%20 == 0 then add(x, 40) end
        end
        for y = 41, 140 do add(260 + (y%2)*.1, y) end
        add(360, 140, true)
        add(400, 140)
        -- A return along the same road must not disappear as "redundant".
        add(20, 205, true)
        add(130, 205)
        add(43, 205)
        add(200, 205)
        local input = {}
        for i, p in ipairs(points) do input[i] = {p.x, p.y, p.breakBefore} end
        A.Journey.active = {kind='walking', points=points, legs={}}
        A.JourneyView.Refresh()
        local firstCount = #regions
        A.JourneyView.Refresh()
        assert(#regions == firstCount, 'refreshing unchanged world geometry must reuse stroke and join regions')
        local strokes = {}
        for _, line in ipairs(regions) do
            if line:IsShown() and line.routeCasing then
                local a, b = line.lineStart, line.lineEnd
                strokes[#strokes+1] = {a[3], -a[4], b[3], -b[4], line.thickness}
            end
        end
        assert(#input == #points, 'drawing the route changed its navigation point count')
        for i, p in ipairs(points) do
            assert(p.x == input[i][1] and p.y == input[i][2] and p.breakBefore == input[i][3],
                'drawing a simplified route must preserve the original navigation samples')
        end
        local covered = false
        for _, join in ipairs(A.JourneyView.fragments.joins or {}) do
            local anchor = join.face.point
            if join.face:IsShown() and join.edge:IsShown() and math.abs(anchor[4] - 260) < .5 and math.abs(anchor[5] + 40) < .5 then
                covered = true
                assert(join.edge:GetWidth() > join.face:GetWidth(), 'the rim should continue round the corner')
            end
        end
        assert(covered, 'the outer corner between perpendicular native strokes must be covered')
        A.db.showJourneyRoute = false
        A.JourneyView.Refresh()
        for _, region in ipairs(regions) do assert(not region:IsShown(), 'a stroke, joint or direction cue remained on the hidden route') end
        return strokes
    """)


def distance_to_stroke(point, stroke):
    x, y = point
    ax, ay, bx, by = stroke[:4]
    dx, dy = bx - ax, by - ay
    length_squared = dx*dx + dy*dy
    fraction = min(1, max(0, ((x-ax)*dx + (y-ay)*dy) / length_squared)) if length_squared else 0
    return dist(point, (ax + dx*fraction, ay + dy*fraction))


def check():
    expected = ([(x, 40) for x in range(20, 261)] +
                [(260, y) for y in range(41, 141)] +
                [(x, 140) for x in range(360, 401)])
    widths = []
    failures = []
    for scale in [1, 2.5]:
        strokes = [[line[i] for i in range(1, 6)] for line in render(scale).values()]
        assert strokes, 'walking route must render at both zooms'
        reverse = sum(max(0, line[0]-line[2]) for line in strokes if abs(line[1]-205) < 1)
        assert reverse > 75, 'collinear reversal lost'
        strokes = [line for line in strokes if max(line[1], line[3]) < 200]
        deviation = max(min(distance_to_stroke(p, line) for line in strokes) for p in expected) * scale
        print(f'Zoom {scale:g}: {len(strokes)} strokes, maximum centerline gap/deviation {deviation:.2f} px')
        if deviation > 1.5:
            failures.append(f'{scale:g}x: the line must continue through its direction cues and right-angle turn')
        if len(strokes) > 12:
            failures.append(f'{scale:g}x: hundreds of redundant road samples still render as separate tiny strokes')
        assert min(distance_to_stroke((310, 140), line) for line in strokes) > 35, 'a real break was connected'
        assert min(distance_to_stroke((230, 70), line) for line in strokes) > 20, 'corner cut by simplification'
        widths.append(max(line[4]*scale for line in strokes))
    if max(widths) > min(widths)*1.25:
        failures.append(f'world-map stroke width scales up with the map ({widths} screen pixels)')
    assert not failures, '\n'.join(failures)


if __name__ == '__main__':
    check()
    lua = runpy.run_path(str(root/'tests/run.py'))['lua']
    lua.execute("""
        local scale = 1
        local canvas = A.map:GetCanvas()
        canvas.GetEffectiveScale = function() return scale end
        local mapID = A.map:GetMapID()
        local plan = {kind='walking', points={{mapID=mapID,x=.1,y=.2},{mapID=mapID,x=.8,y=.7}}, legs={}}
        A.JourneyView.DisplayPlan = function() return plan end
        A.db.showJourneyRoute = true
        A.lastCanvasScale = nil
        local update = A.bar:GetScript('OnUpdate')
        update(A.bar, .16)
        local line = A.JourneyView.lines[1]
        assert(line and line:IsShown())
        local before = line.thickness
        scale = 2.5
        update(A.bar, .16)
        assert(math.abs(before - line.thickness*scale) < .001,
            'zooming a stationary preview must resize the stroke without reopening the map')
    """)
    print('PASS: smooth world route at both zooms, with continuous cues, preserved bends and genuine gaps')
