# phlipped-rules

Detection rules for the PHLIPPED framework. Reference implementation in **Wazuh** (XML); portable copy in **Sigma** YAML.

Each rule ID is `PHL-D-NNN` and maps 1:1 to one or more threats `PHL-T-NNN` in [`phlipped-catalog`](https://github.com/phlipped-fw/phlipped-catalog).

## Layout

```
wazuh/    # Wazuh local_rules.xml fragments
sigma/    # Sigma YAML per rule
```

## License

MIT.
