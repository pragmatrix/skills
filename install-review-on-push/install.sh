#!/bin/sh

# Install the review-on-push pre-push hook into the current repository, and
# nowhere else.
#
#   install.sh
#
# The hook goes to the path git resolves for hooks/pre-push, which honors
# core.hooksPath. An earlier copy of this hook is replaced. Any other existing
# pre-push hook is left alone and the script exits with status 3.
#
# The copy gets the skills folder this script lives in, so the review run can
# read the skills from there. The folder is written as the path this script was
# run by, and again with symlinks resolved.

src=$(dirname "$0")/pre-push
marker='# review-on-push pre-push hook.'

skills_dir=$(cd "$(dirname "$0")/.." && pwd) || exit 1
skills_dir_resolved=$(cd -P "$(dirname "$0")/.." && pwd) || exit 1

dest=$(git rev-parse --path-format=absolute --git-path hooks/pre-push) || exit 1

if [ -e "$dest" ] && ! grep -qF "$marker" "$dest"; then
    printf 'install.sh: %s exists and is not a review-on-push hook\n' "$dest" >&2
    exit 3
fi

# Wraps $1 in single quotes for the shell, so any path survives the copy.
quote() {
    printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

# awk takes the quoted paths from the environment, which keeps backslashes as
# they are.
mkdir -p "$(dirname "$dest")" &&
    SKILLS_DIR=$(quote "$skills_dir") \
    SKILLS_DIR_RESOLVED=$(quote "$skills_dir_resolved") \
    awk '
        $0 == "skills_dir=" { print "skills_dir=" ENVIRON["SKILLS_DIR"]; next }
        $0 == "skills_dir_resolved=" { print "skills_dir_resolved=" ENVIRON["SKILLS_DIR_RESOLVED"]; next }
        { print }
    ' "$src" >"$dest" &&
    chmod +x "$dest" &&
    printf '%s\n' "$dest" || exit 1
