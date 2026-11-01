#!/bin/sh

# Install the review-on-push pre-push hook into the current repository, and
# nowhere else.
#
#   install.sh [skill...]
#
# The hook goes to the path git resolves for hooks/pre-push, which honors
# core.hooksPath. An earlier copy of this hook is replaced. Any other existing
# pre-push hook is left alone and the script exits with status 3.
#
# The skills given are the review skills the hook runs, each in a run of its
# own. Without any, an earlier copy's list is kept, and a first install runs
# the review skill alone.
#
# The copy gets the skills folder this script lives in, so the review runs can
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

if [ $# -gt 0 ]; then
    review_skills=$*
elif [ -e "$dest" ]; then
    review_skills=$(sed -n "s/^review_skills='\(.*\)'$/\1/p" "$dest")
fi
[ -n "$review_skills" ] || review_skills=review
for skill in $review_skills; do
    if [ ! -f "$skills_dir/$skill/SKILL.md" ]; then
        printf 'install.sh: no skill %s in %s\n' "$skill" "$skills_dir" >&2
        exit 1
    fi
done

# Wraps $1 in single quotes for the shell, so any path survives the copy.
quote() {
    printf "'%s'" "$(printf '%s' "$1" | sed "s/'/'\\\\''/g")"
}

# awk takes the quoted paths from the environment, which keeps backslashes as
# they are.
mkdir -p "$(dirname "$dest")" &&
    SKILLS_DIR=$(quote "$skills_dir") \
    SKILLS_DIR_RESOLVED=$(quote "$skills_dir_resolved") \
    REVIEW_SKILLS=$(quote "$review_skills") \
    awk '
        $0 == "skills_dir=" { print "skills_dir=" ENVIRON["SKILLS_DIR"]; next }
        $0 == "skills_dir_resolved=" { print "skills_dir_resolved=" ENVIRON["SKILLS_DIR_RESOLVED"]; next }
        $0 == "review_skills='"'"'review'"'"'" { print "review_skills=" ENVIRON["REVIEW_SKILLS"]; next }
        { print }
    ' "$src" >"$dest" &&
    chmod +x "$dest" &&
    printf '%s: %s\n' "$dest" "$review_skills" || exit 1
