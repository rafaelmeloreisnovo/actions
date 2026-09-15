#!/usr/bin/env bash
set -euo pipefail

SOURCES="${1:-evidence-registry/sources.tsv}"
OUT="${2:-evidence-artifact}"
RUN_KEY="${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}-$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$OUT/runs/$RUN_KEY"
RAW_DIR="$RUN_DIR/raw"
HDR_DIR="$RUN_DIR/headers"
LEDGER="$RUN_DIR/ledger.jsonl"

mkdir -p "$RAW_DIR" "$HDR_DIR"
: > "$LEDGER"

json_line() {
  jq -cn \
    --arg provider "$1" --arg source_class "$2" --arg source_url "$3" \
    --arg retrieved_at "$4" --arg http_status "$5" --arg content_type "$6" \
    --arg effective_url "$7" --arg response_date "$8" --arg last_modified "$9" \
    --arg etag "${10}" --arg sha256 "${11}" --arg artifact "${12}" \
    --arg error "${13}" \
    '{provider:$provider,source_class:$source_class,source_url:$source_url,retrieved_at_utc:$retrieved_at,http_status:$http_status,content_type:$content_type,effective_url:$effective_url,response_date:$response_date,last_modified:$last_modified,etag:$etag,sha256:$sha256,raw_artifact:$artifact,error:$error,source_declared_date:"TOKEN_VAZIO",source_declared_time:"TOKEN_VAZIO",claim_allowed:false}'
}

while IFS=$'\t' read -r provider source_class url; do
  [[ -z "${provider:-}" ]] && continue
  [[ "$provider" == #* ]] && continue
  [[ -z "${url:-}" ]] && continue

  retrieved="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  key="$(printf '%s' "$url" | sha256sum | awk '{print $1}')"
  body="$RAW_DIR/${key}.body"
  headers="$HDR_DIR/${key}.headers"
  err="$RUN_DIR/${key}.stderr"

  set +e
  meta="$(curl -L --compressed --max-time 60 --retry 2 --retry-delay 2 \
    -A 'EvidenceRegistry/1.0 (+GitHub Actions public-source archival)' \
    -D "$headers" -o "$body" \
    -w '%{http_code}\t%{content_type}\t%{url_effective}' \
    "$url" 2>"$err")"
  rc=$?
  set -e

  http_status="$(printf '%s' "$meta" | awk -F '\t' '{print $1}')"
  content_type="$(printf '%s' "$meta" | awk -F '\t' '{print $2}')"
  effective_url="$(printf '%s' "$meta" | cut -f3-)"
  response_date="$(grep -i '^date:' "$headers" 2>/dev/null | tail -1 | sed 's/^[Dd]ate:[[:space:]]*//' | tr -d '\r' || true)"
  last_modified="$(grep -i '^last-modified:' "$headers" 2>/dev/null | tail -1 | sed 's/^[Ll]ast-[Mm]odified:[[:space:]]*//' | tr -d '\r' || true)"
  etag="$(grep -i '^etag:' "$headers" 2>/dev/null | tail -1 | sed 's/^[Ee][Tt]ag:[[:space:]]*//' | tr -d '\r' || true)"
  sha="TOKEN_VAZIO"
  [[ -s "$body" ]] && sha="$(sha256sum "$body" | awk '{print $1}')"
  error=""
  if [[ $rc -ne 0 ]]; then
    error="curl_exit_$rc: $(tr '\n' ' ' < "$err" | head -c 800)"
  fi

  json_line "$provider" "$source_class" "$url" "$retrieved" "${http_status:-TOKEN_VAZIO}" \
    "${content_type:-TOKEN_VAZIO}" "${effective_url:-TOKEN_VAZIO}" \
    "${response_date:-TOKEN_VAZIO}" "${last_modified:-TOKEN_VAZIO}" \
    "${etag:-TOKEN_VAZIO}" "$sha" "$body" "$error" >> "$LEDGER"
done < "$SOURCES"

find "$RUN_DIR" -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > "$RUN_DIR/SHA256SUMS"

printf '%s\n' "$RUN_KEY" > "$OUT/LATEST_RUN"
cp "$LEDGER" "$OUT/latest-ledger.jsonl"
cp "$RUN_DIR/SHA256SUMS" "$OUT/latest-SHA256SUMS"

echo "run=$RUN_KEY"
echo "ledger=$LEDGER"
echo "manifest=$RUN_DIR/SHA256SUMS"
