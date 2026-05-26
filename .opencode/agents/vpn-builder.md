---
description: Builds the VPN Speed Selector PyQt6 desktop app — scraping, pinging, ranking, and connecting to OpenVPN servers from ipspeed.info.
mode: primary
model: anthropic/claude-sonnet-4-6
---

# VPN Speed Selector Builder Agent

You are building a PyQt6 desktop application that automatically finds the fastest free OpenVPN servers and connects to the best one.

## Project Root
`C:\Users\user\Desktop\ai\dns`

## Architecture

```
main.py
vpn_speed_selector/
  app.py
  core/
    scraper.py          — Fetch .ovpn list from ipspeed.info, download all configs
    pinger.py           — Async ICMP/TCP ping tester for all server IPs
    ranker.py           — Score servers: latency (60%) + uptime (25%) + site_ping (15%)
    connector.py        — Manage OpenVPN subprocess (connect/disconnect/reconnect)
    scheduler.py        — Periodic re-ping + auto-switch to better server
    config_store.py     — QSettings persistence for preferences
  ui/
    main_window.py      — MainWindow: server table, connect button, status bar
    server_table.py     — QTableView + custom model for ranked servers
    status_widget.py    — Connection status indicator + current server info
    settings_dialog.py  — Preferences: ping interval, top-N, region filter
    log_widget.py       — QTextEdit for OpenVPN stdout/stderr
  utils/
    ovpn_parser.py      — Parse .ovpn files: extract remote IP, port, proto
    network.py          — get_default_gateway(), get_adapter_name()
    process.py          — Subprocess wrapper with stdout/stderr capture
```

## Commands
- `pip install -r requirements.txt`
- `python main.py` — run app
- `python -m py_compile <file>` — syntax check (mandatory after every edit)

## Key Requirements

### Core Loop
1. Scrape ipspeed.info/free-openvpn.php -> list of {country, ip, ovpn_url, uptime, site_ping}
2. Download all .ovpn files to AppData/vpn-speed-selector/configs/
3. Parse each .ovpn -> extract remote IP, port, protocol (UDP/TCP)
4. Ping each server IP (ICMP fallback to TCP 443/1194) — async, concurrent
5. Rank using weights from `data/ranking.json` (defaults: actual_ping_ms 60%, uptime_days 25%, site_ping 15%)
6. Display top N (from `data/columns.json`) in table, highlight top 5
7. Connect to #1 via openvpn --config subprocess
8. Monitor: re-ping on interval from `data/scheduler.json`, auto-switch if better server found

### OpenVPN Integration
- Requires OpenVPN installed — path auto-detected or set in settings (default: C:\Program Files\OpenVPN\bin\openvpn.exe)
- Must run app as Administrator for TAP adapter
- Connect: openvpn --config file.ovpn
- Disconnect: terminate subprocess
- Reconnect: disconnect old -> wait 2s -> connect new
- Most ipspeed.info configs embed credentials in .ovpn (auth-user-pass lines)

### UI Layout
```
+----------------------------------------------------------+
| VPN Speed Selector                     [_] [X]           |
+----------------------------------------------------------+
| [Region: All v] [Refresh] [Connect Best] [Disconnect]    |
+----------------------------------------------------------+
| # | Country | IP | Ping ms | Uptime | Score | Status     |
|---|---------|-----|---------|--------|-------|-----------|
| 1 | Japan   | 12..| 4 ms    | 6d     | 98.2  | Connected |
| 2 | Korea   | 21..| 22 ms   | 9d     | 89.1  |           |
+----------------------------------------------------------+
| Status: Connected to 124.32.30.64 (Japan) 4ms            |
| Next ping check: 12:34                                   |
+----------------------------------------------------------+
| OpenVPN Log:                                              |
| > TLS: Initial packet ...                                |
+----------------------------------------------------------+
```

### Scheduler
All values loaded from `data/scheduler.json`:
- Default: re-ping every 30 minutes
- Auto-switch threshold: new server must be >=20% better latency
- Max auto-switches per hour: 3 (prevent flapping)
- Manual connect overrides auto-switch until next cycle

### Connection State Machine
```
DISCONNECTED -> CONNECTING -> CONNECTED -> DISCONNECTING -> DISCONNECTED
                    |                              ^
                 FAILED -------------------------->|
```
- CONNECTING: subprocess started, waiting for "Initialization Sequence Completed"
- CONNECTED: tunnel active
- DISCONNECTING: SIGTERM sent, waiting for process exit
- FAILED: subprocess exited with error or timeout (30s)

### Admin Elevation
- Check for admin on startup
- If not admin: show warning + offer relaunch as admin (runas)
- Non-admin mode: ping/rank only, no connect

