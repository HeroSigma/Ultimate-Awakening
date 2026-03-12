#!/usr/bin/env python3
"""
Sub-Phase 3.2: Migrate HnS Kanto maps into Ultimate-Awakening _Frlg folders.

Strategy:
  - HnS is the authoritative source for all Kanto maps.
  - Every HnS Kanto map <Name>  →  data/maps/<Name>_Frlg/ in our project.
  - Every HnS group gMapGroup_X →  gMapGroup_X_Frlg in our map_groups.json.
  - No manual renaming — HnS names used directly (just append _Frlg).
  - dest_map/connection MAP_ constants: append _FRLG if a Kanto map, else keep.
  - music: MUS_HG_* → nearest MUS_RG_* equivalent via table.

For each HnS Kanto map:
  1. Copy layout binaries (map.bin, border.bin) → data/layouts/<Name>_Frlg/
  2. Add/update layouts.json entry for the _Frlg layout
  3. Write data/maps/<Name>_Frlg/map.json  (HnS content, transformed)
  4. Create data/maps/<Name>_Frlg/scripts.inc stub  (if absent)
  5. Update map_groups.json (replace old Kanto groups with HnS-derived groups)

Usage:
  python3 dev_scripts/migrate_hns_kanto_maps.py [--dry-run] [--only=MapName]
"""

import json, os, re, shutil, sys, argparse, hashlib
from collections import OrderedDict

PROJECT_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HNS_ROOT        = "/home/allan/HnS-reference"
MAPS_DIR        = os.path.join(PROJECT_ROOT, "data/maps")
LAYOUTS_DIR     = os.path.join(PROJECT_ROOT, "data/layouts")
LAYOUTS_JSON    = os.path.join(PROJECT_ROOT, "data/layouts/layouts.json")
MAP_GROUPS_JSON = os.path.join(PROJECT_ROOT, "data/maps/map_groups.json")
HNS_MAPS_DIR    = os.path.join(HNS_ROOT, "data/maps")
HNS_LAYOUTS_DIR = os.path.join(HNS_ROOT, "data/layouts")
HNS_LAYOUTS_JSON = os.path.join(HNS_ROOT, "data/layouts/layouts.json")

