# lab

Reproducible lab environment for testing the PHLIPPED framework end-to-end. Brings up Wazuh + supporting services in `docker-compose`, with the sibling [`rules/`](../rules) folder mounted into the manager.

> **Note:** physical attack rigs (Flipper Zero, BadUSB, drop Pi) are obviously out-of-scope for a container lab. The lab is for *detection* validation: feed it sample logs / live agent telemetry and verify the rules fire as expected.

## Layout

```
docker-compose.yml
wazuh/                # mounts ../rules/wazuh into /var/ossec/etc/rules/local_rules.d/
sysmon/               # Olaf Hartong's modular Sysmon config + PHLIPPED additions
```

## Bring up

The rules live in the sibling `rules/` folder of this monorepo, so nothing extra
needs cloning.

```bash
docker compose up -d
# Wazuh dashboard: https://localhost:5601
```

## License

MIT.
