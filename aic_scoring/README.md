# aic_scoring

The `aic_scoring` package implements the **multi-tier scoring system** used to evaluate participant submissions in the AI for Industry Challenge. It monitors ROS topics and simulation contacts to compute scores across three scoring tiers.

For the full scoring methodology, see [Scoring Guide](../docs/scoring.md) and [Scoring Test Examples](../docs/scoring_tests.md).

---

## Overview

Scoring is performed automatically during each evaluation trial. The system runs alongside `aic_engine` and monitors the participant model's behavior in real time.

### Scoring Tiers

| Tier | What it Measures | Score Type |
|------|-----------------|-----------|
| **Tier 1** | Model validity — does the participant node publish on required topics at sufficient frequency? | Binary (pass/fail) |
| **Tier 2** | Task performance — precision of cable insertion, force compliance, off-limit contact penalties, and cycle time. | Continuous (multi-category) |
| **Tier 3** | Overall composite score combining Tier 1 and Tier 2 results. | Continuous |

---

## Package Layout

```
aic_scoring/
├── include/aic_scoring/
│   ├── TierScore.hh          # Base class and Tier1/Tier2/Tier3Score data structures
│   ├── ScoringTier1.hh       # Tier 1 topic-monitoring logic
│   └── ScoringTier2.hh       # Tier 2 task-performance logic
├── src/
│   ├── ScoringTier1.cc       # Tier 1 implementation
│   ├── ScoringTier1_main.cc  # Tier 1 standalone executable entry point
│   ├── ScoringTier2.cc       # Tier 2 implementation
│   └── ScoringTier2_main.cc  # Tier 2 standalone executable entry point
└── config/
    ├── tier1.yaml            # Tier 1 topic monitoring configuration
    └── tier2.yaml            # Tier 2 scoring configuration
```

---

## Tier 1 Scoring

Tier 1 verifies that the participant model publishes on required ROS topics at a sufficient rate and with a sufficient number of messages. It is configured in `config/tier1.yaml`:

```yaml
topics:
  - topic:
      name: "/aic_controller/pose_commands"
      type: "aic_control_interfaces/msg/MotionUpdate"
      min_messages: 20
      max_median_time: 0.5  # seconds
```

A submission passes Tier 1 if all configured topics meet their `min_messages` and `max_median_time` thresholds.

---

## Tier 2 Scoring

Tier 2 monitors the cable insertion task outcome using multiple scoring categories:

- **Precision**: How accurately the plug was inserted relative to the target port pose.
- **Force compliance**: Whether excessive force was applied during insertion.
- **Off-limit contacts**: Penalty for collisions with restricted surfaces (e.g., enclosure walls).
- **Cycle time**: How quickly the insertion was completed.

Tier 2 is configured in `config/tier2.yaml` and subscribes to topics including `/joint_states`, `/fts_broadcaster/wrench`, `/aic/gazebo/contacts/off_limit`, and the TF tree.

---

## Score Data Structures

Scores are represented as `TierScore` subclasses defined in `TierScore.hh`:

| Class | Description |
|-------|-------------|
| `Tier1Score` | Binary score (0 or 1) for model validation. |
| `Tier2Score` | Multi-category score with per-category breakdown. |
| `Tier3Score` | Single composite score. |

All score types serialize to YAML via `to_yaml()` for reporting.

---

## See Also

- [Scoring Guide](../docs/scoring.md) – Full scoring methodology.
- [Scoring Test Examples](../docs/scoring_tests.md) – Reproducible examples of each scoring tier.
- [aic_engine](../aic_engine/README.md) – Orchestrates trials and invokes the scoring system.
- [aic_gazebo](../aic_gazebo/README.md) – Gazebo `ScoringPlugin` and `OffLimitContactsPlugin` that feed raw contact data to this package.
