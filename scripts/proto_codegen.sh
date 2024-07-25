#!/bin/bash
# This script generates proto code but doesn't generate the grpc stubs
set -ex

repo_root="$(git rev-parse --show-toplevel)"
PROTO_REPO_DIR="$repo_root/protos"
venv_dir="/tmp/proto_codegen_venv"

cd "$repo_root"

# Activate the virtual environment
source "$repo_root/venv/bin/activate"

# Ensure protoc-gen-mypy is in the PATH
export PATH="$repo_root/venv/bin:$PATH"

# clean up old generated code
find "$PROTO_REPO_DIR" -regex ".*_pb2.*\.pyi?" -exec rm {} +

# generate proto code for all protos
all_protos=$(find "$PROTO_REPO_DIR" -iname "*.proto")
python -m grpc_tools.protoc \
    -I "$PROTO_REPO_DIR" \
    --python_out="$repo_root/protos" \
    --mypy_out="$repo_root/protos" \
    $all_protos

echo "Latest proto generation done."
