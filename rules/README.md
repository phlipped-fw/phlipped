# rules

Detection rules for the PHLIPPED framework. Reference implementation in **Wazuh** (XML); portable copy in **Sigma** YAML.

Each rule ID is `PHL-D-NNN` and maps 1:1 to one or more threats `PHL-T-NNN` in [`data/techniques`](../data/techniques). The portable Sigma form of each rule is the `logic`
field of its detection object in [`data/detections`](../data/detections).

## Layout

```
wazuh/phlipped_rules.xml   # Wazuh rules, validated by ../lab/validate.py
```

The file name matters: Wazuh loads every rule file in one name-sorted list, so it must sort
after the stock `0xxx` ruleset or its `if_sid` parents do not exist yet.

## License

MIT.