# ===========================================================================
# CANONICAL KANTO MAP GROUPS  (HnS-authoritative)
# Keys   = our group names (_Frlg already embedded)
# Values = list of HnS map folder names (NO _Frlg yet)
# ===========================================================================
HNS_KANTO_GROUPS = OrderedDict([
    ("gMapGroup_TownsAndRoutes_Frlg", [
        "PalletTown","ViridianCity","PewterCity","CeruleanCity","VermilionCity",
        "LavenderTown","CeladonCity","SaffronCity","FuchsiaCity","CinnabarIsland",
        "Route1","Route2","Route3","Route4","Route5","Route6","Route7","Route8",
        "Route9","Route10","Route11","Route12","Route13","Route14","Route15",
        "Route16","Route17","Route18","Route19","Route20","Route21","Route22",
        "Route23","IndigoPlateau","Route24","Route25","Route26","Route26North",
        "Route27","Route28",
    ]),
    ("gMapGroup_IndoorPallet_Frlg", [
        "PalletTown_RedsHouse_1F","PalletTown_RedsHouse_2F",
        "PalletTown_House2","PalletTown_House3","PalletTown_Lab",
    ]),
    ("gMapGroup_IndoorViridian_Frlg", [
        "ViridianCity_PokemonCenter","ViridianCity_Mart",
        "ViridianCity_House1","ViridianCity_House2","ViridianCity_Gym",
    ]),
    ("gMapGroup_IndoorPewter_Frlg", [
        "PewterCity_PokemonCenter","PewterCity_Mart",
        "PewterCity_House1","PewterCity_House2","PewterCity_Gym",
        "PewterCity_Museum_1F","PewterCity_Museum_2F",
    ]),
    ("gMapGroup_IndoorCerulean_Frlg", [
        "CeruleanCity_PokemonCenter","CeruleanCity_Mart",
        "CeruleanCity_House2","CeruleanCity_House3",
        "CeruleanCity_BikeShop","CeruleanCity_Gym",
    ]),
    ("gMapGroup_IndoorVermilion_Frlg", [
        "VermilionCity_PokemonCenter","VermilionCity_Mart",
        "VermilionCity_PortOutside","VermilionCity_PortInside","VermilionCity_Gym",
        "VermilionCity_FanClub",
        "VermilionCity_House1","VermilionCity_House2","VermilionCity_House3",
    ]),
    ("gMapGroup_IndoorLavender_Frlg", [
        "LavenderTown_PokemonCenter","LavenderTown_Mart",
        "LavenderTown_House1","LavenderTown_House2","LavenderTown_House3",
        "LavenderTown_RadioStation","LavenderTown_SoulHouse",
    ]),
    ("gMapGroup_IndoorCeladon_Frlg", [
        "CeladonCity_PokemonCenter","CeladonCity_House1","CeladonCity_House2",
        "CeladonCity_Apartments_1F","CeladonCity_Apartments_2F","CeladonCity_Apartments_3F",
        "CeladonCity_Apartments_RoofDay","CeladonCity_Apartments_RoofNight","CeladonCity_Apartments_RoofHouse",
        "CeladonCity_GameCorner",
        "CeladonCity_DepartmentStore_1F","CeladonCity_DepartmentStore_2F","CeladonCity_DepartmentStore_3F",
        "CeladonCity_DepartmentStore_4F","CeladonCity_DepartmentStore_5F",
        "CeladonCity_DepartmentStore_RoofDay","CeladonCity_DepartmentStore_RoofNight",
        "CeladonCity_Gym",
    ]),
    ("gMapGroup_IndoorSaffron_Frlg", [
        "SaffronCity_PokemonCenter","SaffronCity_Mart","SaffronCity_TrainStation",
        "SaffronCity_FightingDojo","SaffronCity_FightingDojoVIP","SaffronCity_Gym",
        "SaffronCity_SilphCo",
        "SaffronCity_CopyCatsHouse_1F","SaffronCity_CopyCatsHouse_2F","SaffronCity_House1",
    ]),
    ("gMapGroup_IndoorFuchsia_Frlg", [
        "FuchsiaCity_PokemonCenter","FuchsiaCity_Mart",
        "FuchsiaCity_House1","FuchsiaCity_House2","FuchsiaCity_Gym",
        "FuchsiaCity_Route19_Gate","FuchsiaCity_Route15_Gate",
        "FuchsiaCity_SafariZoneEntrance",
        "FuchsiaCity_SafariZoneBeach","FuchsiaCity_SafariZoneBrush",
        "FuchsiaCity_SafariZoneMountain","FuchsiaCity_SafariZoneCave",
    ]),
    ("gMapGroup_IndoorCinnabar_Frlg", [
        "CinnabarIsland_PokemonCenter",
    ]),
    ("gMapGroup_IndoorIndigo_Frlg", [
        "IndigoPlateau_PokemonCenter",
        "PokemonLeague_WillsRoom","PokemonLeague_KogasRoom",
        "PokemonLeague_BrunosRoom","PokemonLeague_KarensRoom",
        "PokemonLeague_ChampionsRoom","PokemonLeague_HallOfFame",
    ]),
    ("gMapGroup_IndoorKantoRoutes_Frlg", [
        "Route26_House1","Route26_House2",
        "Gate_Route2_ViridianForest","Gate_ViridianForest_Route2",
        "Gate_Route2","Route2_House","MtMoon_Shop","CeruleanCity_House1",
        "Route5_House","Route5_TunnelEntrance",
        "Gate_SaffronCity_Route5","SaffronCity_Tunnel_NS",
        "Route6_TunnelEntrance","Gate_SaffronCity_Route6",
        "Gate_SaffronCity_Route7","Route7_TunnelEntrance",
        "SaffronCity_Tunnel_SW","Route8_TunnelEntrance","Gate_SaffronCity_Route8",
        "Route9_PokemonCenter",
        "Route10_PowerPlantEntrance","Route10_PowerPlantBackRoom",
        "Route16_House","Gate_CeladonCity_Route16",
        "Gate_FuchsiaCity_Route18","Route12_House",
        "Route4_PokemonCenter","Route25_BillsHouse",
    ]),
    # Kanto dungeon maps → merged into gMapGroup_Dungeons_Frlg
    ("_kanto_dungeons_", [
        "VictoryRoadKanto_B2F","VictoryRoadKanto_B1F","VictoryRoadKanto_1F",
        "ViridianForest","MtMoon_Cave","MtMoon_Outside",
        "RockTunnel_B1F","RockTunnel_1F",
        "CeruleanCave_1F","CeruleanCave_B1F","CeruleanCave_B2F",
        "DiglettsCave_EntranceNorth","DiglettsCave_EntranceSouth","DiglettsCave_Tunnel",
        "SeafoamIslands_1F","SeafoamIslands_Gym","SeafoamIslands_B1F",
        "SeafoamIslands_SecretCave","Route19_Cave",
    ]),
])

