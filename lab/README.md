# phlipped-lab

Reproducible lab environment for testing the PHLIPPED framework end-to-end. Brings up Wazuh + supporting services in `docker-compose`, with the [`phlipped-rules`](https://github.com/phlipped-fw/phlipped-rules) repo mounted into the manager.

> **Note:** physical attack rigs (Flipper Zero, BadUSB, drop Pi) are obviously out-of-scope for a container lab. The lab is for *detection* validation: feed it sample logs / live agent telemetry and verify the rules fire as expected.

## Layout

```
docker-compose.yml
wazuh/                # mounts phlipped-rules/wazuh into /var/ossec/etc/rules/local_rules.d/
sysmon/               # Olaf Hartong's modular Sysmon config + PHLIPPED additions
```

## Bring up

```bash
git clone https://github.com/phlipped-fw/phlipped-rules ../phlipped-rules
docker compose up -d
# Wazuh dashboard: https://localhost:5601
```

## License

MIT.
