TIBERIUM COMMAND — BUILDING GRAPHICS OVERHAUL

PLAY
Open tiberium_command_building_graphics_overhaul.html directly in a modern desktop browser. The game is standalone and does not need a server or external libraries.

WHAT CHANGED
- Eight original raster building sprites: Power Plant, Barracks, War Factory, Ore Refinery, Radar Dome, Gun Turret, SAM Site and Concrete Wall.
- Separate friendly gray/yellow and enemy gray/red-accent building sprite atlases.
- Building sprites are embedded in the HTML as PNG data URLs.
- The building collision, placement, pathfinding, production and damage footprints remain the original tile dimensions.
- Hovering the visible sprite or footprint shows the structure name, role and health.
- Gun Turret barrel rotates toward its current target independently of the building base.
- Radar sweep, power status lights and refinery ore conveyor have lightweight time-based animations.

ASSETS
rts_building_sprite_sheet.png       Friendly building atlas, 4 columns × 2 rows, 256 × 208 per cell.
rts_building_sprite_sheet_enemy.png Enemy-accent atlas, same layout.
rts_building_sprite_sheet_preview.jpg Preview of the friendly atlas.
building_*.png                      Individual source sprites.
build_building_sprites.py           Python/Pillow source used to construct the PNG atlas.

BUILDING ATLAS CELL ORDER
Row 1: power, barracks, warfactory, refinery
Row 2: radar, turret, sam, wall

The building sprites are original artwork inspired by classic isometric RTS visual language; they are not extracted from Command & Conquer.
