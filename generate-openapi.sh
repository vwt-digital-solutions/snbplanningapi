#!/bin/bash
cd api_server || exit
openapi-generator generate -i endpoint_api.yaml -g python-flask -o ./  --type-mappings=datetime=str
cd ../ || exit

