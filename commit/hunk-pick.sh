#!/bin/sh

# Split one file's working-tree diff into selectable hunks.
#
# Prints a patch containing only the named hunks, ready for git apply --cached:
#
#   hunk-pick.sh --list path/to/file
#   hunk-pick.sh path/to/file 1 3 > pick
#   git apply --cached --check pick && git apply --cached pick

usage() {
    printf '%s\n' "usage: hunk-pick.sh [--list] [--staged] [--repo DIR] PATH [HUNK ...]" >&2
    exit 2
}

list=false
staged=false
repo=
path=
hunks=

while [ "$#" -gt 0 ]; do
    case $1 in
        --list)
            list=true
            ;;
        --staged)
            staged=true
            ;;
        --repo)
            shift
            [ "$#" -gt 0 ] || usage
            repo=$1
            ;;
        --help|-h)
            usage
            ;;
        --)
            shift
            [ "$#" -gt 0 ] || usage
            path=$1
            shift
            hunks=$*
            break
            ;;
        -*)
            printf 'unknown option: %s\n' "$1" >&2
            usage
            ;;
        *)
            if [ -z "$path" ]; then
                path=$1
            else
                hunks=${hunks:+$hunks }$1
            fi
            ;;
    esac
    shift
done

[ -n "$path" ] || usage

diff_file=$(mktemp "${TMPDIR:-/tmp}/hunk-pick.XXXXXX") || exit 1
trap 'rm -f "$diff_file"' EXIT HUP INT TERM

if [ -n "$repo" ]; then
    if [ "$staged" = true ]; then
        git -C "$repo" diff --cached -- "$path" >"$diff_file"
    else
        git -C "$repo" diff -- "$path" >"$diff_file"
    fi
elif [ "$staged" = true ]; then
    git diff --cached -- "$path" >"$diff_file"
else
    git diff -- "$path" >"$diff_file"
fi
git_status=$?
[ "$git_status" -eq 0 ] || exit "$git_status"

# Keep the diff in a file: command substitution strips trailing newlines and
# text-mode shell pipelines are not suitable for CRLF sources.

awk -v list="$list" -v requested="$hunks" -v path="$path" '
function fail(message) {
    print message > "/dev/stderr"
    exit 1
}
function selected(number,    i, value) {
    if (requested == "") return 0
    count = split(requested, values, /[[:space:]]+/)
    for (i = 1; i <= count; i++) {
        value = values[i] + 0
        if (value == number && values[i] ~ /^[0-9]+$/) return 1
    }
    return 0
}
function emit_header(    i) {
    for (i = 1; i <= header_count; i++) print header[i]
}
function emit_hunk(number,    i) {
    if (list == "true") {
        printf "%d: %s\n", number, hunk[number, 1]
    } else if (selected(number)) {
        for (i = 1; i <= hunk_count[number]; i++) print hunk[number, i]
    }
}
BEGIN {
    hunk_number = 0
    header_count = 0
}
{
    if ($0 ~ /^@@/) {
        hunk_number++
        hunk_count[hunk_number] = 1
        hunk[hunk_number, 1] = $0
    } else if (hunk_number == 0) {
        header[++header_count] = $0
    } else {
        hunk[hunk_number, ++hunk_count[hunk_number]] = $0
    }
}
END {
    if (hunk_number == 0) fail("no changes in " path)
    if (list == "true") {
        for (i = 1; i <= hunk_number; i++) emit_hunk(i)
        exit 0
    }

    count = split(requested, values, /[[:space:]]+/)
    for (i = 1; i <= count; i++) {
        if (values[i] !~ /^[0-9]+$/ || values[i] < 1 || values[i] > hunk_number)
            fail("no such hunk: " values[i] " (the file has " hunk_number ")")
    }

    emit_header()
    for (i = 1; i <= hunk_number; i++) emit_hunk(i)
}
' "$diff_file"