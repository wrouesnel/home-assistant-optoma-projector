# Home Assistant Optoma Projector Integration

## Description

Integration developed to control an Optoma UHD series projector from its web interface
via Home Assistant.

## Features

* Configure via the Home Assistant UI
* All "Projector Control" commands from the Projector Web UI.
* IP control only (for now)

## Installation

### Home Assistant Community Store (HACS)

*Recommended as you get notified of updates.*

HACS is a 3rd party downloader for Home Assistant to easily install and update custom integrations made by the community. More information and installation instructions can be found on their site https://hacs.xyz/

* Add integration within HACS ([use a custom repository for now](https://hacs.xyz/docs/faq/custom_repositories/))
* Restart Home Assistant
* Go to the Home Assistant integrations menu and press the Add button and search for "Optoma Projector". You might need to clear the browser cache for it to show up (e.g. reload with CTRL+F5).

### Manual

* Install the custom component by downloading the zipfile from the releases.
* Extract the zip and copy the contents to the `custom_components` directory.
* Restart Home Assistant
* Go to the Home Assistant integrations menu and press the Add button and search for "Yamaha (YNCA)". You might need to clear the browser cache for it to show up (e.g. reload with CTRL+F5).

## Errata

Not all options are always available via the projector, but they can't be easily limited. If you try to click a toggle
or select an option and it reverts, it means the projector did not acknowledge the command.
