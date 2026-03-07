"""Advanced QoS mechanisms: traffic policing, shaping, and WRED.

QoS (Quality of Service) gives the network the ability to prioritize some
traffic over others and protect against congestion.  This module covers:

- **Policing** — hard-drops or re-marks traffic that exceeds a Committed
  Information Rate (CIR).  Excess traffic is discarded immediately.
- **Shaping** — buffers excess traffic and releases it at the configured
  shape rate instead of dropping, smoothing bursts at the cost of added delay.
- **WRED (Weighted Random Early Detection)** — probabilistically drops packets
  *before* a queue fills completely, providing early congestion signals to
  TCP flows.  ECN-capable flows receive a mark instead of a drop when between
  min and max thresholds.
"""

from __future__ import annotations

from typing import Literal


def apply_policer(*, offered_kbps: int, cir_kbps: int) -> int:
    """Police offered traffic rate to CIR with deterministic zero-floor normalization.

    Returns ``max(0, min(offered_kbps, cir_kbps))``.  Both negative inputs floor
    to ``0`` — a negative offered rate or negative CIR both yield ``0``.

    # TODO(student): implement apply_policer.
    """
    raise NotImplementedError("TODO: implement apply_policer")


def wred_decision_profile(
    *,
    queue_depth: int,
    min_threshold: int,
    max_threshold: int,
) -> Literal["BELOW_MIN", "BETWEEN_THRESHOLDS", "AT_OR_ABOVE_MAX"]:
    """Classify queue depth into a deterministic WRED threshold profile bucket.

    - ``queue_depth < min_threshold`` → ``"BELOW_MIN"``
    - ``min_threshold <= queue_depth < max_threshold`` → ``"BETWEEN_THRESHOLDS"``
    - ``queue_depth >= max_threshold`` → ``"AT_OR_ABOVE_MAX"``

    # TODO(student): implement wred_decision_profile.
    """
    raise NotImplementedError("TODO: implement wred_decision_profile")


def qos_police_shape(
    *, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int
) -> tuple[int, int]:
    """Model deterministic policing and shaping rates.

    Returns ``(admitted_kbps, released_kbps)``:

    - ``admitted_kbps = min(offered_kbps, cir_kbps)``  — policing hard-caps
      traffic at the CIR; anything above is dropped.
    - ``released_kbps = min(admitted_kbps, shape_rate_kbps)``  — shaping
      limits the burst release rate after policing.

    See ``docs/tutorial/lab30_qos_policing_and_shaping.md`` for the walkthrough.

    # TODO(student): implement qos_police_shape.
    """
    raise NotImplementedError("TODO: implement qos_police_shape")


def qos_wred_decision(
    *,
    queue_depth: int,
    min_threshold: int,
    max_threshold: int,
    ecn_capable: bool,
) -> str:
    """Apply WRED/ECN decision logic based on queue fill thresholds.

    Decision (apply in order):

    1. ``queue_depth < min_threshold`` → ``"FORWARD"`` (queue not congested).
    2. ``queue_depth >= max_threshold`` → ``"DROP"`` (queue full; drop always,
       even for ECN-capable flows).
    3. ``min_threshold <= queue_depth < max_threshold``:
       - ``ecn_capable=True`` → ``"MARK"`` (set ECN CE bits instead of dropping).
       - ``ecn_capable=False`` → ``"DROP"`` (random early drop).

    See ``docs/tutorial/lab31_qos_congestion_avoidance_wred.md``.

    # TODO(student): implement qos_wred_decision using the thresholds above.
    """
    raise NotImplementedError("TODO: implement qos_wred_decision")
