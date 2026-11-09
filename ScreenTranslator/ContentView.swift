import SwiftUI
import ReplayKit
import PhotosUI

struct ContentView: View {
    @EnvironmentObject var store: TranslationStore
    @State private var showSettings = false
    @State private var showPhotoPicker = false
    @State private var selectedPhoto: PhotosPickerItem?

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    Text("Screen Translator")
                        .font(.largeTitle).bold()

                    Text("Start a system screen broadcast. The extension captures the screen, runs on-device OCR, and sends the text to your configured translation API. Results appear below in near real time.")
                        .font(.subheadline).foregroundColor(.secondary)

                    BroadcastButton()
                        .frame(height: 44)

                    Button {
                        showPhotoPicker = true
                    } label: {
                        Label("Translate a Photo", systemImage: "photo")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)

                    Divider()

                    Text("Live translations")
                        .font(.headline)
                    LiveOverlayView(items: store.liveItems)

                    Divider()

                    Text("History")
                        .font(.headline)
                    if store.history.isEmpty {
                        Text("No translations yet.").foregroundColor(.secondary)
                    } else {
                        ForEach(store.history.reversed()) { item in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.source).font(.body)
                                Text(item.target).font(.body).bold().foregroundColor(.blue)
                                Divider()
                            }
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Translator")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button { showSettings = true } label: {
                        Image(systemName: "gearshape")
                    }
                }
            }
            .sheet(isPresented: $showSettings) {
                SettingsView().environmentObject(store)
            }
            .photosPicker(isPresented: $showPhotoPicker, selection: $selectedPhoto)
            .onChange(of: selectedPhoto) { handlePhoto($0) }
        }
    }

    private func handlePhoto(_ item: PhotosPickerItem?) {
        guard let item = item else { return }
        Task {
            if let data = try? await item.loadTransferable(type: Data.self),
               let image = UIImage(data: data)?.cgImage {
                let lines = await withCheckedContinuation { (cont: CheckedContinuation<[String], Never>) in
                    OCRManager.shared.recognize(image: image, language: store.config.ocrLanguage) { lines in
                        cont.resume(returning: lines)
                    }
                }
                store.translatePhoto(lines: lines)
            }
        }
    }
}

/// Wraps `RPSystemBroadcastPickerView` so the user can pick and start the
/// broadcast extension from within the app.
struct BroadcastButton: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let picker = RPSystemBroadcastPickerView(frame: CGRect(x: 0, y: 0, width: 240, height: 44))
        picker.preferredExtension = "com.example.screentranslator.broadcast"
        picker.showsMicrophoneButton = false
        picker.tintColor = UIColor.systemBlue
        return picker
    }

    func updateUIView(_ uiView: UIView, context: Context) {}
}
