import ReplayKit
import Vision
import CoreImage

/// Broadcast Upload Extension.
///
/// When the user starts a system screen broadcast (via the app's
/// `RPSystemBroadcastPickerView`), iOS calls this handler for every video frame.
/// We throttle to ~1 fps, run on-device Vision OCR, send the text to the
/// configured translation API, and append the result to the shared
/// `translations.json` file in the App Group, which the main app displays.
class SampleHandler: RPBroadcastSampleHandler {

    private var lastProcess = Date.distantPast
    private let minimumInterval: TimeInterval = 1.0
    private let ciContext = CIContext()

    override func broadcastStarted(withSetupInfo setupInfo: [String: NSObject]?) {
        // Reset the queue when a new broadcast begins.
        if let url = AppGroup.translationsFile {
            try? Data().write(to: url)
        }
    }

    override func broadcastPaused() {}
    override func broadcastResumed() {}
    override func broadcastFinished() {}

    override func processSampleBuffer(_ sampleBuffer: CMSampleBuffer, with sampleType: RPSampleBufferType) {
        guard sampleType == .video else { return }

        let now = Date()
        guard now.timeIntervalSince(lastProcess) >= minimumInterval else { return }
        lastProcess = now

        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        let ciImage = CIImage(cvImageBuffer: imageBuffer)
        guard let cgImage = ciContext.createCGImage(ciImage, from: ciImage.extent) else { return }

        let config = SharedConfig.load()
        guard config.translationEnabled, !config.apiKey.isEmpty else { return }

        OCRManager.shared.recognize(image: cgImage, language: config.ocrLanguage) { [weak self] lines in
            guard !lines.isEmpty else { return }
            TranslationService.shared.translate(texts: lines, config: config) { result in
                if case .success(let targets) = result {
                    self?.append(lines: lines, targets: targets, config: config)
                }
            }
        }
    }

    private func append(lines: [String], targets: [String], config: SharedConfig) {
        let count = min(lines.count, targets.count)
        var items: [TranslationItem] = []
        for i in 0..<count {
            items.append(TranslationItem(source: lines[i], target: targets[i],
                                         sourceLanguage: config.sourceLanguage,
                                         targetLanguage: config.targetLanguage))
        }
        guard let url = AppGroup.translationsFile else { return }

        var existing: [TranslationItem] = []
        if let data = try? Data(contentsOf: url),
           let decoded = try? JSONDecoder().decode([TranslationItem].self, from: data) {
            existing = decoded
        }
        existing.append(contentsOf: items)
        if existing.count > 500 { existing.removeFirst(existing.count - 500) }
        if let data = try? JSONEncoder().encode(existing) {
            try? data.write(to: url, options: .atomic)
        }
    }
}
