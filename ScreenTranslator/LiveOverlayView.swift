import SwiftUI

/// In-app preview of the live translation stream produced by the extension.
/// On iOS a third-party app cannot draw a system-wide overlay over other apps;
/// this view shows the same data the extension is producing, inside the app.
struct LiveOverlayView: View {
    let items: [TranslationItem]

    var body: some View {
        if items.isEmpty {
            Text("Waiting for screen broadcast…")
                .font(.caption).foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(8)
                .background(Color(.secondarySystemBackground))
                .cornerRadius(10)
        } else {
            VStack(alignment: .leading, spacing: 8) {
                ForEach(items) { item in
                    HStack(alignment: .top, spacing: 8) {
                        Text(item.source)
                            .foregroundColor(.primary)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        Image(systemName: "arrow.right")
                            .foregroundColor(.secondary)
                        Text(item.target)
                            .bold()
                            .foregroundColor(.blue)
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .padding(8)
                    .background(.ultraThinMaterial)
                    .cornerRadius(10)
                }
            }
        }
    }
}
