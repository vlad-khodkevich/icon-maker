# Icon Maker

**Icon Maker** is a lightweight Python CLI script for mobile developers that takes a single source image and automatically slices it into a complete, ready-to-use set of app icons for iOS and Android.

Instead of manually resizing and organizing artwork for dozens of platform requirements, Icon Maker sets up the exact folder structure, asset catalogs, and configurations with a single command.

## 💡 Philosophy

Managing app icons is tedious and error-prone. Icon Maker treats asset generation as a seamless utility — turning one high-resolution source square into meticulously structured assets for Xcode, Android Studio, and app stores instantly, while automatically handling platform specifics like transparency removal and background colors.

## 🚀 Key Features

- **Cross-platform generation** — build icons for iOS, Android, and Apple Watch simultaneously or target a specific platform
- **iOS & watchOS support** — generates all standard iPhone/iPad sizes, App Store icon (`1024x1024`), and automatically creates the required `Contents.json` file for Xcode
- **Android adaptive & legacy icons** — produces adaptive icon layers (`mipmap-anydpi-v26`) with separate foreground/background assets, rounded/circle legacy icons for older Android versions, and the Google Play store asset (`512x512`)
- **Smart background handling** — automatically detects background color from the image corners or lets you specify a custom color (`--bg`), along with support for custom foreground (`--fg`) and background layers

## 🛠 Tech Stack

- **Language**: [Python 3](https://www.python.org/)
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)
- **Architecture**: Single-file CLI script (`IconMaker.py`) using standard `argparse`, `pathlib`, and `json` modules

## 🏁 Getting Started

### Prerequisites

Make sure you have Python 3 and the Pillow library installed:

```bash
pip3 install pillow
```

### Usage
Use a square PNG image as your source (ideally 1024x1024 pixels or larger, without pre-rounded corners or transparent edges).

Basic run (generates icons for all platforms into the default icons_out folder):

```bash
python3 IconMaker.py icon.png
```

### Options
- `-o, --out <dir>` — specify a custom output directory (default: icons_out)
- `--platform <all|ios|android>` — generate icons for a specific platform only
- `--watch` — additionally generate Apple Watch icons
- `--bg <#RRGGBB>` — set a manual background color
- `--fg <path>` — (Android) provide your own transparent foreground layer
- `--help` — show full help message and all available flags