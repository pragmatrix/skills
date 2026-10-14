#!/usr/bin/env bash
# Lists or resolves the review threads of a GitHub PR through GraphQL. The REST endpoint
# `pulls/N/comments` omits threads (unsubmitted reviews among them) and carries no resolution
# state, so it can report "no comments" where threads are open.
#
#   threads.sh list <owner/repo> <pr>     every thread: id, state, path:line, comments
#   threads.sh resolve <thread-id>...     resolve without posting a reply
set -euo pipefail

usage() {
    echo "usage: $0 list <owner/repo> <pr> | resolve <thread-id>..." >&2
    exit 2
}

[ $# -ge 1 ] || usage
command=$1
shift

case $command in
list)
    [ $# -eq 2 ] || usage
    owner=${1%%/*}
    name=${1#*/}
    gh api graphql --paginate \
        -f owner="$owner" -f name="$name" -F number="$2" \
        -f query='
query($owner: String!, $name: String!, $number: Int!, $endCursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line originalLine
          comments(first: 50) { nodes { author { login } createdAt body } }
        }
      }
    }
  }
}' \
        --jq '.data.repository.pullRequest.reviewThreads.nodes[]
            | "\(.id) \(if .isResolved then "resolved" else "OPEN" end)\(if .isOutdated then " outdated" else "" end) \(.path):\(.line // .originalLine)\n"
              + ([.comments.nodes[] | "  [\(.author.login) \(.createdAt)] \(.body)"] | join("\n"))'
    ;;
resolve)
    [ $# -ge 1 ] || usage
    for id in "$@"; do
        gh api graphql -f id="$id" \
            -f query='mutation($id: ID!) { resolveReviewThread(input: {threadId: $id}) { thread { id isResolved } } }' \
            --jq '.data.resolveReviewThread.thread | "\(.id) resolved=\(.isResolved)"'
    done
    ;;
*)
    usage
    ;;
esac
