import Foundation

/// One recognized line of text (OCR) paired with its translation.
struct TranslationItem: Identifiable, Codable {
    let id: UUID
    let source: String
    let target: String
    let sourceLanguage: String
    let targetLanguage: String
    let timestamp: Date

    init(id: UUID = UUID(),
         source: String,
         target: String,
         sourceLanguage: String,
         targetLanguage: String,
         timestamp: Date = Date()) {
        self.id = id
        self.source = source
        self.target = target
        self.sourceLanguage = sourceLanguage
        self.targetLanguage = targetLanguage
        self.timestamp = timestamp
    }
}