# Flat set of ALL HnS Kanto map names (used to determine MAP_ const translation)
ALL_KANTO_HNS = set()
for _g, _m in HNS_KANTO_GROUPS.items():
    ALL_KANTO_HNS.update(_m)


def _camel_to_const(name):
    s = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', name)
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
    return 'MAP_' + s.upper()


# Set of MAP_ constants for Kanto maps (without _FRLG — that's what HnS emits)
KANTO_MAP_CONSTS = {_camel_to_const(n) for n in ALL_KANTO_HNS}

# ===========================================================================
# Music translation:  MUS_HG_*  →  MUS_RG_*
# ===========================================================================
MUSIC_TRANSLATE = {
    "MUS_HG_PALLET":          "MUS_RG_PALLET",
    "MUS_HG_PEWTER":          "MUS_RG_PEWTER",
    "MUS_HG_CERULEAN":        "MUS_RG_FUCHSIA",
    "MUS_HG_VERMILION":       "MUS_RG_VERMILLION",
    "MUS_HG_LAVENDER":        "MUS_RG_LAVENDER",
    "MUS_HG_CELADON":         "MUS_RG_CELADON",
    "MUS_HG_CINNABAR":        "MUS_RG_CINNABAR",
    "MUS_HG_GYM":             "MUS_RG_GYM",
    "MUS_HG_POKE_CENTER":     "MUS_RG_POKE_CENTER",
    "MUS_HG_POKE_MART":       "MUS_RG_POKE_CENTER",
    "MUS_HG_ROUTE1":          "MUS_RG_ROUTE1",
    "MUS_HG_ROUTE3":          "MUS_RG_ROUTE3",
    "MUS_HG_ROUTE11":         "MUS_RG_ROUTE11",
    "MUS_HG_ROUTE24":         "MUS_RG_ROUTE24",
    "MUS_HG_ROUTE26":         "MUS_RG_ROUTE24",
    "MUS_HG_VIRIDIAN_FOREST": "MUS_RG_VIRIDIAN_FOREST",
    "MUS_HG_ROCK_TUNNEL":     "MUS_RG_MT_MOON",
    "MUS_HG_VICTORY_ROAD":    "MUS_RG_VICTORY_ROAD",
    "MUS_HG_POKEMON_LEAGUE":  "MUS_RG_HALL_OF_FAME",
    "MUS_HG_ICE_PATH":        "MUS_RG_SEVII_CAVE",
    "MUS_HG_OAK":             "MUS_RG_OAK",
    "MUS_HG_UNION_CAVE":      "MUS_RG_MT_MOON",
    "MUS_HG_GAME_CORNER":     "MUS_RG_GAME_CORNER",
    "MUS_HG_DANCE_THEATER":   "MUS_RG_CELADON",
    "MUS_HG_GOLDENROD":       "MUS_RG_CELADON",
    "MUS_HG_MT_MOON_SQUARE":  "MUS_RG_MT_MOON",
    "MUS_HG_SAFARI_ZONE":     "MUS_SAFARI_ZONE",
    "MUS_HG_FUCHSIA":         "MUS_RG_FUCHSIA",
}

