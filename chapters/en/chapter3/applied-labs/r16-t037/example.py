"""Count total and trainable parameters from a local named-parameter manifest.

The manifest maps a parameter name to its size. A name is frozen when it starts
with one of the freeze prefixes. A prefix that matches nothing is reported.
Toy numbers only, no real model is loaded.
"""


def account_parameters(manifest, freeze_prefixes=()):
    for name, count in manifest.items():
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ValueError(f"size of {repr(name)} must be a whole number >= 0")
    total = sum(manifest.values())
    frozen = 0
    matched = set()
    for name, count in manifest.items():
        hits = [prefix for prefix in freeze_prefixes if name.startswith(prefix)]
        if hits:
            frozen += count
            matched.update(hits)
    return {"total": total, "frozen": frozen, "trainable": total - frozen,
            "unmatched_prefixes": sorted(set(freeze_prefixes) - matched)}


def main():
    manifest = {"encoder": 100, "head": 20}
    print("manifest:", manifest)
    print("Worked example, freeze ['encoder']:")
    for name, count in manifest.items():
        state = "frozen" if name.startswith("encoder") else "trainable"
        print(f"  {name}: {count} -> {state}")
    for freeze in (["encoder"], [], ["encoder", "decoder"]):
        print(f"freeze {freeze} -> {account_parameters(manifest, freeze)}")


if __name__ == "__main__":
    main()
