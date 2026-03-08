#ifndef GUARD_CONSTANTS_REGIONS_H
#define GUARD_CONSTANTS_REGIONS_H

// Core-series regions
enum Region
{
    REGION_NONE,
    REGION_KANTO,
    REGION_JOHTO,
    REGION_HOENN,
    REGION_SINNOH,
    REGION_UNOVA,
    REGION_KALOS,
    REGION_ALOLA,
    REGION_GALAR,
    REGION_HISUI,
    REGION_PALDEA,
    REGIONS_COUNT,
};

enum KantoSubRegion
{
    KANTO_SUBREGION_KANTO,
    KANTO_SUBREGION_SEVII123,
    KANTO_SUBREGION_SEVII45,
    KANTO_SUBREGION_SEVII67,
    KANTO_SUBREGION_COUNT
};

// Kanto (FRLG) map groups span groups 34..74.
// UpdateCurrentRegionVar() in overworld.c uses these to auto-detect the current region
// and store it in VAR_CURRENT_REGION (see constants/vars.h).
#define MAP_GROUP_FRLG_FIRST  34
#define MAP_GROUP_FRLG_LAST   74

#endif  // GUARD_CONSTANTS_REGIONS_H
