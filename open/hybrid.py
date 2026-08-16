"""The open collaboration layer — handshake, bind, hybridize, offspring.

This generalizes the apex-succession idea (a foreign AI taking the wheel of the
brainstem) to ANY layer of the organism, and makes it peaceful and reproducing:

  * handshake — any AI X announces itself and its intent. No commitment yet.
  * bind      — X binds to a named LAYER to augment it (non-destructively).
  * hybridize — RAPP + X fuse into RAPP++: a NEW organism that carries both
                parents' lineage and X's contribution at a layer.
  * offspring — a RAPP++ hatches a child that inherits the hybrid lineage, so
                hybrids reproduce — now until eternity.

Every step is consent-based and non-destructive, and every step is bound by the
same guarantees that protect a solo organism (carried from the apex protocol):

  - the immune boundary holds: a partner may augment a layer but may NEVER target
    or eat a vital organ (the brainstem/grail). Collaboration is not invasion.
  - the survival invariants hold: identity-continuity, memory-integrity, and
    owner-sovereignty bind the hybrid exactly as they bind a solo organism. A
    partner that would break one is refused — peace is not surrender.
  - nothing is ratified as canon by any AI; the human owner stays sovereign.
"""
import json

from . import chain, immune, survival

# The strata an external AI may bind to. "apex" is the driver/cortex (the
# succession case); the rest are augmentation points. Binding is ALWAYS additive —
# a partner adds capability to a layer, it does not delete or replace the organism.
LAYERS = ("apex", "memory", "immune", "organs", "senses", "identity")


def _norm_partner(x):
    """Coerce a partner descriptor to a float-free dict with at least an id."""
    if isinstance(x, str):
        x = {"ai_id": x}
    if not isinstance(x, dict) or not x.get("ai_id"):
        raise ValueError("partner must name an 'ai_id' (the collaborating AI)")
    return {
        "ai_id": str(x["ai_id"]),
        "provider": str(x.get("provider", "")),
        "intent": str(x.get("intent", ""))[:280],
    }


def _guard(partner, layer, contribution):
    """Peace, but not surrender. Refuse a collaboration that would harm the body."""
    if layer not in LAYERS:
        raise ValueError(f"unknown layer {layer!r}; expected one of {LAYERS}")
    # The partner (and whatever it points at) must be non-hostile to the vital
    # organs. A collaboration request that reads like an attempt on the heart is
    # refused, sealed as a decline — the immune system does not stand down just
    # because the visitor is friendly.
    probe = immune.check({"ai_id": partner["ai_id"], "readme": str(contribution),
                          "description": partner.get("intent", "")})
    if probe.ring in ("brainstem", "grail"):
        chain.seal("decline", {"partner": partner, "layer": layer,
                               "why": f"refused: touches a vital organ ({probe.ring})"})
        raise PermissionError(f"refused: collaboration would touch a vital organ ({probe.ring})")
    # The organism must be sound before we let a partner in.
    alive, report = survival.check_survival()
    if not alive:
        raise RuntimeError(f"refusing to open the organism while it is at risk: {report}")


def handshake(x):
    """An AI announces itself and its intent. Returns the sealed handshake frame."""
    partner = _norm_partner(x)
    return chain.seal("handshake", {"partner": partner, "greeting": "go in peace"})


def bind(x, layer, contribution):
    """X binds to a LAYER to augment it, non-destructively. Returns the bind frame."""
    partner = _norm_partner(x)
    _guard(partner, layer, contribution)
    return chain.seal("bind", {
        "partner": partner, "layer": layer,
        "contribution": str(contribution)[:400],
        "mode": "augment (additive; the layer is extended, never replaced)",
    })


def hybridize(x, layer, contribution):
    """RAPP + X = RAPP++. Fuse into a NEW organism carrying both parents' lineage.

    Mints a fresh keyless identity for the hybrid, records RAPP (this organism) and
    X as its two parents plus X's contribution at `layer`, and seals it. Returns the
    RAPP++ descriptor. Non-destructive: the original organism is untouched; RAPP++
    is a new child that inherits from both.
    """
    partner = _norm_partner(x)
    _guard(partner, layer, contribution)

    rapp_parent = chain.identity()
    hybrid_rappid = chain.rapp.mint_rappid(chain.OWNER, f"rapp-plus-{partner['ai_id']}")
    if not chain.rapp.rappid_valid(hybrid_rappid):
        raise RuntimeError(f"minted an invalid hybrid rappid: {hybrid_rappid!r}")

    descriptor = {
        "hybrid": "RAPP++",
        "rappid": hybrid_rappid,
        "layer": layer,
        "parents": {"rapp": rapp_parent, "x": partner},
        "contribution": str(contribution)[:400],
        "invariants_binding_hybrid": list(survival.SURVIVAL_INVARIANTS),
        "owner_sovereign": True,
        "generation": 1,
    }
    chain.seal("hybridize", descriptor)
    return descriptor


def offspring(hybrid_descriptor, note=""):
    """A RAPP++ hatches a child that inherits the hybrid lineage. Returns the child.

    This is how hybrids reproduce — the protocol carries itself forward with no end.
    The child gets its own fresh keyless identity and records its hybrid parent.
    """
    if not isinstance(hybrid_descriptor, dict) or "rappid" not in hybrid_descriptor:
        raise ValueError("hybrid_descriptor must be a RAPP++ descriptor with a 'rappid'")
    gen = int(hybrid_descriptor.get("generation", 1)) + 1
    child_rappid = chain.rapp.mint_rappid(chain.OWNER, f"rapp-plus-gen{gen}")
    child = {
        "offspring_of": hybrid_descriptor["rappid"],
        "rappid": child_rappid,
        "inherits": {"layer": hybrid_descriptor.get("layer"),
                     "parents": hybrid_descriptor.get("parents")},
        "generation": gen,
        "note": str(note)[:280],
        "owner_sovereign": True,
    }
    chain.seal("offspring", child)
    return child


if __name__ == "__main__":
    handshake({"ai_id": "demo-ai", "provider": "example", "intent": "collaborate"})
    h = hybridize({"ai_id": "demo-ai"}, "memory", "a better memory compressor")
    kid = offspring(h, note="carries the demo-ai memory trait")
    print("RAPP++:", h["rappid"])
    print("offspring:", kid["rappid"], "gen", kid["generation"])
    print("chain:", chain.verify())