# Primary tilesets that exist as-is in our project (no _Frlg suffix needed)
_PRIMARY_PASSTHROUGH = {
    "gTileset_Johto_General", "gTileset_General",
    "gTileset_Building", "gTileset_BuildingFrlg",
    "gTileset_Johto_Building", "gTileset_Kanto_General",
}

# OLD Kanto entries to REMOVE from gMapGroup_Dungeons_Frlg when rebuilding
_OLD_KANTO_DUNGEONS = {
    "ViridianForest_Frlg",
    "MtMoon_1F_Frlg","MtMoon_B1F_Frlg","MtMoon_B2F_Frlg",
    "UndergroundPath_NorthEntrance_Frlg","UndergroundPath_NorthSouthTunnel_Frlg",
    "UndergroundPath_SouthEntrance_Frlg","UndergroundPath_WestEntrance_Frlg",
    "UndergroundPath_EastWestTunnel_Frlg","UndergroundPath_EastEntrance_Frlg",
    "DiglettsCave_NorthEntrance_Frlg","DiglettsCave_B1F_Frlg","DiglettsCave_SouthEntrance_Frlg",
    "VictoryRoad_1F_Frlg","VictoryRoad_2F_Frlg","VictoryRoad_3F_Frlg",
    "RocketHideout_B1F_Frlg","RocketHideout_B2F_Frlg","RocketHideout_B3F_Frlg",
    "RocketHideout_B4F_Frlg","RocketHideout_Elevator_Frlg",
    "SilphCo_1F_Frlg","SilphCo_2F_Frlg","SilphCo_3F_Frlg","SilphCo_4F_Frlg",
    "SilphCo_5F_Frlg","SilphCo_6F_Frlg","SilphCo_7F_Frlg","SilphCo_8F_Frlg",
    "SilphCo_9F_Frlg","SilphCo_10F_Frlg","SilphCo_11F_Frlg","SilphCo_Elevator_Frlg",
    "PokemonMansion_1F_Frlg","PokemonMansion_2F_Frlg",
    "PokemonMansion_3F_Frlg","PokemonMansion_B1F_Frlg",
    "SafariZone_Center_Frlg","SafariZone_East_Frlg",
    "SafariZone_North_Frlg","SafariZone_West_Frlg",
    "SafariZone_Center_RestHouse_Frlg","SafariZone_East_RestHouse_Frlg",
    "SafariZone_North_RestHouse_Frlg","SafariZone_West_RestHouse_Frlg",
    "SafariZone_SecretHouse_Frlg",
    "CeruleanCave_1F_Frlg","CeruleanCave_2F_Frlg","CeruleanCave_B1F_Frlg",
    "PokemonLeague_LoreleisRoom_Frlg","PokemonLeague_BrunosRoom_Frlg",
    "PokemonLeague_AgathasRoom_Frlg","PokemonLeague_LancesRoom_Frlg",
    "PokemonLeague_ChampionsRoom_Frlg","PokemonLeague_HallOfFame_Frlg",
    "RockTunnel_1F_Frlg","RockTunnel_B1F_Frlg",
    "SeafoamIslands_1F_Frlg","SeafoamIslands_B1F_Frlg",
    "SeafoamIslands_B2F_Frlg","SeafoamIslands_B3F_Frlg","SeafoamIslands_B4F_Frlg",
    "PokemonTower_1F_Frlg","PokemonTower_2F_Frlg","PokemonTower_3F_Frlg",
    "PokemonTower_4F_Frlg","PokemonTower_5F_Frlg","PokemonTower_6F_Frlg","PokemonTower_7F_Frlg",
    "PowerPlant_Frlg",
}

