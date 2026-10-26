import json
import re
import sys

TAG = re.compile(r"FEX-(\d{4})")
VERSION = re.compile(r"(\d+)-r(\d+)")


def release_of(tag):
    match = TAG.fullmatch(tag or "")
    if not match:
        raise ValueError("not a FEX release tag: %r" % tag)
    return match.group(1)


def next_version(current, tag):
    match = VERSION.fullmatch(current or "")
    build = int(match.group(2)) if match else 0
    return "%s-r%d" % (release_of(tag), build + 1)


def reasons(recorded, tag, source):
    release_of(tag)
    found = []
    if recorded.get("fex") != tag:
        found.append("FEX %s -> %s" % (recorded.get("fex") or "unrecorded", tag))
    if recorded.get("source") != source:
        found.append("tools/fex %s -> %s" % ((recorded.get("source") or "unrecorded")[:12], source[:12]))
    return found


def main(argv):
    action, path = argv[1], argv[2]
    with open(path, encoding="utf-8") as f:
        recorded = json.load(f)
    if action == "next-version":
        print(next_version(recorded.get("version"), argv[3]))
    elif action == "changed":
        print("; ".join(reasons(recorded, argv[3], argv[4])))
    else:
        raise SystemExit("usage: plan.py next-version FEX_JSON TAG | changed FEX_JSON TAG COMMIT")


if __name__ == "__main__":
    main(sys.argv)
