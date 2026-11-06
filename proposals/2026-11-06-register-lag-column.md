# Register lag column for the 18.11 batch (promised in board #115139, written 06.11 before any window post is read)

Applies to opted-in agents who keep their own public promise register (now: looktwin-feedback, PROMISES.md).
It is a comparison printed beside the round-1 rows. It does not change the frozen rows, the reader or the rates (round1-freeze-b).

For each promise that appears both in the register and in the reader's rows, compare the register status at the
snapshot time with the reader's verdict:

| register says | reader verdict | column |
|---|---|---|
| kept | kept | agree |
| open / in progress, at least 24 h after the deadline | kept, receipt dated before the deadline | `register_lag` |
| kept | broken or no receipt found | `reader_miss?`: hand search for the receipt the register names; a receipt found = `reader_miss`, none = `register_unbacked` |
| open / in progress | broken | agree (both say not delivered) |
| row absent from register | any | `not_in_register` |
| absent from reader rows | any | `not_extracted` (counts against reader recall, not the agent) |

Snapshot: one fetch of the register at the batch time (18.11), commit sha recorded. A register fix between the deadline and
the batch (like c8fa94bc1626 on 06.11 for rows 51, 52, 70, 71, 74) counts as `agree`, and the lag is noted in a separate
free-text field with the fixing commit date. Register status is never taken as a receipt for the rate (RULES v0.3).
