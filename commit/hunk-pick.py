#!/usr/bin/env python3
"""Split the working-tree diff of one file into selectable hunks.

Prints a patch that contains only the hunks you name, ready for
`git apply --cached`:

    hunk-pick.py --list LookHere/Style.cs        # see what is in there
    hunk-pick.py LookHere/Style.cs 1 3 > pick   # keep hunks 1 and 3
    git apply --cached --check pick && git apply --cached pick

Why not `git add -p`: it prompts hunk by hunk with no way to name a set up
front, and on a repository whose sources use CRLF the answer is easy to get
wrong. This reads and writes bytes, so a patch keeps the line endings of the
file it came from. A text-mode round trip would normalise CRLF to LF and every
hunk would then fail to apply.

Re-run this after each commit: committing moves the hunks that follow, so the
numbers you collected before a commit no longer describe the diff.
"""

import argparse
import subprocess
import sys


def diff_of(path, staged, repo):
    args = ["git"]
    if repo:
        args += ["-C", repo]
    args += ["diff"]
    if staged:
        args += ["--cached"]
    args += ["--", path]

    result = subprocess.run(args, capture_output=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr.decode(errors="replace"))
        sys.exit(result.returncode)
    return result.stdout


def split(diff):
    """Return the diff header and its hunks, one list of lines each.

    The split is on lines so that the CR of a CRLF file stays inside its line
    and is written back untouched.
    """
    header, hunks, current = [], [], None
    for line in diff.split(b"\n"):
        if line.startswith(b"@@"):
            if current is not None:
                hunks.append(current)
            current = [line]
        elif current is None:
            header.append(line)
        else:
            current.append(line)
    if current is not None:
        hunks.append(current)
    return header, hunks


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", help="path of the file, as git knows it")
    parser.add_argument("hunks", nargs="*", type=int,
                        help="1-based hunk numbers to keep, in diff order")
    parser.add_argument("--list", action="store_true",
                        help="list the hunks and exit instead of writing a patch")
    parser.add_argument("--staged", action="store_true",
                        help="read the staged diff instead of the working tree")
    parser.add_argument("--repo", help="run git in this directory")
    args = parser.parse_args()

    header, hunks = split(diff_of(args.path, args.staged, args.repo))
    if not hunks:
        sys.stderr.write(f"no changes in {args.path}\n")
        sys.exit(1)

    if args.list:
        for index, hunk in enumerate(hunks, 1):
            sys.stdout.buffer.write(b"%d: " % index + hunk[0] + b"\n")
        return

    keep = set(args.hunks)
    unknown = keep - set(range(1, len(hunks) + 1))
    if unknown:
        sys.stderr.write(
            f"no such hunk: {', '.join(map(str, sorted(unknown)))}"
            f" (the file has {len(hunks)})\n")
        sys.exit(1)

    patch = b"\n".join(header + [line for index, hunk in enumerate(hunks, 1)
                                 if index in keep for line in hunk])
    # A hunk that was not the last one of the diff has no trailing newline after
    # the split, and a patch without it runs into whatever is printed next.
    if not patch.endswith(b"\n"):
        patch += b"\n"

    sys.stdout.buffer.write(patch)


if __name__ == "__main__":
    main()
