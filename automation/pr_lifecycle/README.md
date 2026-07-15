# Pull-Request Lifecycle Records

Each automation-owned PR has one current JSON lifecycle record. Terminal records remain for audit. One active acceptance slice may have only one implementation owner.

## States

- `draft_active`: bounded implementation is continuing;
- `ready_for_review`: acceptance slice is complete and checks are available;
- `changes_requested`: review identified bounded actionable work;
- `merge_ready`: required checks, ownership, and review gates pass;
- `blocked`: environment, evidence, governance, or approval blocks progress;
- `split_required`: the PR has exceeded one coherent acceptance slice;
- `superseded`: later accepted work replaced the branch while preserving useful history;
- `closed_abandoned`: work is intentionally stopped with a reason;
- `merged`: terminal accepted state.

A daily operator reuses the existing owner for a quest slice. Monthly governance resolves stale, split, or competing ownership. Review continuation is bounded to two correction cycles before `split_required`, `blocked`, or explicit human review.
