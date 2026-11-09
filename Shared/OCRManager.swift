import Vision
import CoreImage

/// On-device OCR using Apple Vision. No network, no API cost.
final class OCRManager {
    static let shared = OCRManager()

    /// Recognizes text lines from a CGImage and returns them in reading order
    /// (top-to-bottom, then left-to-right).
    func recognize(image: CGImage, language: String, completion: @escaping ([String]) -> Void) {
        let request = VNRecognizeTextRequest { request, _ in
            guard let observations = request.results as? [VNRecognizedTextObservation] else {
                completion([]); return
            }
            let lines = observations.compactMap { obs in
                obs.topCandidates(1).first?.string
            }.filter { !$0.isEmpty }
            completion(lines)
        }

        // Vision expects short language codes, e.g. "en", "ja", "ko", "zh-Hans", "fr".
        request.recognitionLanguages = [language]
        request.usesLanguageCorrection = true
        request.recognitionLevel = .accurate

        let handler = VNImageRequestHandler(cgImage: image, options: [:])
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                try handler.perform([request])
            } catch {
                completion([])
            }
        }
    }
}
