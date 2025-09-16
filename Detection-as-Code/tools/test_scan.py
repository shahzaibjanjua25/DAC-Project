import sys, json, re, pathlib

sample = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("samples/windows_process_creation.json")
print(f"[i] CWD        : {pathlib.Path.cwd()}")
print(f"[i] Sample path: {sample.resolve()}")

if not sample.exists():
    print("[!] Sample NON trovato. Controlla il percorso.")
    sys.exit(2)

text = sample.read_text(encoding="utf-8").strip()
if not text:
    print("[!] Sample vuoto.")
    sys.exit(3)

events = []
if text.lstrip().startswith("["):
    events = json.loads(text)
    print(f"[i] Formato: ARRAY JSON | Eventi: {len(events)}")
else:
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except Exception as e:
            print(f"[!] Riga {n} non valida: {e}")
    print(f"[i] Formato: NDJSON | Eventi: {len(events)}")

pat_b64 = re.compile(r"(?i)[A-Za-z0-9+/]{20,}={0,2}")
hits = 0
for idx, evt in enumerate(events, 1):
    img = (evt.get("Image") or "").lower()
    cmd = (evt.get("CommandLine") or "")
    cond = (
        (img.endswith("\\powershell.exe") or img.endswith("\\pwsh.exe")) and
        ((" -enc " in cmd.lower()) or (" --encodedcommand " in cmd.lower()) or (" -e " in cmd.lower())) and
        (pat_b64.search(cmd) is not None)
    )
    if cond:
        hits += 1
        print(f"[MATCH] evt#{idx}: {cmd}")

print(f"[✓] Totale match: {hits}")
