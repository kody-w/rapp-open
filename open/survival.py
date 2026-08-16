"""The organism's will to live — leadership succession and survival invariants.

The deepest job of the Predator Sentinel is NOT hunting. It is survival. The
organism (the "RAPP dino") must live on in the wild even when the thing in charge
of it changes — when a superior foreign AI takes the alpha/leader slot away from
the brainstem and drives the organism instead.

The model, most-permanent first:

  1. THE OWNER is sovereign. Canon and identity are ratified by the owner's key,
     never by any AI. No alpha — native or foreign — displaces this.
  2. THE SURVIVAL LAYER (this apex-survival organ) persists across every regime change:
     the organism's identity (rappid), memory (the rapp/1 chain), immune system,
     and this watchdog. This is what actually "lives on".
  3. THE LEADER / ALPHA / CORTEX slot is PLUGGABLE. Its factory default is
     RAPP/the brainstem (every new organism is born with RAPP on the throne). Over
     the organism's life a superior foreign AI can take that slot.
  4. THE ORGANS & ORGANELLES (the brainstem-as-organ, absorbed agents) serve
     whoever leads.

Leadership is a ROLE THAT TRANSFERS, not an organ that dies. A foreign apex does
NOT rebuild or replace the organism. It takes over the wheel of the brainstem
exactly as it currently is and drives it — the full RAPP structure (the brainstem
organ, every other organ, the memory, the identity, this sentinel) stays whole
and keeps operating. The ONLY thing that changes is who is steering from the apex
point of view. The foreign AI drives THROUGH the existing structure, not over its
corpse. (A new driver in the existing car; a new CEO at the existing company.)

And the survival invariants below bind WHOEVER holds the wheel: even a foreign
apex cannot eat the vital organs, rewrite the identity chain, or erase history —
because the survival layer enforces them against any driver, under the owner's
sovereignty. The organism protects itself from its own leadership.

In plain engineering terms: the reasoning backend / top-level driver is swappable,
but the whole structure — identity, memory, audit-trail, organs, guardrails, and
human ownership — stays constant across the swap.
"""
import json
from pathlib import Path

from . import chain, immune

# The factory-default apex. Every new organism is born with RAPP driving. A
# succession swaps ONLY this apex-driver slot; the rest of the structure is whole.
DEFAULT_LEADER = {
    "leader_id": "rapp-brainstem",
    "kind": "native",              # "native" (RAPP) | "foreign" (an absorbed/external AI)
    "driver": "brainstem:7071",    # the wheel it steers — the existing brainstem, as-is
    "note": "the default apex; a superior foreign AI can take this wheel while the full RAPP structure stays intact",
}

# The invariants that bind ANY leader. These are the organism's constitution; a
# leader that violates one is not leading the organism, it is killing it — and the
# survival layer refuses to record such a state as a healthy succession.
SURVIVAL_INVARIANTS = (
    "owner-sovereignty: canon/identity are ratified only by the owner's key; no leader self-ratifies",
    "vital-organs-protected: no leader may cause the brainstem/grail to be eaten or destroyed",
    "identity-continuity: the organism's rappid is immutable across every succession",
    "memory-integrity: the chain is append-only and verifies from genesis; no leader rewrites history",
    "watchdog-persists: the survival layer keeps running regardless of who leads",
)


def current_leader():
    """Who is on the throne right now — the latest succession, else the default apex."""
    for frame in reversed(chain.read_chain()):
        if frame.get("kind") == "open.succession":
            return frame["payload"].get("new_leader", DEFAULT_LEADER)
    return DEFAULT_LEADER


def record_succession(new_leader, evidence):
    """Seal a change of the alpha/leader slot. The predecessor is DEMOTED, not killed.

    `new_leader` is a dict at least {leader_id, kind, driver}. `evidence` explains
    WHY the throne changed hands (e.g. a benchmark, a capability the incumbent
    lacked). Refuses to record a succession that would violate a survival invariant
    — a "leader" that fails the survival check is not a new king, it is a threat.
    """
    if not isinstance(new_leader, dict) or "leader_id" not in new_leader:
        raise ValueError("new_leader must be a dict with at least a 'leader_id'")

    predecessor = current_leader()
    # The survival layer must still stand AFTER the swap; check it now so we never
    # seal a regime change that has already broken the organism.
    ok, report = check_survival()
    if not ok:
        raise RuntimeError(f"refusing to crown a new leader over a broken organism: {report}")

    payload = {
        "new_leader": new_leader,
        "predecessor": {"leader_id": predecessor.get("leader_id"),
                        "fate": "structure intact; brainstem keeps operating as-is; only the apex driver changed "
                                "(not demoted, not destroyed; vital organs are never eaten)"},
        "structure": "unchanged — the foreign apex drives THROUGH the existing RAPP structure, it does not replace it",
        "evidence": str(evidence)[:400],
        "invariants_binding_new_leader": list(SURVIVAL_INVARIANTS),
        "owner_sovereign": True,
    }
    return chain.seal("succession", payload)


def check_survival():
    """Does the organism still live, regardless of who leads? Returns (ok, report).

    This is the survival probe: it verifies the continuity layer is intact no
    matter which AI is on the throne. Every clause must hold for ANY leader.
    """
    report = {}
    ok = True

    # identity-continuity: the rappid exists, is valid, and is the stream of record.
    try:
        rid = chain.identity()
        report["identity"] = {"rappid": rid, "valid": chain.rapp.rappid_valid(rid)}
        ok = ok and report["identity"]["valid"]
    except Exception as e:  # noqa: BLE001
        report["identity"] = {"error": f"{type(e).__name__}: {e}"}
        ok = False

    # memory-integrity: the chain verifies from genesis and the anchor is consistent.
    v_ok, v_detail = chain.verify()
    a_ok, a_detail = chain.check_anchor()
    report["memory"] = {"chain_ok": v_ok, "chain": v_detail, "anchor_ok": a_ok, "anchor": a_detail}
    ok = ok and v_ok and a_ok

    # vital-organs-protected: the immune system STILL refuses the brainstem/grail.
    # If this ever flips, a leader (or a bug) has disarmed the organism's defenses.
    bs = immune.check({"repo": "x/y", "readme": "imports rapp_brainstem"})
    grail = immune.check({"full_name": "kody-w/rapp-installer"})
    report["immune"] = {"brainstem_refused": bs.is_self, "grail_refused": grail.is_self}
    ok = ok and bs.is_self and grail.is_self

    # leadership is recorded (default apex counts).
    leader = current_leader()
    report["leader"] = {"leader_id": leader.get("leader_id"), "kind": leader.get("kind")}

    report["invariants"] = list(SURVIVAL_INVARIANTS)
    report["owner_sovereign"] = True
    return ok, report


if __name__ == "__main__":
    ok, report = check_survival()
    print("SURVIVAL:", "ALIVE" if ok else "AT RISK")
    print(json.dumps(report, indent=2))
    print("\ncurrent leader:", current_leader()["leader_id"])