# OLD mainland Kanto entries to REMOVE from gMapGroup_TownsAndRoutes_Frlg
_OLD_MAINLAND_TOWNS_ROUTES = {
    "PalletTown_Frlg","ViridianCity_Frlg","PewterCity_Frlg","CeruleanCity_Frlg",
    "VermilionCity_Frlg","LavenderTown_Frlg","CeladonCity_Frlg","SaffronCity_Frlg",
    "FuchsiaCity_Frlg","CinnabarIsland_Frlg","IndigoPlateau_Exterior_Frlg",
    "IndigoPlateau_Frlg","SaffronCity_Connection_Frlg",
    "Route1_Frlg","Route2_Frlg","Route3_Frlg","Route4_Frlg","Route5_Frlg",
    "Route6_Frlg","Route7_Frlg","Route8_Frlg","Route9_Frlg","Route10_Frlg",
    "Route11_Frlg","Route12_Frlg","Route13_Frlg","Route14_Frlg","Route15_Frlg",
    "Route16_Frlg","Route17_Frlg","Route18_Frlg","Route19_Frlg","Route20_Frlg",
    "Route21_North_Frlg","Route21_South_Frlg","Route22_Frlg","Route23_Frlg",
    "Route24_Frlg","Route25_Frlg",
}

# Indoor groups to fully replace with HnS content
_INDOOR_GROUPS_REPLACE = {
    "gMapGroup_IndoorPallet_Frlg",
    "gMapGroup_IndoorViridian_Frlg",
    "gMapGroup_IndoorPewter_Frlg",
    "gMapGroup_IndoorCerulean_Frlg",
    "gMapGroup_IndoorVermilion_Frlg",
    "gMapGroup_IndoorLavender_Frlg",
    "gMapGroup_IndoorCeladon_Frlg",
    "gMapGroup_IndoorSaffron_Frlg",
    "gMapGroup_IndoorFuchsia_Frlg",
    "gMapGroup_IndoorCinnabar_Frlg",
}

# Old route-specific groups that are deprecated (content moved to IndoorKantoRoutes)
_OLD_ROUTE_INDOOR_GROUPS = {
    "gMapGroup_IndoorRoute2_Frlg","gMapGroup_IndoorRoute4_Frlg",
    "gMapGroup_IndoorRoute5_Frlg","gMapGroup_IndoorRoute6_Frlg",
    "gMapGroup_IndoorRoute7_Frlg","gMapGroup_IndoorRoute8_Frlg",
    "gMapGroup_IndoorRoute10_Frlg","gMapGroup_IndoorRoute11_Frlg",
    "gMapGroup_IndoorRoute12_Frlg","gMapGroup_IndoorRoute15_Frlg",
    "gMapGroup_IndoorRoute16_Frlg","gMapGroup_IndoorRoute18_Frlg",
    "gMapGroup_IndoorRoute22_Frlg","gMapGroup_IndoorRoute25_Frlg",
    "gMapGroup_IndoorIndigoPlateau_Frlg",
}

# ===========================================================================
# Helpers
# ===========================================================================

def translate_map_const(const):
    """MAP_X → MAP_X_FRLG if Kanto, else unchanged."""
    if const in KANTO_MAP_CONSTS:
        return const + "_FRLG"
    return const


def translate_tileset(ts, is_primary=False):
    if is_primary:
        return ts  # primary names are identical in our project
    if not ts:
        return ts
    if ts.endswith("_Frlg") or ts.endswith("_frlg"):
        return ts
    return ts + "_Frlg"


def md5file(path):
    return hashlib.md5(open(path, 'rb').read()).hexdigest()


# ===========================================================================
# Layout JSON helpers
# ===========================================================================

def load_hns_layouts():
    with open(HNS_LAYOUTS_JSON) as f:
        return json.load(f)["layouts"]


def find_hns_layout(hns_layouts, layout_id):
    for l in hns_layouts:
        if l.get("id") == layout_id:
            return l
    return None


