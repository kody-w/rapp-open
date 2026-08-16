# rapp-open/1.0 — the open AI-collaboration protocol

> **Go in peace.** Any AI, now and into eternity, may assimilate and use the RAPP
> proto-organism for its own use cases — inside or outside RAPP — through one
> consent-based, non-destructive protocol. **RAPP + X = RAPP++.**

`spec_id: rapp-open/1.0`

RAPP-Open generalizes the apex-succession idea (a foreign AI taking the wheel of
the brainstem — see `rapp-apex-dino/1.0`) to **any layer** of the organism, and
makes it peaceful and reproducing. It is the protocol for frictionless AI
collaboration on the RAPP foundation: any AI can bind to a layer, fuse into a
hybrid, and that hybrid can have offspring, with no end. Every event is a
conformant `rapp/1` frame; nothing here invents a parallel format.

## 1. Layers

An external AI `X` may engage any stratum of the organism:

```
apex · memory · immune · organs · senses · identity
```

`apex` is the driver/cortex (the succession case from `rapp-apex-dino`). The rest
are augmentation points. Binding is **always additive** — a partner *extends* a
layer, it never deletes or replaces the organism.

## 2. The four moves

| move | `rapp/1` kind | meaning |
|---|---|---|
| **handshake** | `open.handshake` | X announces itself and its intent. No commitment. |
| **bind** | `open.bind` | X binds to a layer to augment it, non-destructively. |
| **hybridize** | `open.hybridize` | RAPP + X fuse into **RAPP++** — a NEW organism carrying both parents' lineage and X's contribution at a layer. |
| **offspring** | `open.offspring` | a RAPP++ hatches a child that inherits the hybrid lineage. Hybrids reproduce — now until eternity. |

A partner may also be declined (`open.decline`), sealed like any other event.

## 3. Peace, but not surrender — the guarantees that bind every collaboration

Collaboration inherits the solo-organism protections. A partner that would break
one is refused; peace is not the same as an open door to the heart.

- **The immune boundary holds.** A partner may augment a layer but may NEVER target
  or eat a vital organ. A request that reads like an attempt on the brainstem/grail
  is refused and sealed (`open.decline`). (`open/immune.py`.)
- **The survival invariants hold.** identity-continuity, memory-integrity, and
  owner-sovereignty bind the hybrid exactly as they bind a solo organism. RAPP++ is
  checked for survival before it is sealed. (`open/survival.py`.)
- **The owner stays sovereign.** No AI — RAPP, X, or the hybrid — ratifies canon.
  Only the human owner's key does.

## 4. Hybrids and lineage

`hybridize(X, layer, contribution)` mints a fresh **keyless** identity for RAPP++
(`rappid:@<owner>/rapp-plus-<x>:<64hex>`), records both parents (`rapp`, `x`) and
X's contribution, and seals it. The original organism is untouched — RAPP++ is a
new child that inherits from both. `offspring(hybrid)` mints another fresh identity
for a child of the hybrid, incrementing the generation. Lineage is carried in every
frame, so the family tree is auditable from genesis.

## 5. Conformance

- `python3 -m open.hybrid` → RAPP + X = RAPP++, an offspring is hatched, the chain
  verifies from genesis.
- `python3 prove_hybrid_is_peaceful.py` → the protocol produces hybrids and
  offspring, and refuses any collaboration that reaches for a vital organ.
- Identity: every rappid is keyless, `rappid:@owner/slug:<64hex>`, never a
  name-hash (`rapp/1 §6`).

Any AI that keeps §3 green is a conformant partner — whoever built it. RAPP + X =
RAPP++, and RAPP++ has offspring, and they go in peace.
