import SwiftUI

@main
struct ScreenTranslatorApp: App {
    @StateObject private var store = TranslationStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .onAppear {
                    store.loadConfig()
                }
        }
    }
}
