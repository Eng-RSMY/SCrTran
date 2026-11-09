import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var store: TranslationStore
    @Environment(\.dismiss) private var dismiss
    @State private var cfg: SharedConfig = .default

    var body: some View {
        NavigationView {
            Form {
                Section("Translation Service") {
                    Picker("Provider", selection: $cfg.service) {
                        Text("OpenAI compatible").tag("openai")
                        Text("DeepL").tag("deepl")
                    }
                    .pickerStyle(.segmented)

                    if cfg.service == "openai" {
                        TextField("API Base URL", text: $cfg.apiBaseURL)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                        TextField("Model", text: $cfg.model)
                            .textInputAutocapitalization(.never)
                            .autocorrectionDisabled()
                    }
                    SecureField("API Key", text: $cfg.apiKey)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                }

                Section("Languages") {
                    TextField("Source (auto or code, e.g. ja)", text: $cfg.sourceLanguage)
                        .textInputAutocapitalization(.never)
                    TextField("Target (e.g. en)", text: $cfg.targetLanguage)
                        .textInputAutocapitalization(.never)
                    TextField("OCR language (e.g. ja)", text: $cfg.ocrLanguage)
                        .textInputAutocapitalization(.never)
                }

                Section {
                    Toggle("Translation enabled (extension)", isOn: $cfg.translationEnabled)
                } header: {
                    Text("Extension")
                } footer: {
                    Text("Config is shared with the broadcast extension through the App Group '\(AppGroup.identifier)'. Create this App Group in your Apple Developer account and enable it for both targets.")
                }

                Section {
                    Button("Save") {
                        store.config = cfg
                        store.saveConfig()
                        dismiss()
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                    .bold()
                }
            }
            .navigationTitle("Settings")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") { dismiss() }
                }
            }
            .onAppear { cfg = store.config }
        }
    }
}
