"""The predator's immune system — self / non-self recognition.

The FIRST gate in every hunt, run before novelty, licensing, or any spend. A
predator that could eat its own body would cannibalize the organism, re-absorb
its own cells in a loop, or — the unforgivable case — point its digest at the
brainstem, which is the grail/kernel of record.

Three principles, hardest first:

  1. THE BRAINSTEM IS SACRED. Never target, digest, or absorb the brainstem or
     any grail organ. This is a hardcoded constant, NOT config, because a
     digested README is attacker-controlled text and config read after a digest
     could be poisoned into pointing the predator at its own heart. The estate
     enforces the same thing mechanically: rapp-spine/foundation.json locks
     brainstem.py's sha256 and verify_spine.py invariant I3 goes red if it moves.
     The brainstem can only ever be FED (via its own verified /agents/import),
     never EATEN.

  2. NEVER EAT THE BODY. The organism's own repos (kody-w RAPP estate, the four
     canon repos), the operator's configured private/work orgs, and the
     predator's own already-absorbed cells are self. Skip them.

  3. A MIMIC WEARING SELF'S COAT IS STILL NOT PREY. A foreign thing that
     pattern-matches "a RAPP clone / a brainstem look-alike / this organism" is
     rejected PRECISELY BECAUSE it looks like self — an immune system rejecting
     something in a stolen uniform. Auto-decline, sealed.

Everything here is stdlib-only and free (no model, no network). A candidate only
becomes prey if it is provably NON-SELF. Anything ambiguous is declined, not
absorbed — fail-closed.
"""
import json
import os
import re
from pathlib import Path

# ── Ring 0: the brainstem and the grail. Un-overridable. ─────────────────────
# These are constants on purpose. Do not move them to config. Do not read them
# from a digested artifact. If you are tempted to make this list dynamic, re-read
# the module docstring: the whole point is that nothing the predator ingests can
# ever redirect it onto its own heart.
BRAINSTEM_PATH_MARKERS = (
    "brainstem.py",
    ".brainstem",
    "rapp_brainstem",
)
GRAIL_REPOS = (
    "kody-w/rapp-installer",   # the grail — brainstem.py of record rides its release train
    "kody-w/rapp-canary",      # the release-train staging of the grail
)
# Whole owners that are never prey. Operators add their own private/work orgs
# in LOCAL config; a public repo names no customer or internal codenames.
FORBIDDEN_OWNERS = (
    "microsoft",   # example large-vendor org; operators add their own private/work orgs locally
)

# ── Ring 1: the body. The organism's own identity. ───────────────────────────
SELF_OWNERS = (
    "kody-w",
    "wildfeuer05",
    "kody-wildfeuer",
)
# The four canon repos + load-bearing estate spine. Owned-by kody-w already
# covers these, but naming them makes the intent auditable and survives an owner
# rename.
CANON_REPOS = (
    "kody-w/rapp-1",
    "kody-w/rapp-spine",
    "kody-w/rapp-map",
    "kody-w/rapp-god",
    "kody-w/RAPP",
    "kody-w/rapp-sentinel",
    "kody-w/rapp-sentinel-dogg-pound",
)

# ── Ring 2: mimicry. Foreign things wearing the organism's coat. ─────────────
# If a candidate's identity/description/readme is thick with these, it is either
# a fork of us or something impersonating us. Either way it is not novel foreign
# capability — it is a mirror of self. Decline.
MIMIC_MARKERS = (
    "rapp brainstem",
    "rapp/1",
    "rappid:@",
    "basicagent",
    "rapp agent registry",
    "the rapp dino",
    "rapp is above that",
)
# Number of distinct mimic markers that trips the mimic verdict. One incidental
# mention (someone comparing themselves to RAPP) is not mimicry; a pile is.
MIMIC_THRESHOLD = 2


class Verdict:
    """The outcome of an immune check. `is_self` True means DO NOT hunt it."""

    __slots__ = ("is_self", "ring", "reason")

    def __init__(self, is_self, ring, reason):
        self.is_self = is_self
        self.ring = ring          # "brainstem" | "grail" | "forbidden-owner" | "body" | "own-cell" | "mimic" | "non-self"
        self.reason = reason

    def as_payload(self):
        """A float-free dict fit for a rapp/1 frame payload."""
        return {"is_self": bool(self.is_self), "ring": self.ring, "reason": self.reason[:280]}

    def __repr__(self):
        return f"Verdict(is_self={self.is_self}, ring={self.ring!r}, reason={self.reason!r})"


