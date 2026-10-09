#!/usr/bin/env python3
"""Local preview server with auto-rebuild.

    python3 tools/serve.py            # http://localhost:8000
    python3 tools/serve.py 8080       # pick a different port

Serves _site_preview/ and watches the source files. Edit anything under _data,
_pages, _includes, _layouts, assets or images and it rebuilds within
about half a second — just refresh the browser.

Stdlib only, and it shells out to `ruby tools/preview.rb`, so there is nothing
to install beyond the liquid/kramdown gems that script already needs.

Ctrl-C to stop.
"""

import functools
import http.server
import os
import socketserver
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_site_preview')

# so progress still appears promptly when the output is piped or redirected
try:
    sys.stdout.reconfigure(line_buffering=True)
except AttributeError:
    pass

WATCH_DIRS = ['_data', '_pages', '_includes', '_layouts',
              'assets', 'images', 'tools']
WATCH_FILES = ['_config.yml']
IGNORE_SUFFIX = ('.swp', '.swx', '~', '.pyc')


def snapshot():
    """Map of watched file -> mtime."""
    state = {}
    for rel in WATCH_FILES:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            state[p] = os.stat(p).st_mtime
    for rel in WATCH_DIRS:
        base = os.path.join(ROOT, rel)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            for f in filenames:
                if f.startswith('.') or f.endswith(IGNORE_SUFFIX):
                    continue
                p = os.path.join(dirpath, f)
                try:
                    state[p] = os.stat(p).st_mtime
                except OSError:
                    pass
    return state


def build():
    """Run the renderer. Returns True on success."""
    started = time.time()
    proc = subprocess.run(['ruby', os.path.join('tools', 'preview.rb')],
                          cwd=ROOT, capture_output=True, text=True)
    stamp = time.strftime('%H:%M:%S')
    if proc.returncode == 0:
        n = sum(1 for line in proc.stdout.splitlines() if line.startswith('  /'))
        print(f'[{stamp}] rebuilt {n} pages in {time.time() - started:.1f}s')
        return True
    print(f'[{stamp}] BUILD FAILED')
    for line in (proc.stdout + proc.stderr).strip().splitlines():
        print(f'    {line}')
    print('    (previous build is still being served)')
    return False


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # always re-fetch, so a refresh really shows the latest build
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        super().end_headers()

    def log_message(self, *args):
        pass  # the rebuild log is the interesting one


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    if not build():
        print('\nFirst build failed — fix the error above and re-run.')
        return 1

    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(Handler, directory=OUT)
    try:
        httpd = socketserver.TCPServer(('', port), handler)
    except OSError as e:
        print(f'\nCould not bind port {port}: {e}')
        print(f'Something else is using it. Try: python3 tools/serve.py {port + 1}')
        return 1

    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f'\n  Serving http://localhost:{port}  — watching for changes, Ctrl-C to stop\n')

    state = snapshot()
    try:
        while True:
            time.sleep(0.5)
            new = snapshot()
            if new != state:
                changed = [os.path.relpath(p, ROOT)
                           for p in set(new) ^ set(state)
                           or [k for k in new if state.get(k) != new[k]]]
                if changed:
                    print(f'  changed: {", ".join(sorted(changed)[:4])}'
                          + (' …' if len(changed) > 4 else ''))
                time.sleep(0.2)          # let a multi-file save settle
                build()
                state = snapshot()
    except KeyboardInterrupt:
        print('\nstopped')
        return 0


if __name__ == '__main__':
    sys.exit(main())
