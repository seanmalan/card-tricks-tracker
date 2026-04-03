import threading
import time
import sys

from app import create_app

PORT = 5757


def run_flask(flask_app):
    flask_app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


def main():
    flask_app = create_app()

    t = threading.Thread(target=run_flask, args=(flask_app,), daemon=True)
    t.start()

    # Brief pause to let Flask bind the port
    time.sleep(0.6)

    try:
        import gi
        try:
            gi.require_version('WebKit2', '4.1')
        except ValueError:
            gi.require_version('WebKit2', '4.0')
        import webview
        webview.create_window(
            "Prestige — Card Magic Tracker",
            f"http://127.0.0.1:{PORT}",
            width=1200,
            height=780,
            min_size=(900, 600),
        )
        webview.start()
    except ImportError:
        # Fallback: open in browser if pywebview not available
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{PORT}")
        print(f"App running at http://127.0.0.1:{PORT}  (press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