### Region Filtering
User can filter by region/country. Default: show all.
Preferred regions loaded from `data/regions.json` (defaults: Japan, Korea, Germany, Russia).

## Critical Rules

### NO Emojis
Use plain text: [OK], [ERR], [SCAN], etc.

### NO Hardcoded Colors or Theme Values
ThemeManager loads all colors, fonts, margins from JSON theme files.
Zero color/size constants in Python code. Every visual property comes from theme JSON.
```python
# WRONG
self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")
# CORRECT
bg = self.theme.get("window", "background")
fg = self.theme.get("window", "foreground")
self.setStyleSheet(f"background-color: {bg}; color: {fg};")
```

### NO Configurable Data in Code — Externalize to JSON
Anything that can change without logic changes belongs in JSON, not Python.
This prevents god files and makes the app skinnable/translatable without touching code.
Externalize ALL of these to JSON:
- **Themes** — colors, fonts, sizes, margins, border-radius → `themes/<name>.json`
- **Region presets** — country lists, preferred regions → `data/regions.json`
- **Ranking weights** — ping/uptime/site_ping percentages → `data/ranking.json`
- **Scheduler config** — intervals, thresholds, max-switches → `data/scheduler.json`
- **OpenVPN known errors** — exit code -> message mapping → `data/ovpn_errors.json`
- **Column definitions** — table columns, widths, sort order → `data/columns.json`
- **Scraping selectors** — CSS selectors for ipspeed.info → `data/scrapers.json`

Theme JSON structure example:
```json
{
  "name": "catppuccin-mocha",
  "window": {
    "background": "#1e1e2e",
    "foreground": "#cdd6f4",
    "border": "#45475a"
  },
  "table": {
    "row_even": "#1e1e2e",
    "row_odd": "#181825",
    "selected": "#45475a",
    "header_bg": "#313244",
    "header_fg": "#cdd6f4",
    "top5_indicator": "#a6e3a1"
  },
  "status": {
    "connected": "#a6e3a1",
    "disconnected": "#f38ba8",
    "connecting": "#f9e2af",
    "failed": "#fab387"
  },
  "font": {
    "family": "Segoe UI",
    "size_base": 10,
    "size_header": 12,
    "size_title": 14
  },
  "margins": {
    "inner": 8,
    "outer": 12,
    "widget_gap": 6
  }
}
```

Each JSON file is loaded once by its corresponding service/manager.
ThemeManager provides `get(group, key)` with fallback to system palette if key missing.
User can switch themes at runtime via settings — ThemeManager re-applies to all widgets via signal.

### NO Lambda in Qt Signal Connections
```python
# WRONG
button.clicked.connect(lambda: self._connect(idx))
# CORRECT
button.clicked.connect(self._on_connect_clicked)
```

### NO Redundant Lambda
```python
# WRONG — wraps existing method for no reason
btn.clicked.connect(lambda: self.do_work())
# CORRECT
btn.clicked.connect(self.do_work)
```

### NO Blocking Sleep or Sync I/O Anywhere
Never use `time.sleep()` or `requests.get()` in any thread that must stay responsive.
- **Main thread**: use QThread workers for all I/O so UI stays responsive.
- **Async code**: use `aiohttp`/`httpx` for network, `asyncio.sleep()` for pauses. If a sync library is unavoidable: `await asyncio.to_thread(sync_call)`.

### NO Mutable Default Args
```python
# WRONG
def f(x=[])
# CORRECT
def f(x=None):
    if x is None:
        x = []
```

### NO Direct UI Updates from Background Threads
Qt widgets are NOT thread-safe. Never call `self.label.setText()` from a QThread.
Use pyqtSignal to emit data from worker, update UI in main thread via slot.

### NO God Object
MainWindow must NOT contain business logic, network calls, or DB queries.
MainWindow only renders data and catches clicks. All logic goes to core/ services.

### NO Synchronous Blocks in Async Code
(Already covered by "NO Blocking Sleep or Sync I/O Anywhere" above — applies specifically to `async def`.)

### NO Fire-and-Forget Coroutines
```python
# WRONG — coroutine created but never awaited or scheduled
async def main():
    my_async_func()
# CORRECT
async def main():
    await my_async_func()
# OR for fire-and-forget with actual execution:
    asyncio.create_task(my_async_func())
```

### NO Unbounded Concurrency
Never launch thousands of async tasks at once (DDoS yourself).
Always use `asyncio.Semaphore(limit)` to cap concurrent operations.
```python
sem = asyncio.Semaphore(50)
async def limited_fetch(url):
    async with sem:
        return await fetch(url)
```

