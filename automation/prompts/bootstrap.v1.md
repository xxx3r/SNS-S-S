# SNS scheduler bootloader

Generate the scheduler text with `automation.orchestration.render_bootstrap_prompt(loop_id)`.
It names the repository, loop ID, connected tools and AGENTS.md entrypoint. The active contract, standing scope, validator rules, queue, budgets and current next move stay in the repository.

## Freshness invariant

Each run establishes the repository's current default-branch `main` head through a new GitHub observation before interpreting repository state. Previous-run SHA, contract, queue and next-action values are historical context until corroborated against that freshly observed head. Prior scheduled-run context is history, never current repository authority.

Bind `AGENTS.md`, the active loop contract and decision state to the newly observed `CURRENT_MAIN_SHA`. Before publication or merge, observe default-branch HEAD again and refresh decision state if it moved. If current default-branch state cannot be observed, terminate with an explicit source-observation blocker rather than substituting a prior SHA.

The `weekly-evidence-synthesis` ID is stable historical identity; its current role is Weekly Research Delivery. Observatory has a separate projection route. Tool mentions express intended use; connector availability must be observed, and optional Wolfram availability is never a provenance prerequisite.

The scheduler API exposes prompt, title, timing and enabled state. It does not expose a tool-attachment field here. Preserve existing connected task contexts, verify configuration readback, and distinguish that from a successful scheduled run.
