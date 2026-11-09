import Foundation

/// Shared constants and helpers for communication between the main app and the
/// Broadcast Upload Extension through an App Group container.
///
/// The main app writes the active `SharedConfig` to `config.json`; the extension
/// reads it. The extension writes the live translation queue to `translations.json`;
/// the app reads it and displays the results.
enum AppGroup {
    static let identifier = "group.com.example.screentranslator"

    static var containerURL: URL? {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: identifier)
    }

    /// Live translation queue: written by the extension, read by the app.
    static var translationsFile: URL? {
        containerURL?.appendingPathComponent("translations.json")
    }

    /// Active configuration: written by the app, read by the extension.
    static var configFile: URL? {
        containerURL?.appendingPathComponent("config.json")
    }
}

/// Configuration shared from the main app to the extension.
struct SharedConfig: Codable {
    var service: String = "openai"        // "openai" | "deepl"
    var apiBaseURL: String = "https://api.openai.com/v1"
    var apiKey: String = ""
    var model: String = "gpt-4o-mini"
    var sourceLanguage: String = "auto"   // "auto" or ISO code (e.g. "ja")
    var targetLanguage: String = "en"     // ISO code (e.g. "en")
    var ocrLanguage: String = "en"        // Vision recognition language
    var translationEnabled: Bool = true

    static let `default` = SharedConfig()
}

extension SharedConfig {
    static func load() -> SharedConfig {
        guard let url = AppGroup.configFile,
              let data = try? Data(contentsOf: url),
              let cfg = try? JSONDecoder().decode(SharedConfig.self, from: data) else {
            return .default
        }
        return cfg
    }

    func save() {
        guard let url = AppGroup.configFile else { return }
        if let data = try? JSONEncoder().encode(self) {
            try? data.write(to: url, options: .atomic)
        }
    }
}