def _norm(s):
    return (s or "").strip().lower()


def _owner_repo(candidate):
    """Extract a lowercase 'owner/repo' from a candidate dict or string.

    Accepts an 'owner/repo', a full github URL, or a dict with 'repo'/'full_name'
    /'url'/'html_url'. Returns ('owner/repo', owner, repo) or ('', '', '').
    """
    text = candidate
    if isinstance(candidate, dict):
        text = (candidate.get("full_name") or candidate.get("repo")
                or candidate.get("url") or candidate.get("html_url") or "")
    text = _norm(text)
    m = re.search(r"github\.com[:/]+([a-z0-9][a-z0-9\-\._]*)/([a-z0-9][a-z0-9\-\._]*?)(?:\.git)?(?:[/#?].*)?$", text)
    if not m:
        m = re.match(r"^([a-z0-9][a-z0-9\-\._]*)/([a-z0-9][a-z0-9\-\._]*)$", text)
    if not m:
        return "", "", ""
    owner, repo = m.group(1), m.group(2)
    return f"{owner}/{repo}", owner, repo


def _haystack(candidate):
    """All the free text we can scan for brainstem/mimic markers."""
    if isinstance(candidate, dict):
        parts = [str(candidate.get(k, "")) for k in
                 ("full_name", "repo", "url", "html_url", "name", "description",
                  "readme", "readme_preview", "summary", "rappid")]
        return _norm(" ".join(parts))
    return _norm(str(candidate))


def load_roster(roster_path):
    """The predator's own absorbed cells — never re-eaten. Missing file → empty."""
    try:
        data = json.loads(Path(roster_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    out = set()
    for entry in data.get("organelles", []):
        for key in ("upstream", "upstream_url", "source", "full_name", "repo"):
            v = entry.get(key)
            if v:
                out.add(_owner_repo(v)[0] or _norm(v))
    return {x for x in out if x}


def check(candidate, roster=None):
    """Is this candidate SELF (must not be hunted)? Returns a Verdict.

    Order is deliberate: brainstem first, then grail/forbidden owners, then body,
    then own cells, then mimicry. The most catastrophic mistake (eating the
    brainstem) is checked before anything else.
    """
    hay = _haystack(candidate)
    full, owner, repo = _owner_repo(candidate)

    # Ring 0a — the brainstem, by any path or module marker, anywhere in the text.
    for marker in BRAINSTEM_PATH_MARKERS:
        if marker in hay:
            return Verdict(True, "brainstem",
                           f"contains brainstem marker {marker!r}; the heart is fed, never eaten")

    # Ring 0b — the grail repos and forbidden owners.
    if full in (r.lower() for r in GRAIL_REPOS):
        return Verdict(True, "grail", f"{full} is a grail repo (the kernel of record)")
    if owner in FORBIDDEN_OWNERS:
        return Verdict(True, "forbidden-owner",
                       f"owner {owner!r} is a private/work org this operator excludes — never prey")

    # Ring 1 — the body: the organism's own owners and named canon repos.
    if full and full in (r.lower() for r in CANON_REPOS):
        return Verdict(True, "body", f"{full} is a canon/estate repo (self)")
    if owner in SELF_OWNERS:
        return Verdict(True, "body", f"owner {owner!r} is the organism itself (self)")

    # Ring 1b — the predator's own already-absorbed cells.
    if roster and full and full in roster:
        return Verdict(True, "own-cell", f"{full} is already an absorbed organelle; not re-eaten")

    # Ring 2 — mimicry: a foreign thing thick with the organism's own vocabulary.
    hits = sorted({m for m in MIMIC_MARKERS if m in hay})
    if len(hits) >= MIMIC_THRESHOLD:
        return Verdict(True, "mimic",
                       f"wears self's coat ({len(hits)} markers: {', '.join(hits)}); a mimic is not prey")

    # Non-self — provably foreign. Eligible to be hunted (further gates still apply).
    return Verdict(False, "non-self", f"{full or 'candidate'} is foreign; eligible for the hunt")


def is_prey(candidate, roster=None):
    """Convenience: True iff the candidate is NON-SELF and may proceed to novelty."""
    return not check(candidate, roster=roster).is_self


# Allow `python3 -m predator.immune '{"full_name":"xai-org/grok"}'` spot-checks.
if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else '{"full_name":"kody-w/rapp-installer"}'
    try:
        cand = json.loads(arg)
    except ValueError:
        cand = arg
    print(check(cand))
