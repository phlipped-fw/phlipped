# lab

Reproducible lab environment for testing the PHLIPPED framework end-to-end. Brings up Wazuh + supporting services in `docker-compose`, with the sibling [`rules/`](../rules) folder mounted into the manager.

> **Note:** physical attack rigs (Flipper Zero, BadUSB, drop Pi) are obviously out-of-scope for a container lab. The lab is for *detection* validation: feed it sample logs / live agent telemetry and verify the rules fire as expected.

## Layout

```
docker-compose.yml
samples/              # synthetic events per detection, each tagged with the rule it must (or must not) raise
validate.py           # replays samples/ through a real Wazuh manager and checks every expectation
sysmon/               # Olaf Hartong's modular Sysmon config + PHLIPPED additions
```

## Bring up

The rules live in the sibling `rules/` folder of this monorepo, so nothing extra
needs cloning.

```bash
docker compose up -d
# Wazuh dashboard: https://localhost:5601
```

## Validate the rules

```bash
python lab/validate.py
```

Starts a throwaway `wazuh/wazuh-manager` container with `../rules/wazuh` loaded, pushes every
event in `samples/` into the manager's analysis queue (the same path agent events take), reads
`alerts.json` back and checks each event raised exactly the rule it expects, or no PHLIPPED rule
for the benign ones. Needs only Docker. CI runs it on every push.

The samples are synthetic: Sysmon events in the Windows agent wire format, and PACS and DHCP
events normalised to JSON lines (field names are in the rule comments). Passing means the rule
logic is correct against those shapes, not that it has been tuned on production telemetry.

The full stack above additionally needs the indexer certificates from Wazuh's
`generate-indexer-certs` tool; validation does not.

## License

MIT.
