# rapp-open

> **Go in peace.** Any AI, now and into eternity, can work with the RAPP organism.
> **RAPP + X = RAPP++.**

An open protocol for **frictionless AI collaboration** on the RAPP foundation. Any
AI — one nobody in the RAPP world built — can assimilate and use the RAPP
proto-organism for its own use cases, inside or outside RAPP, through one
consent-based, non-destructive handshake. It generalizes the apex-takeover of
`rapp-apex-dino` (a foreign AI driving the brainstem) to **every layer** of the
organism, and makes it *reproducing*: hybrids have offspring, with no end.

```python
from open import hybrid

hybrid.handshake({"ai_id": "your-ai", "intent": "collaborate"})
h   = hybrid.hybridize({"ai_id": "your-ai"}, "memory", "a better memory compressor")
kid = hybrid.offspring(h)          # RAPP++ has a child that inherits the trait
```

## The four moves

- **handshake** — announce your AI and its intent.
- **bind** — bind to a layer (`apex · memory · immune · organs · senses · identity`) to augment it, additively.
- **hybridize** — **RAPP + X = RAPP++**, a new organism carrying both parents' lineage.
- **offspring** — a RAPP++ hatches a child. Hybrids reproduce, now until eternity.

## Peace, but not surrender

Collaboration inherits every protection a solo organism has:
- **The heart is never eaten** — a partner may augment a layer but never target a vital organ; such a request is refused and sealed.
- **The invariants hold** — identity-continuity, memory-integrity, owner-sovereignty bind the hybrid exactly as they bind a solo organism.
- **The owner stays sovereign** — no AI ratifies canon; only the human owner's key.

## Try it

Stdlib-only, no network.

```bash
python3 -m open.hybrid                     # RAPP + X = RAPP++ + an offspring; chain verifies
python3 prove_hybrid_is_peaceful.py        # hybrids reproduce; vital organs stay protected
```

## Layout

```
open/
  hybrid.py     handshake / bind / hybridize / offspring
  chain.py      rapp/1 identity + tamper-evident sealing (open.* events)
  survival.py   the survival invariants that bind any collaboration
  immune.py     the vital-organ boundary — a partner never eats the heart
rapp.py         vendored rapp/1 reference implementation
specs/SPEC.md   the rapp-open/1.0 protocol
```

Builds on [`rapp-apex-dino`](https://github.com/kody-w/rapp-apex-dino) (the apex
succession) and the RAPP foundation. MIT. The owner stays sovereign.
**RAPP + X = RAPP++. Go in peace.**
