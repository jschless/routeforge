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

from typing import Literal, TypeAlias

WredAction: TypeAlias = Literal["FORWARD", "MARK", "DROP"]


def apply_policer(*, offered_kbps: int, cir_kbps: int) -> int:
    """Police offered rate to CIR with zero-floor normalization."""
    normalized_offered = max(offered_kbps, 0)
    normalized_cir = max(cir_kbps, 0)
    return min(normalized_offered, normalized_cir)


def qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]:
    """Return admitted (policer) and released (shaper) rates."""
    admitted = apply_policer(offered_kbps=offered_kbps, cir_kbps=cir_kbps)
    released = min(admitted, max(shape_rate_kbps, 0))
    return admitted, released


def wred_decision_profile(
    *,
    queue_depth: int,
    min_threshold: int,
    max_threshold: int,
) -> Literal["BELOW_MIN", "BETWEEN_THRESHOLDS", "AT_OR_ABOVE_MAX"]:
    """Classify queue depth against WRED thresholds."""
    if queue_depth < min_threshold:
        return "BELOW_MIN"
    if queue_depth < max_threshold:
        return "BETWEEN_THRESHOLDS"
    return "AT_OR_ABOVE_MAX"


def qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> WredAction:
    """Return FORWARD/MARK/DROP based on profile and ECN capability."""
    profile = wred_decision_profile(
        queue_depth=queue_depth,
        min_threshold=min_threshold,
        max_threshold=max_threshold,
    )
    if profile == "BELOW_MIN":
        return "FORWARD"
    if profile == "BETWEEN_THRESHOLDS":
        return "MARK" if ecn_capable else "DROP"
    return "DROP"
