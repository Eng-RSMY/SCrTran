import Foundation

/// Talks to a configurable translation backend.
///
/// Two providers are supported out of the box:
///   - "openai": any OpenAI-compatible `/chat/completions` endpoint
///     (OpenAI, Azure OpenAI, or a self-hosted LLM such as Ollama/LM Studio).
///   - "deepl": the DeepL REST API.
///
/// This is the "API app" core: every endpoint is set by the user in Settings,
/// so no key or service is hard-coded.
final class TranslationService {
    static let shared = TranslationService()

    enum ServiceError: Error {
        case invalidResponse
        case httpError(Int)
        case noData
        case decodingFailed
        case emptyInput
    }

    /// Translates an array of strings, preserving order. Each element is
    /// translated independently so line alignment with the OCR text is kept.
    func translate(texts: [String], config: SharedConfig, completion: @escaping (Result<[String], Error>) -> Void) {
        let cleaned = texts.map { $0.trimmingCharacters(in: .whitespacesAndNewlines) }
                          .filter { !$0.isEmpty }
        guard !cleaned.isEmpty else { completion(.failure(ServiceError.emptyInput)); return }

        switch config.service.lowercased() {
        case "deepl":
            translateDeepL(texts: cleaned, config: config, completion: completion)
        default:
            translateOpenAI(texts: cleaned, config: config, completion: completion)
        }
    }

    // MARK: - OpenAI compatible

    private func translateOpenAI(texts: [String], config: SharedConfig, completion: @escaping (Result<[String], Error>) -> Void) {
        guard let url = URL(string: config.apiBaseURL)?.appendingPathComponent("chat/completions") else {
            completion(.failure(ServiceError.invalidResponse)); return
        }

        let targetNote = config.targetLanguage
        let sourceNote = config.sourceLanguage == "auto" ? "the detected source language" : config.sourceLanguage
        let systemPrompt = """
        You are a precise translator. You will receive a JSON array of strings.
        Translate each element into \(targetNote) from \(sourceNote).
        Preserve the original meaning and tone. Do not merge or reorder elements.
        Respond with ONLY a JSON array of strings of the exact same length and order,
        with no extra text, keys, or markdown formatting.
        """

        let userContent: String
        if let data = try? JSONSerialization.data(withJSONObject: texts),
           let str = String(data: data, encoding: .utf8) {
            userContent = str
        } else {
            userContent = "[]"
        }

        let payload: [String: Any] = [
            "model": config.model,
            "temperature": 0,
            "messages": [
                ["role": "system", "content": systemPrompt],
                ["role": "user", "content": userContent]
            ],
            "response_format": ["type": "json_object"]
        ]

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(config.apiKey)", forHTTPHeaderField: "Authorization")
        request.timeoutInterval = 30
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error { completion(.failure(error)); return }
            guard let http = response as? HTTPURLResponse else { completion(.failure(ServiceError.invalidResponse)); return }
            guard (200..<300).contains(http.statusCode) else { completion(.failure(ServiceError.httpError(http.statusCode))); return }
            guard let data = data else { completion(.failure(ServiceError.noData)); return }

            guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let choices = obj["choices"] as? [[String: Any]],
                  let message = choices.first?["message"] as? [String: Any],
                  let content = message["content"] as? String,
                  let arr = try? JSONSerialization.jsonObject(with: Data(content.utf8)) as? [String] else {
                completion(.failure(ServiceError.decodingFailed)); return
            }
            completion(.success(arr))
        }.resume()
    }

    // MARK: - DeepL

    private func translateDeepL(texts: [String], config: SharedConfig, completion: @escaping (Result<[String], Error>) -> Void) {
        let endpoint = "https://api-free.deepl.com/v2/translate"
        guard let url = URL(string: endpoint) else { completion(.failure(ServiceError.invalidResponse)); return }

        var components = URLComponents(url: url, resolvingAgainstBaseURL: false)!
        var items: [URLQueryItem] = [URLQueryItem(name: "target_lang", value: config.targetLanguage.uppercased())]
        if config.sourceLanguage != "auto" {
            items.append(URLQueryItem(name: "source_lang", value: config.sourceLanguage.uppercased()))
        }
        for t in texts {
            items.append(URLQueryItem(name: "text", value: t))
        }
        components.queryItems = items

        var request = URLRequest(url: components.url!)
        request.httpMethod = "POST"
        request.setValue("DeepL-Auth-Key \(config.apiKey)", forHTTPHeaderField: "Authorization")
        request.timeoutInterval = 30

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error { completion(.failure(error)); return }
            guard let http = response as? HTTPURLResponse else { completion(.failure(ServiceError.invalidResponse)); return }
            guard (200..<300).contains(http.statusCode) else { completion(.failure(ServiceError.httpError(http.statusCode))); return }
            guard let data = data else { completion(.failure(ServiceError.noData)); return }

            guard let obj = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let translations = obj["translations"] as? [[String: Any]] else {
                completion(.failure(ServiceError.decodingFailed)); return
            }
            let result = translations.compactMap { $0["text"] as? String }
            completion(.success(result))
        }.resume()
    }
}
