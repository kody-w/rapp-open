"""The predator's biography — a rapp/1 tamper-evident hash-chain.

Every decision the predator makes (hunt, digest, absorb, decline, reprobe) is
sealed as one conformant rapp/1 frame on the predator's own memory-stream. This
is the same discipline the three watchers use in neighborhood.py: a chain, not a
log, so "the predator says it absorbed X" becomes "the predator's record verifies
from genesis, and here is the head hash."

Conformance is not optional and not approximated — we call the repo's vendored
rapp.py (the reference implementation of record) for minting, framing, and
verification. Rules we obey (rapp-1 SPEC §6/§7):

  * identity is a keyless rappid minted ONCE from uuid4 octets, then immutable
    (never a name-hash, never uuid4().hex).
  * a frame is the 11-key envelope; payload is a JSON object with NO floats;
    prev links the predecessor's payload_hash; utc is the fixed millisecond form
    and non-decreasing; kind is two lowercase-hyphen segments joined by a dot.
  * every frame is verified with rapp.verify_frame BEFORE it is appended; an
    invalid frame is refused, never written.
  * the chain is append-only and immutable; a broken chain is reported as drift,
    never silently rewritten (that is an owner-authorized re-genesis, not ours).
  * the head is anchored OUTSIDE the chain, because a chain cannot detect its own
    truncation — an interior frame with a repeated payload could be dropped and
    the rest resealed and it would still verify. The external anchor is the
    outside witness a splice cannot rewrite.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# The vendored reference implementation lives at the repo root.
_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
import rapp  # noqa: E402  (the rapp/1 reference impl of record)

OWNER = os.environ.get("APEX_OWNER", "kody-w")
SLUG = "rapp-open"
KIND_PREFIX = "open"           # frames are apex.<verb>
VALID_VERBS = ("hunt", "digest", "absorb", "decline", "reprobe", "genesis",
               "propose", "succession",
               "handshake", "bind", "hybridize", "offspring")   # succession = the alpha/leader slot changed hands

_STATE = _REPO / "state" / "open"
_IDENTITY = _STATE / "identity.json"
_CHAIN = _STATE / "chain.jsonl"

# The external anchor lives OUTSIDE the repo tree, keyed to this install so a
# fresh clone never inherits another install's high-water mark.
def _anchor_path():
    # Keyed to this install AND this stream slug, so a fresh clone never inherits
    # another install's high-water mark and two organisms on one machine never
    # collide on a shared ledger.
    key = rapp.H("rapp/1:install", {"path": str(Path.home()), "slug": SLUG})[:16]
    base = Path.home() / "Library" / "Application Support" / "rapp-open"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"anchor-{key}.json"


def utc_now():
    """rapp-1 §7.4 fixed form: YYYY-MM-DDTHH:MM:SS.mmmZ, exactly 3 fractional digits."""
    n = datetime.now(timezone.utc)
    return n.strftime("%Y-%m-%dT%H:%M:%S.") + f"{n.microsecond // 1000:03d}Z"


def identity():
    """Mint-once keyless rappid; reused forever after. Never re-minted on read."""
    if _IDENTITY.exists():
        return json.loads(_IDENTITY.read_text(encoding="utf-8"))["rappid"]
    _STATE.mkdir(parents=True, exist_ok=True)
    rid = rapp.mint_rappid(OWNER, SLUG)          # keyless, from uuid4 octets
    if not rapp.rappid_valid(rid):               # belt-and-suspenders on the mint
        raise RuntimeError(f"minted an invalid rappid: {rid!r}")
    _IDENTITY.write_text(json.dumps({"schema": "rapp/1", "rappid": rid,
                                     "kind": "organism", "name": SLUG,
                                     "parent_rappid": None}, indent=2) + "\n",
                         encoding="utf-8")
    return rid


def read_chain():
    if not _CHAIN.exists():
        return []
    return [json.loads(l) for l in _CHAIN.read_text(encoding="utf-8").splitlines() if l.strip()]


def _assert_float_free(obj, where="payload"):
    """rapp-1 canonicalization rejects floats; catch them here with a clear message."""
    if isinstance(obj, float):
        raise ValueError(f"{where} contains a float ({obj!r}); rapp/1 payloads use ints/strings only")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _assert_float_free(v, f"{where}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _assert_float_free(v, f"{where}[{i}]")


def seal(verb, payload):
    """Append one verified predator.<verb> frame. Returns the frame.

    Refuses to write an invalid frame, an unknown verb, a non-object payload, or a
    payload carrying a float.
    """
    if verb not in VALID_VERBS:
        raise ValueError(f"unknown predator verb {verb!r}; expected one of {VALID_VERBS}")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object (dict)")
    _assert_float_free(payload)

    stream = identity()                          # the rappid IS the stream of record
    chain = read_chain()
    head = chain[-1] if chain else None
    frame = rapp.build_frame(
        kind=f"{KIND_PREFIX}.{verb}",
        stream_id=stream,
        seq=(head["seq"] + 1) if head else 0,
        utc=utc_now(),
        payload=payload,
        prev=head["payload_hash"] if head else None,   # links the PARTICLE, per §7.4
        prev_wave=None,                                 # null off-swarm (memory-stream)
    )
    ok, step, why = rapp.verify_frame(frame, head=head, stream_id_of_record=stream)
    if not ok:
        raise ValueError(f"refusing to append an invalid frame (step {step}): {why}")

    _STATE.mkdir(parents=True, exist_ok=True)
    with open(_CHAIN, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(frame, ensure_ascii=False) + "\n")
    _anchor(frame)
    return frame


def verify():
    """Re-verify the whole chain from genesis. Returns (ok, detail)."""
    stream = identity()
    chain = read_chain()
    if not chain:
        return True, "empty chain"
    head = None
    for i, frame in enumerate(chain):
        ok, step, why = rapp.verify_frame(frame, head=head, stream_id_of_record=stream)
        if not ok:
            return False, f"frame {i} failed §7.5 step {step}: {why}"
        head = frame
    return True, f"{len(chain)} frames verified from genesis"


def _anchor(frame):
    """Witness the head outside the chain (splice/truncation detection)."""
    p = _anchor_path()
    try:
        led = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        led = {"schema": "rapp-predator-anchor/1.0", "stream_id": identity(), "high_water": -1}
    if frame["seq"] >= led.get("high_water", -1):
        led["high_water"] = frame["seq"]
        led["head_frame_hash"] = frame["frame_hash"]
        led["head_payload_hash"] = frame["payload_hash"]
        led["utc"] = frame["utc"]
        p.write_text(json.dumps(led, indent=2) + "\n", encoding="utf-8")
    return led


def check_anchor():
    """Compare the chain head to the external witness. Returns (ok, detail).

    Truncation shows as a chain shorter than what was witnessed.
    """
    chain = read_chain()
    try:
        led = json.loads(_anchor_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True, "no anchor yet"
    hw = led.get("high_water", -1)
    if not chain:
        return (hw < 0), ("empty chain, empty anchor" if hw < 0 else f"TRUNCATED: anchor@{hw} but chain empty")
    head = chain[-1]
    if head["seq"] < hw:
        return False, f"TRUNCATED: anchor witnessed seq {hw}, chain head is seq {head['seq']}"
    if head["seq"] == hw and head["frame_hash"] != led.get("head_frame_hash"):
        return False, f"SPLICE: seq {hw} frame_hash differs from the anchored witness"
    return True, f"head seq {head['seq']} consistent with anchor high-water {hw}"


if __name__ == "__main__":
    # Smoke: mint, seal a genesis, verify, show the head.
    rid = identity()
    print("rappid:", rid, "valid:", rapp.rappid_valid(rid))
    if not read_chain():
        f = seal("genesis", {"note": "predator awakened", "motto": "RAPP is above that"})
        print("genesis frame_hash:", f["frame_hash"])
    ok, detail = verify()
    print("verify:", ok, detail)
    print("anchor:", check_anchor())
