# Immutable Run Receipts

Store one schema-valid JSON receipt at `YYYY/MM/<run-id>.json` for every scheduled or explicit-human loop trigger. Writers use exclusive-create semantics. Never edit or renumber an existing receipt.
