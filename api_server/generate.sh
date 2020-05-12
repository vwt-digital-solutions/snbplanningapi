#!/usr/bin/env bash
docker run --rm -v "${PWD}":/local openapitools/openapi-generator-cli generate \
--type-mappings=datetime=str \
-i /local/endpoint_api.yaml \
-g python-flask \
-o /local

for f in openapi_server/models/*.py; do
  if ! grep -q '# flake8: noqa' "$f"; then
    echo '# flake8: noqa' >>"$f"
  fi
done
