import Foundation
import SwiftUI

/// Central state for the app: holds the shared config, the live translations
/// streamed from the broadcast extension, the local history, and the in-app
/// photo-translate path.
final class TranslationStore: ObservableObject {
    @Published var config: SharedConfig = .default
    @Published var liveItems: [TranslationItem] = []
    @Published var history: [TranslationItem] = []

    private var timer: Timer?

    init() {
        loadConfig()
        startPolling()
    }

    deinit {
        timer?.invalidate()
    }

    // MARK: - Config

    func loadConfig() {
        config = SharedConfig.load()
    }

    func saveConfig() {
        config.save()
        loadConfig()
    }

    // MARK: - Live polling from the App Group

    private func startPolling() {
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.pollTranslations()
        }
    }

    private func pollTranslations() {
        guard let url = AppGroup.translationsFile,
              let data = try? Data(contentsOf: url),
              let items = try? JSONDecoder().decode([TranslationItem].self, from: data) else {
            return
        }
        let known = Set(history.map { $0.id })
        let fresh = items.filter { !known.contains($0.id) }
        guard !fresh.isEmpty else { return }

        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            self.history.append(contentsOf: fresh)
            if self.history.count > 500 { self.history.removeFirst(self.history.count - 500) }
            self.liveItems = Array(self.history.suffix(20).reversed())
        }
    }

    // MARK: - Photo translate (in-app, no extension required)

    func translatePhoto(lines: [String]) {
        guard !lines.isEmpty else { return }
        TranslationService.shared.translate(texts: lines, config: config) { [weak self] result in
            guard let self = self else { return }
            switch result {
            case .success(let targets):
                let count = min(lines.count, targets.count)
                let items = (0..<count).map {
                    TranslationItem(source: lines[$0], target: targets[$0],
                                    sourceLanguage: self.config.sourceLanguage,
                                    targetLanguage: self.config.targetLanguage)
                }
                DispatchQueue.main.async {
                    self.history.append(contentsOf: items)
                    self.liveItems = Array(self.history.suffix(20).reversed())
                }
            case .failure(let error):
                print("Translation error: \(error)")
            }
        }
    }
}