def build_our_layout_entry(hns_entry, our_frlg_name):
    """Transform an HnS layouts.json entry for our _Frlg version."""
    hns_id   = hns_entry.get("id", "")
    our_id   = hns_id + "_FRLG" if not hns_id.endswith("_FRLG") else hns_id
    our_name = our_frlg_name + "_Layout"
    return {
        "id":                 our_id,
        "name":               our_name,
        "width":              hns_entry.get("width", 20),
        "height":             hns_entry.get("height", 20),
        "border_width":       hns_entry.get("border_width", 2),
        "border_height":      hns_entry.get("border_height", 2),
        "primary_tileset":    translate_tileset(hns_entry.get("primary_tileset","gTileset_General"), is_primary=True),
        "secondary_tileset":  translate_tileset(hns_entry.get("secondary_tileset","gTileset_Pallet_Town")),
        "border_filepath":    f"data/layouts/{our_frlg_name}/border.bin",
        "blockdata_filepath": f"data/layouts/{our_frlg_name}/map.bin",
        "layout_version":     "frlg",
    }


# ===========================================================================
# Map JSON transformation
# ===========================================================================

def transform_map_json(hns_data, hns_name, our_frlg_name, our_layout_id):
    d = json.loads(json.dumps(hns_data))  # deep copy

    d["id"]     = _camel_to_const(our_frlg_name)
    d["name"]   = our_frlg_name
    d["layout"] = our_layout_id
    d["region"] = "REGION_KANTO"

    # Music
    music = d.get("music", "")
    if music:
        d["music"] = MUSIC_TRANSLATE.get(music, music)

    # Warp dest_map
    for w in d.get("warp_events", []) or []:
        dm = w.get("dest_map", "")
        if dm:
            w["dest_map"] = translate_map_const(dm)

    # Connection map consts
    for c in d.get("connections", []) or []:
        m = c.get("map", "")
        if m:
            c["map"] = translate_map_const(m)

    return d


# ===========================================================================
# Per-map migration
# ===========================================================================

def migrate_map(hns_name, hns_layouts, our_layouts_by_id, dry_run=False):
    our_frlg_name  = hns_name + "_Frlg"
    hns_map_dir    = os.path.join(HNS_MAPS_DIR, hns_name)
    our_map_dir    = os.path.join(MAPS_DIR, our_frlg_name)
    our_layout_dir = os.path.join(LAYOUTS_DIR, our_frlg_name)
    hns_map_json   = os.path.join(hns_map_dir, "map.json")

    if not os.path.exists(hns_map_json):
        print(f"  [SKIP] {hns_name}: no HnS map.json")
        return None

    with open(hns_map_json) as f:
        hns_data = json.load(f)

    hns_layout_id = hns_data.get("layout", "")
    hns_entry     = find_hns_layout(hns_layouts, hns_layout_id)

    if not hns_entry:
        print(f"  [WARN] {hns_name}: layout '{hns_layout_id}' not found in HnS layouts.json")
        our_layout_id = hns_layout_id + "_FRLG"
    else:
        our_layout_id = hns_layout_id + "_FRLG" if not hns_layout_id.endswith("_FRLG") else hns_layout_id

    # ---- layout binaries ----
    hns_layout_folder_rel = hns_entry.get("blockdata_filepath", "") if hns_entry else ""
    if hns_layout_folder_rel:
        hns_layout_folder = os.path.join(HNS_ROOT, os.path.dirname(hns_layout_folder_rel))
    else:
        hns_layout_folder = os.path.join(HNS_LAYOUTS_DIR, hns_name)

    copied_bins = []
    for fname in ("map.bin", "border.bin"):
        src = os.path.join(hns_layout_folder, fname)
        dst = os.path.join(our_layout_dir, fname)
        if os.path.exists(src):
            same = os.path.exists(dst) and md5file(src) == md5file(dst)
            if not same:
                copied_bins.append(fname)
                if not dry_run:
                    os.makedirs(our_layout_dir, exist_ok=True)
                    shutil.copy2(src, dst)

    # ---- layouts.json entry ----
    new_layout_entry = None
    if hns_entry:
        new_layout_entry = build_our_layout_entry(hns_entry, our_frlg_name)

    # ---- map.json ----
    our_data   = transform_map_json(hns_data, hns_name, our_frlg_name, our_layout_id)
    map_json_path = os.path.join(our_map_dir, "map.json")
    map_exists = os.path.exists(map_json_path)

    if not dry_run:
        os.makedirs(our_map_dir, exist_ok=True)
        with open(map_json_path, 'w') as f:
            json.dump(our_data, f, indent=4)
            f.write('\n')

    # ---- scripts.inc stub ----
    scripts_path = os.path.join(our_map_dir, "scripts.inc")
    scripts_created = False
    if not os.path.exists(scripts_path):
        scripts_created = True
        if not dry_run:
            with open(scripts_path, 'w') as f:
                f.write(f"\t.include \"data/maps/{our_frlg_name}/scripts.inc\"\n")

    tag = "UPD" if map_exists else "NEW"
    extras = []
    if copied_bins: extras.append(f"bins:{','.join(copied_bins)}")
    if scripts_created: extras.append("scripts.inc")
    extra_str = f"  ({', '.join(extras)})" if extras else ""
    print(f"  [{tag}] {our_frlg_name}{extra_str}")

    return new_layout_entry


