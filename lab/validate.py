"""Replay lab/samples/*.jsonl through a real Wazuh manager and check each event raises the expected rule.

Each sample line is {"expect": "<rule id>" | null, "event": {...}}. null means no PHLIPPED rule
(id 1002xx) may alert. Events go into analysisd's own queue socket, the path agent events take,
then alerts.json is read back. Windows events use the agent wire format (event XML wrapped in
JSON) because wazuh-logtest cannot exercise the EventChannel decoder. Correlation state is
shared across all samples, so scenarios use distinct card UIDs. Needs Docker; starts and removes
a throwaway manager container.

    python lab/validate.py
"""
import json
import subprocess
import sys
import time
from pathlib import Path

IMAGE = "wazuh/wazuh-manager:4.9.0"
NAME = "phlipped-validate"
LAB = Path(__file__).resolve().parent
RULES = LAB.parent / "rules" / "wazuh"
PY = "/var/ossec/framework/python/bin/python3"

# runs inside the container: one json event per stdin line, prints the rule ids it alerted on
CLIENT = r"""
import json, socket, sys, time
ALERTS = "/var/ossec/logs/alerts/alerts.json"
s = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
s.connect("/var/ossec/queue/sockets/queue")
seen = sum(1 for _ in open(ALERTS))
for line in sys.stdin:
    ev = json.loads(line)
    # 'f' is the eventchannel queue, '1' the plain logfile queue
    head = "f:EventChannel:" if "Event" in ev else "1:phlipped-lab:"
    s.send((head + json.dumps(ev)).encode())
    time.sleep(float(sys.argv[1]))
    lines = [l for l in open(ALERTS).readlines() if l.endswith("\n")]  # skip a half-written line
    print(json.dumps([json.loads(l)["rule"]["id"] for l in lines[seen:]]), flush=True)
    seen = len(lines)
"""


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def start():
    sh("docker", "rm", "-f", NAME)
    r = sh("docker", "run", "-d", "--name", NAME,
           "-v", f"{RULES}:/wazuh-config-mount/etc/rules:ro", IMAGE)
    if r.returncode:
        sys.exit(f"docker run failed: {r.stderr.strip()}")
    for _ in range(90):
        if sh("docker", "exec", NAME, "test", "-S", "/var/ossec/queue/sockets/queue").returncode == 0 \
                and sh("docker", "exec", NAME, "test", "-f", "/var/ossec/logs/alerts/alerts.json").returncode == 0:
            break
        time.sleep(2)
    else:
        sys.exit("wazuh manager did not start")
    time.sleep(10)  # analysisd opens the queue before it has finished loading rules
    log = sh("docker", "exec", NAME, "cat", "/var/ossec/logs/ossec.log").stdout
    bad = [l for l in log.splitlines() if "analysisd" in l and ("ERROR" in l or "CRITICAL" in l or "WARNING" in l)]
    if bad:
        sys.exit("rules did not load cleanly:\n" + "\n".join(bad))


def alerted(lines, wait=1.0):
    """Rule ids each input line alerted on, in order."""
    r = sh("docker", "exec", "-i", NAME, PY, "-c", CLIENT, str(wait), input="\n".join(lines) + "\n")
    res = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    if r.returncode or len(res) != len(lines):
        sys.exit(f"queue client failed:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    return res


def main():
    start()
    failed = 0
    try:
        for f in sorted((LAB / "samples").glob("*.jsonl")):
            rows = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
            for n, (row, ids) in enumerate(zip(rows, alerted([json.dumps(r["event"]) for r in rows])), 1):
                want, ours = row["expect"], [i for i in ids if i.startswith("1002")]
                ok = ours == [want] if want else not ours
                failed += not ok
                print(f"{'ok  ' if ok else 'FAIL'} {f.name}:{n} expect {want or 'no phlipped alert'}, got {ours or None}")
    finally:
        sh("docker", "rm", "-f", NAME)
    print(f"\n{failed} failed" if failed else "\nall samples matched")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
