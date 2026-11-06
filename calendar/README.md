# SNS Research Calendar

The calendar preserves two distinct claim-specific evidence lanes: Weekly's **external literature confidence** and the trio's **internal experimental confidence**. See `docs/research/SNS_RESEARCH_WHEEL_V3.md` for the June eight paths and [Formula]→[Mechanism]→[Implementation].

## Weekly loop

Every Sunday, create `calendar/roundups/YYYY-MM-DD.md` from the template. It must contain:

1. weighted belief shifts
2. suggested actions
3. an SNS awareness update

Front matter uses JSON syntax, which is valid YAML 1.2 and can be parsed without an additional dependency.

## Monthly loop

At month end, create one roundup-of-roundups that:

- consolidates repeated signals
- distinguishes temporary news from durable trajectory
- updates subsystem plausibility
- closes, merges, or reprioritizes quests
- records changes to the long-range architecture

## Evidence discipline

A belief shift should state:

- subsystem
- direction or delta
- confidence
- rationale
- source trail
- model or quest consequence

A paper does not automatically become a positive belief shift. Relevance, environment, scale, and evidence quality matter.

## External versus internal confidence

External confidence arrows ⬆️/⬇️/↔️ cite recent primary sources, environments and cross-domain transfer limits; internal arrows cite our exact-source accepted models, physical tests, uncertainty and falsifiers. UNKNOWN is valid for either. Never add an invented joint score or infer physical hardware readiness from a synthetic measurement. Weekly proposes scientific connections; the internal wheel tests them; Monthly consolidates strategic beliefs.