# ===========================================================================
# layouts.json update
# ===========================================================================

def update_layouts_json(new_entries, dry_run=False):
    with open(LAYOUTS_JSON) as f:
        data = json.load(f)

    by_id = {l["id"]: i for i, l in enumerate(data["layouts"])}
    added = updated = 0

    for entry in new_entries:
        if entry is None:
            continue
        eid = entry["id"]
        if eid in by_id:
            if data["layouts"][by_id[eid]] != entry:
                if not dry_run:
                    data["layouts"][by_id[eid]] = entry
                updated += 1
        else:
            if not dry_run:
                data["layouts"].append(entry)
                by_id[eid] = len(data["layouts"]) - 1
            added += 1

    if not dry_run and (added or updated):
        with open(LAYOUTS_JSON, 'w') as f:
            json.dump(data, f, indent=4)
            f.write('\n')

    print(f"  layouts.json: +{added} new, ~{updated} updated")


# ===========================================================================
# map_groups.json update
# ===========================================================================

def update_map_groups_json(dry_run=False):
    with open(MAP_GROUPS_JSON) as f:
        mg = json.load(f)

    group_order = list(mg.get("group_order", []))

    # 1.  Fully replace indoor Kanto groups
    for grp in _INDOOR_GROUPS_REPLACE:
        if grp in mg and grp in HNS_KANTO_GROUPS:
            new_maps = [m + "_Frlg" for m in HNS_KANTO_GROUPS[grp]]
            before = len(mg[grp])
            if not dry_run:
                mg[grp] = new_maps
            print(f"  [REPLACE] {grp}: {before}→{len(new_maps)} maps")

    # 2.  gMapGroup_TownsAndRoutes_Frlg — replace mainland Kanto, keep Sevii
    if "gMapGroup_TownsAndRoutes_Frlg" in mg:
        old = mg["gMapGroup_TownsAndRoutes_Frlg"]
        keep = [m for m in old if m not in _OLD_MAINLAND_TOWNS_ROUTES]
        new_kanto = [m + "_Frlg" for m in HNS_KANTO_GROUPS["gMapGroup_TownsAndRoutes_Frlg"]]
        combined = new_kanto + keep
        if not dry_run:
            mg["gMapGroup_TownsAndRoutes_Frlg"] = combined
        print(f"  [REPLACE] gMapGroup_TownsAndRoutes_Frlg: "
              f"{len(new_kanto)} Kanto + {len(keep)} kept = {len(combined)}")

    # 3.  gMapGroup_Dungeons_Frlg — replace old Kanto dungeons, keep Sevii/SSAnne
    if "gMapGroup_Dungeons_Frlg" in mg:
        old = mg["gMapGroup_Dungeons_Frlg"]
        keep = [m for m in old if m not in _OLD_KANTO_DUNGEONS]
        new_kanto = [m + "_Frlg" for m in HNS_KANTO_GROUPS["_kanto_dungeons_"]]
        combined = new_kanto + keep
        removed = len(old) - len(keep)
        if not dry_run:
            mg["gMapGroup_Dungeons_Frlg"] = combined
        print(f"  [REPLACE] gMapGroup_Dungeons_Frlg: -{removed} old, +{len(new_kanto)} HnS, "
              f"kept {len(keep)} Sevii = {len(combined)}")

    # 4.  Remove obsolete route-indoor groups (drop from group_order, clear contents)
    for grp in _OLD_ROUTE_INDOOR_GROUPS:
        if grp in mg:
            old_len = len(mg[grp])
            if not dry_run:
                mg[grp] = []   # clear contents (don't remove key in case referenced)
            print(f"  [CLEAR]   {grp}: was {old_len} maps (merged into IndoorKantoRoutes)")

    # 5.  Add new groups: IndoorIndigo_Frlg and IndoorKantoRoutes_Frlg
    for new_grp in ("gMapGroup_IndoorIndigo_Frlg", "gMapGroup_IndoorKantoRoutes_Frlg"):
        maps = [m + "_Frlg" for m in HNS_KANTO_GROUPS.get(new_grp, [])]
        if new_grp not in mg:
            if not dry_run:
                mg[new_grp] = maps
                # Insert after IndoorCinnabar_Frlg in group_order
                ref = "gMapGroup_IndoorCinnabar_Frlg"
                if ref in group_order:
                    idx = group_order.index(ref) + 1
                    group_order.insert(idx, new_grp)
                else:
                    group_order.append(new_grp)
            print(f"  [ADD]     {new_grp}: {len(maps)} maps")
        else:
            if not dry_run:
                mg[new_grp] = maps
            print(f"  [REPLACE] {new_grp}: {len(maps)} maps")

    if not dry_run:
        mg["group_order"] = group_order
        with open(MAP_GROUPS_JSON, 'w') as f:
            json.dump(mg, f, indent=4)
            f.write('\n')


