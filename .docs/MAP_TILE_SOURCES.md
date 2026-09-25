# Map Tile Sources (No API Key Required)

Candidate XYZ tile providers for `tkintermapview`'s `set_tile_server()`, all usable without signing up for an API key. Each entry has a link to view the style live in a browser, plus a raw single-tile URL (zoom 5, x=16, y=10 — roughly Western Europe) so you can see the exact tile image tkintermapview would fetch.

## OpenStreetMap (current default)
- Live map: https://www.openstreetmap.org/#map=5/50/10
- Sample tile: https://a.tile.openstreetmap.org/5/16/10.png
- Tile server pattern: `https://a.tile.openstreetmap.org/{z}/{x}/{y}.png`
- Note: usage policy asks for light/reasonable use; heavy local caching should ideally go through a mirror or self-hosted setup — see https://operations.osmfoundation.org/policies/tiles/


## Esri (ArcGIS Online basemaps)
- Service directory: https://server.arcgisonline.com/arcgis/rest/services/World_Street_Map/MapServer
- World Street Map sample tile: https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/5/10/16
- World Imagery (satellite) sample tile: https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/5/10/16
- Tile server pattern: `https://server.arcgisonline.com/ArcGIS/rest/services/{style}/MapServer/tile/{z}/{y}/{x}` — note the `y`/`x` order is swapped vs. the other providers
- Note: ToS restricts local caching of tiles without a separate license/agreement

## OpenTopoMap
- Live map: https://opentopomap.org/#map=5/50/10
- Sample tile: https://a.tile.opentopomap.org/5/16/10.png
- Tile server pattern: `https://a.tile.opentopomap.org/{z}/{x}/{y}.png`
- Topographic style — shows elevation/terrain, good if terrain context matters for routes
