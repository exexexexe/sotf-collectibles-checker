# Forest Collectibles Checker

**Use it here: https://exexexexe.github.io/sotf-collectibles-checker/**

Steam only tells you how many items you have left for an achievement in Sons of the Forest. This page reads your save file and lists exactly which ones you're missing. It also shows where the items are on a map of the island.

It tracks these collection achievements:

| Tracker | Items | What counts |
|---|---|---|
| Note pages (Gumshoe) | 50 | Picked up |
| Blueprints (Interior Designer) | 16 | Added to your blueprint book |
| Solafite-plated weapons (Oooh Shiny) | 14 | Plated at the Solafite plater |
| Clothing | 11 | Picked up (includes Virginia's 4 outfits) |
| Action camera videos | 4 | Collected |
| Eat every edible | 37 | Eaten at least once |
| Craft all weapons | 5 | Crafted at least once |
| Print all 3D-printer items | 6 | Printed at least once |

Achievements that are only a count, like logs placed or days survived, are left out because Steam already shows those numbers.

## How to use it

1. Open the page and click **Choose save file…**
2. Press **Win + R**, paste `%USERPROFILE%\AppData\LocalLow\Endnight\SonsOfTheForest\Saves` and press Enter.
3. Open your Steam ID folder. Then open **SinglePlayer**, or **Multiplayer** if you host, or **MultiplayerClient** if you join someone else's game.
4. Open the save's number folder and pick **SaveData.zip**. Older saves have loose files instead, so pick **PlayerStateSaveData.json**.

Your save is read in your browser and never uploaded anywhere. Click **Show example save** to try the page without a save of your own.

## In-game mod (live tracking)

The web page only sees your progress as of your last save. The **CollectiblesTracker** mod tracks the same achievements live, while you play:

- Press **F7** to open a panel with your counts and the exact items you're missing. It also shows where each one is and how far away it is. **Page Up / Page Down** switch between achievements.
- Press **F8** to show or hide markers on your GPS for missing notes, blueprints, weapons to plate, clothing and action cameras. Each marker disappears once you have that item.
- When something counts, an on-screen message shows your new total.

> **Early version:** the mod builds and installs, but hasn't been tested in-game yet. The GPS markers are the part most likely to need fixing. If something doesn't work, please open an issue and include your RedLoader log.

**Install**

1. Install [RedLoader](https://github.com/ToniMacaroni/RedLoader) for Sons of the Forest.
2. Download `CollectiblesTracker.zip` from the [Releases page](https://github.com/exexexexe/sotf-collectibles-checker/releases).
3. Extract it into your game folder, so that `Mods\CollectiblesTracker.dll` ends up next to your other mods.

You can change the keys, marker range and other options in the in-game mod settings. The source code is in [`mod/`](mod/). The mod's item lists are generated from this page's lists, so the two always match.

## How it works

The page is a single static `index.html` plus `map.jpg`. It reads `PlayerStateSaveData.json` and checks these keys:

- `hasOwned_<id>` for notes and clothing
- `DiscoverablePageUnlocked_<id>` for blueprints
- `isPlated_<id>` for plated weapons
- `consumed.<id>` for food
- `crafted.<id>` for crafted and printed items
- `ActionCameraVideoCollected_<name>` for the videos

The item lists come from the game's own achievement assets. The world positions come from pickup objects in the game's scene files. The map is a shaded render of the game's terrain height data.

The `extract/` folder has the Python scripts (UnityPy) used to pull this data from a game install, plus the JSON they produced. Each script has the Steam install path written into it, so change that path if your game is installed somewhere else.

## Credits

This is a fan project and is not affiliated with Endnight Games. Sons of the Forest and its assets belong to Endnight Games.
