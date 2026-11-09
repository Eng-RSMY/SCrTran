# ScreenTranslator (iOS)

A GotachaScreenTranslator-style iOS app: it captures whatever is on the screen,
runs **on-device OCR** (Apple Vision), and sends the recognized text to a
**configurable translation API**, then shows the translation. Built so you can
open it in Xcode and archive a `.ipa` yourself.

## How it works

```
┌──────────────────────────┐      screen frames       ┌─────────────────────────────┐
│  Broadcast Upload Ext.    │ ───────────────────────▶│  SampleHandler              │
│  (ScreenTranslatorBroadcast)                        │   • Vision OCR (on-device)  │
└──────────────────────────┘                          │   • call translation API    │
                                                       │   • write to App Group      │
                                                       └──────────────┬──────────────┘
                                                                      │ translations.json
                                                                      ▼
                                                       ┌─────────────────────────────┐
                                                       │  Main App (ScreenTranslator)│
                                                       │   • reads App Group          │
                                                       │   • shows live translations  │
                                                       │   • Settings (API config)    │
                                                       │   • Photo translate mode     │
                                                       └─────────────────────────────┘
```

* **OCR** is fully local (Vision `VNRecognizeTextRequest`) — no cost, no latency.
* **Translation** is a network call to an API you configure. Two providers ship:
  *OpenAI-compatible* `/chat/completions` (OpenAI, Azure, or a self-hosted LLM)
  and *DeepL*. The endpoint, key, and model are editable in Settings.
* The extension and the app talk through an **App Group** container:
  the app writes `config.json`; the extension writes `translations.json`.

## Requirements

* macOS with **Xcode 15+**
* An **Apple Developer** account (free works for device testing via
  Personal Team; App Groups need at least a free account and a real provisioning
  profile). To distribute a real `.ipa` you need a paid account / Ad Hoc profile.
* An iOS device running **iOS 16.0+** (screen broadcast extensions do not run in
  the simulator).

## Build & archive to `.ipa`

1. **Generate the Xcode project** (already done, but re-runnable):
   ```bash
   python3 generate_project.py
   ```
   This writes `ScreenTranslator.xcodeproj`.

2. **Open in Xcode**
   ```bash
   open ScreenTranslator.xcodeproj
   ```

3. **Change the bundle identifiers** (they must be unique to you):
   * App: `com.example.screentranslator` → e.g. `com.yourname.screentranslator`
   * Extension: `com.example.screentranslator.broadcast` → matching `.broadcast`
   * Update `ContentView.swift` `picker.preferredExtension` to the new extension id.

4. **Create the App Group** in the [Apple Developer portal]
   (Identifiers → App Groups), e.g. `group.com.yourname.screentranslator`, and
   enable it for **both** targets (Signing & Capabilities → + App Groups). Update
   `AppGroup.identifier` in `Shared/AppGroup.swift` and the two `.entitlements`
   files to match.

5. **Set signing** (Signing & Capabilities → Team) for both targets.

6. **Archive**: Product → Archive, then Organizer → Distribute App →
   Ad Hoc / Development → Export. The exported `.ipa` is your installable build.

   Or from the command line:
   ```bash
   xcodebuild -project ScreenTranslator.xcodeproj \
     -scheme ScreenTranslator -configuration Release \
     -archivePath build/ST.xcarchive archive
   xcodebuild -exportArchive -archivePath build/ST.xcarchive \
     -exportOptionsPlist ExportOptions.plist -exportPath build/ipa
   ```

## Configuring the translation API

Open the app → gear icon:

| Field | Example | Notes |
|-------|---------|-------|
| Provider | `OpenAI compatible` / `DeepL` | |
| API Base URL | `https://api.openai.com/v1` | For Ollama/LM Studio use `http://<ip>:11434/v1` |
| Model | `gpt-4o-mini` | Any chat model; for local LLMs use e.g. `llama3` |
| API Key | `sk-...` | Stored in the App Group container (see note below) |
| Source | `auto` or `ja` | `auto` lets the model detect |
| Target | `en` | ISO language code |
| OCR language | `ja` | Vision recognition language (`en`, `ja`, `ko`, `zh-Hans`, `fr`…) |

> **Security note:** the API key is written to the App Group's shared container
> so the extension can read it. This is convenient for a personal app but not
> hardened. For production, move the key into the Keychain with a shared
> access group. For a **local** LLM there is no key to leak.

> **Local HTTP endpoints:** iOS blocks cleartext HTTP by default. If you point the
> base URL at a local server (`http://…`), add an `NSAppTransportSecurity`
> exception to `ScreenTranslator/Info.plist`.

## Limitations (iOS platform constraints)

* A third-party app **cannot draw a system-wide overlay** on top of other apps.
  The extension captures and translates; the app shows the live results in its
  own UI. For a floating overlay you would need a companion *Broadcast UI*
  extension or a jailbroken device — out of scope here.
* Screen broadcast only runs on a physical device, not the simulator.
* OCR accuracy depends on the chosen `ocrLanguage` and on font/contrast.

## Project layout

```
ScreenTranslator/
├── generate_project.py              # builds ScreenTranslator.xcodeproj
├── ScreenTranslator.xcodeproj/      # generated (app + broadcast extension)
├── ScreenTranslator/                # main app (SwiftUI)
│   ├── ScreenTranslatorApp.swift
│   ├── TranslationStore.swift       # config + live queue + photo mode
│   ├── ContentView.swift            # UI + broadcast picker + photo picker
│   ├── SettingsView.swift           # API configuration
│   ├── LiveOverlayView.swift        # in-app live translation preview
│   ├── Info.plist
│   └── ScreenTranslator.entitlements
├── ScreenTranslatorBroadcast/       # Broadcast Upload Extension
│   ├── SampleHandler.swift          # frame → OCR → translate → App Group
│   ├── Info.plist
│   └── ScreenTranslatorBroadcast.entitlements
└── Shared/                          # compiled into BOTH targets
    ├── AppGroup.swift               # App Group ids + config persistence
    ├── TranslationModels.swift
    ├── TranslationService.swift     # OpenAI + DeepL clients
    └── OCRManager.swift             # Vision OCR
```
