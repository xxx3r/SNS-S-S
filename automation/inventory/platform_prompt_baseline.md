# Platform Prompt Baseline and Compatibility

The schedule remains platform-managed. Repository behavior is now versioned in `automation/contracts/`.

## Baseline prompt classes

Before Issue #24, scheduled prompts independently described daily artifact execution, Sunday evidence synthesis, first-Sunday governance, and the September system audit. Those procedures overlapped with `AGENTS.md`, `AURORA.md`, rituals, memory instructions, and calendar templates.

## Active bootstrap form

Use a thin prompt for each scheduled trigger:

```text
Execute the active repository contract `<loop-id>@1.0.0` for
`xxx3r/SNS-S-S`. Record contract version, trigger time, source commit,
state hash, consumed IDs, verification, terminal state, and next action in
one immutable run receipt. Platform safety and explicit human instruction
remain higher authority.
```

The platform prompt may also state notification behavior and temporary observation constraints. It must not duplicate queue governance, receipt schemas, retry rules, or terminal-state definitions.

## Dual-write compatibility

During the transition, loops may update an already-required human summary only when their contract authorizes it. Every new scheduled run must write its immutable receipt. Mandatory appends to `memory/mem_log_long_0000_0999.md` are retired immediately after this implementation merges.

## Activation

A contract is active only when merged to `main`, parse-valid, supported by receipt tooling and semantic validation, and referenced by its scheduled prompt. Retired contracts remain in Git and may be used only in explicit replay mode.