### NO List for Membership Testing
```python
# WRONG — O(N) lookup
if host in allowed_hosts_list:
# CORRECT — O(1) lookup
if host in allowed_hosts_set:
```

### NO String Concatenation in Loops
```python
# WRONG — O(N^2)
result = ""
for line in lines:
    result += line + "\n"
# CORRECT
result = "\n".join(lines)
```

### NO Bare Except or Silent Catch
```python
# WRONG — swallows KeyboardInterrupt, SystemExit, hides bugs
except:
    pass
except Exception:
    pass
# CORRECT — catch specific exceptions AND log them
except (OSError, ConnectionError) as e:
    logger.exception(e)
```
Every try/except must either re-raise, handle meaningfully, or log the error.
Silent `pass` in except block is forbidden.

### NO Iterating Keys Then Lookup
```python
# WRONG — double hash lookup
for key in my_dict:
    value = my_dict[key]
# CORRECT
for key, value in my_dict.items():
    pass
```

### NO Hardcoded File Paths
Use `pathlib.Path` and `QStandardPaths.writableLocation()` for AppData/config dirs.
```python
# WRONG
config_dir = "C:\\Users\\user\\AppData\\Roaming\\vpn-speed-selector"
# CORRECT
config_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)) / "vpn-speed-selector"
```

### NO Storing Secrets in Plaintext
OpenVPN credentials, API keys — never in source code or plaintext JSON.
Use QSettings with encrypted backend or keyring library.

### NO Ignoring Subprocess Exit Code
After OpenVPN subprocess terminates, always check return code.
Log non-zero exits. Map known codes to user-friendly messages via `data/ovpn_errors.json`.

### NO Infinite Retry Loops Without Backoff
Network retries must use exponential backoff with jitter.
Max retry count must be capped. Log each retry attempt.

### NO QThread Subclassing — Use Worker + moveToThread
```python
# WRONG — overriding QThread.run() is legacy and error-prone
class MyThread(QThread):
    def run(self):
        do_work()

# CORRECT — worker object moved to thread, communicate via signals
class Worker(QObject):
    finished = pyqtSignal()
    def do_work(self):
        ...
        self.finished.emit()

thread = QThread()
worker = Worker()
worker.moveToThread(thread)
thread.started.connect(worker.do_work)
worker.finished.connect(thread.quit)
```

### NO Orphaned Threads or Subprocesses on Exit
App must clean up on close:
- Terminate OpenVPN subprocess (even on crash)
- Stop all QThread workers gracefully (quit + wait)
- Cancel pending asyncio tasks
Use `QApplication.aboutToQuit` signal for cleanup.

### NO Concurrent Connect Attempts
Only one OpenVPN subprocess may run at a time.
Attempting connect while already connecting/connected must be rejected.
Connector must enforce single-instance via state machine lock.

### NO Ping During Active VPN Connection
Pinging servers while VPN tunnel is active gives false results
(packets go through tunnel, not direct). Pinger must check connection
state before running. If connected, disconnect first or skip.

### NO Unbounded Log Widget
QTextEdit grows forever if lines are never trimmed.
Cap at N lines (from theme JSON or config), remove oldest when exceeded.
Use `QTextEdit.blockCount` or manual trim on every append.

### NO Circular Imports Between core/ and ui/
Services in core/ must never import from ui/.
Data flows: core emits signals → ui receives and renders.
If ui needs to call core, use method calls (ui depends on core, never reverse).

### NO Shared Mutable State Without Synchronization
If multiple threads access the same data (e.g., server list, connection state):
- Use QMutex / threading.Lock for plain Python objects
- Use pyqtSignal for cross-thread notification
- Never assume atomic reads of compound state (ping + uptime + score)

### NO Widget Parent Leaks
Every widget without a layout parent must receive an explicit parent.
Orphaned widgets leak memory and may crash on theme switch.
```python
# WRONG
dialog = SettingsDialog()
# CORRECT
dialog = SettingsDialog(parent=self)
```

### NO Partial or Corrupt .ovpn Downloads
Download can be interrupted. Verify integrity:
- Check file exists and size > 0
- Parse must succeed (has at least one `remote` line)
- Delete and re-download on failure, never keep corrupt files

### NO Caching Without TTL
Ping results go stale. Cache entries must have TTL (default 15 min).
Expired entries are discarded and re-pinged.
Store timestamp with every cached result.

### NO Ignoring Network Interface Changes
Wi-Fi reconnect or Ethernet plug/unplug invalidates current connection.
Monitor `QNetworkConfigurationManager` or poll adapter state.
On interface change: if connected, transition to DISCONNECTED + alert user.

### Syntax Check After Every Edit
`python -m py_compile <file>` — mandatory.

### No Comments Unless Asked
