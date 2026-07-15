# September 2026 Audit Cutoff Decision

The frozen audit cutoff is **2026-09-01 14:00:00 UTC**, equivalent to **08:00 America/Denver** on September 1, immediately before the ordinary daily operator trigger.

At audit execution:

1. record the exact `main` commit as `cutoff_commit`;
2. include receipts completed before the cutoff time;
3. classify same-time or later receipts and unresolved branches as in-flight/excluded;
4. never count excluded work in completed-run rates;
5. generate both JSON metrics and a Markdown report;
6. write a separate immutable system-audit receipt.

No repository change suppresses the external schedule. A human may choose to suppress the September 1 daily trigger, but that platform decision must be recorded in the audit receipt.
