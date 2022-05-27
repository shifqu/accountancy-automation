#!/bin/bash
set -euxo pipefail

./scripts/clean.sh
./scripts/lint.sh
./scripts/test.sh