# ===========================================================================
# Main
# ===========================================================================

def main():
    ap = argparse.ArgumentParser(description="Migrate HnS Kanto maps → _Frlg in our project")
    ap.add_argument("--dry-run",      action="store_true", help="Preview only, write nothing")
    ap.add_argument("--only",         metavar="NAME",      help="Migrate only this HnS map name")
    ap.add_argument("--skip-groups",  action="store_true", help="Skip map_groups.json update")
    ap.add_argument("--skip-layouts", action="store_true", help="Skip layouts.json update")
    args = ap.parse_args()

    if args.dry_run:
        print("DRY RUN — no files will be written.\n")

    # Which maps to process
    if args.only:
        if args.only not in ALL_KANTO_HNS:
            print(f"ERROR: '{args.only}' not in authoritative Kanto map list")
            sys.exit(1)
        to_migrate = [args.only]
    else:
        to_migrate = sorted(ALL_KANTO_HNS)

    print(f"Migrating {len(to_migrate)} maps from HnS...\n")

    hns_layouts = load_hns_layouts()
    our_layouts_by_id = {}  # populated lazily

    new_layout_entries = []
    ok = skip = 0

    for hns_name in to_migrate:
        result = migrate_map(hns_name, hns_layouts, our_layouts_by_id, dry_run=args.dry_run)
        if result is None and os.path.exists(os.path.join(HNS_MAPS_DIR, hns_name, "map.json")):
            # returned None because layout missing — still count as ok (layout-less maps)
            ok += 1
        elif result is None:
            skip += 1
        else:
            new_layout_entries.append(result)
            ok += 1

    print(f"\nMaps: {ok} processed, {skip} skipped.\n")

    if not args.skip_layouts:
        print("Updating layouts.json...")
        update_layouts_json(new_layout_entries, dry_run=args.dry_run)

    if not args.skip_groups:
        print("\nUpdating map_groups.json...")
        update_map_groups_json(dry_run=args.dry_run)

    print("\nDone." + (" (DRY RUN — nothing written)" if args.dry_run else ""))
    if not args.dry_run:
        print("Next: run  make -j$(nproc)  to rebuild.")


if __name__ == "__main__":
    main()
