# Framework in action: cloning a MIFARE badge

This page walks one real attack through the whole PHLIPPED loop, from the threat
to the fix, so you can see what the framework does without reading any of the
other pages first. The attack is badge cloning, because almost every office has
a badge and most of them are clonable in under a minute.

## 1. The threat

Many access badges are MIFARE Classic cards. That chip uses a cipher
(Crypto1) that has been publicly broken since 2008. An attacker holding a
50-euro Flipper Zero near a reader during a normal badge tap can capture one
exchange, recover the card's key in seconds, and copy the badge onto a blank.
The copy opens the door exactly like the original.

Full detail, hardware, and the attack chain: [PHL-T-003](threats/PHL-T-003.html).

## 2. What it leaves behind

A clone is not invisible. It produces signals an organisation can watch for:

- The same badge ID appearing at two readers that are too far apart to reach in
  the time between taps. A card cannot be in two places at once.
- A burst of failed reads of one badge ID, then moments later a successful entry
  with that same ID: key recovery, then the clone walking in.

These are the *observable indicators* in the catalog entry. The framework's job
is to turn them into something that actually fires an alert.

## 3. The detection

PHLIPPED defines a detection rule for exactly this behaviour:
[`PHL-D-003`](https://github.com/phlipped-fw/phlipped/blob/main/data/detections/PHL-D-003.yml).
Run against the access-control system's event log, it is written to raise a
high-severity alert when the same badge ID appears at incompatible readers, or
on the failed-reads-then-entry pattern above. Every detection rule carries the
id of the threat it defends against, so an analyst seeing the alert can read the
full context in one click. The rule is authored, not yet validated against live
telemetry: a lab that fires it against sample logs is on the roadmap.

## 4. The fix

Detection buys time; it does not close the hole. The lasting fix is to migrate
off MIFARE Classic to a modern card (DESFire EV3 or Seos) that uses real mutual
authentication, so a captured exchange reveals nothing. Until then, the response
procedure is to revoke any badge ID the rule flags and physically check who used
it last.

## Why this matters as a framework

On its own, "MIFARE is broken" is a trivia fact. The value PHLIPPED adds is the
loop: a catalogued threat, the signals it produces, a detection that fires on
those signals, and a prioritised fix, all cross-referenced. The
[assessment tool](about.html) runs this logic across every threat in the catalog
and gives an organisation a single posture score plus its worst gaps, ranked.
This page is that loop shown for one threat; the framework is the same loop for
all of them.
