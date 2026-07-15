# Rituals

Executable loop behavior lives in `automation/contracts/`. This file is human orientation only.

1. Select the contract matching the trigger.
2. Capture source and state snapshots.
3. Execute one bounded artifact-bearing slice within ownership.
4. Verify and recheck concurrency before publication.
5. Write one immutable receipt with a terminal state and next action.
6. Generate human-readable views from records when needed.

Do not maintain a second copy of queue governance, retry rules, or mutation permissions here.
