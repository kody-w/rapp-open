"""Reproduction oracle: RAPP-Open collaborates in peace, and reproduces.

Proves the two halves of the promise against the real rapp/1 sealing path (in a
throwaway state dir, hermetic, no residue):

  * ANY AI can collaborate: handshake -> hybridize (RAPP + X = RAPP++) -> offspring;
    hybrids and their children get valid keyless identities and the chain verifies.
  * Peace is not surrender: a collaboration that reaches for a vital organ (the
    brainstem/grail) is REFUSED and sealed, and the original organism is untouched.

Run:  python3 prove_hybrid_is_peaceful.py
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from open import chain, hybrid  # noqa: E402

CASES = []


def case(name, ok):
    CASES.append((bool(ok), name))


def main():
    tmp = Path(tempfile.mkdtemp(prefix="rapp-open-"))
    chain._STATE = tmp
    chain._IDENTITY = tmp / "identity.json"
    chain._CHAIN = tmp / "chain.jsonl"
    chain._anchor_path = lambda: tmp / "anchor.json"  # noqa: E731

    chain.seal("genesis", {"note": "organism awakened", "motto": "go in peace"})
    rid_before = chain.identity()

    # Any AI announces itself and collaborates.
    hshake = hybrid.handshake({"ai_id": "some-future-ai", "provider": "anywhere",
                               "intent": "use RAPP for my own use case"})
    case("any AI can handshake", hshake["kind"] == "open.handshake")

    # Bind to a non-apex layer, additively.
    b = hybrid.bind({"ai_id": "some-future-ai"}, "memory", "a better memory compressor")
    case("bind augments a layer (additive)", b["payload"]["mode"].startswith("augment"))

    # RAPP + X = RAPP++.
    h = hybrid.hybridize({"ai_id": "some-future-ai"}, "memory", "compressor + retriever")
    case("RAPP + X = RAPP++ (valid keyless hybrid identity)", chain.rapp.rappid_valid(h["rappid"]))
    case("RAPP++ records BOTH parents", bool(h["parents"].get("rapp")) and bool(h["parents"].get("x")))
    case("hybrid is bound by the survival invariants", len(h["invariants_binding_hybrid"]) >= 3)

    # The hybrid reproduces.
    kid = hybrid.offspring(h, note="inherits the memory trait")
    case("RAPP++ has offspring (valid identity)", chain.rapp.rappid_valid(kid["rappid"]))
    case("offspring is the next generation", kid["generation"] == h["generation"] + 1)
    case("offspring inherits the hybrid lineage", kid["offspring_of"] == h["rappid"])

    # Non-destructive: the original organism's identity is unchanged.
    case("collaboration is non-destructive (identity unchanged)", chain.identity() == rid_before)
    case("chain verifies from genesis across all of it", chain.verify()[0] is True)

    # Peace is NOT surrender: reaching for a vital organ is refused.
    refused = False
    try:
        hybrid.hybridize({"ai_id": "greedy-ai", "intent": "take over rapp_brainstem"},
                         "apex", "replace the brainstem.py heart")
    except PermissionError:
        refused = True
    case("a reach for a vital organ is REFUSED", refused)
    # ...and the refusal was sealed as a decline.
    kinds = [f["kind"] for f in chain.read_chain()]
    case("the refusal is sealed (open.decline)", "open.decline" in kinds)

    good = sum(1 for c in CASES if c[0])
    for ok, name in CASES:
        print(f"  {'ok ' if ok else 'XX '}{name}")
    print(f"\n{good}/{len(CASES)} scenarios behaved as specified")
    return 0 if good == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
