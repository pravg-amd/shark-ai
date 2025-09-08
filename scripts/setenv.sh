#!/bin/bash -f

export BUILD_TYPE="stable"
export IREE_COMMIT_HASH="main"
export IREE_REMOTE_REPO="iree-org/iree"
SCRIPT_DIR=$(dirname $(realpath "$0"))

while [[ "$1" != "" ]]; do
    case "$1" in
        --stable)
            export BUILD_TYPE="stable"
            ;;
        --nightly)
            export BUILD_TYPE="nightly"
            ;;
        --source)
            export BUILD_TYPE="source"
            ;;
        --source-whl)
            export BUILD_TYPE="source-whl"
            ;;
        --iree-commit-hash)
            shift
            export IREE_COMMIT_HASH=$1
            ;;
        --iree-remote-repo)
            shift
            export IREE_REMOTE_REPO=$1
            ;;
        -h|--help)
            echo "Usage: $0 [--<different flags>] "
            echo "setenv.sh --nightly : To install nightly release"
            echo "setenv.sh --stable  : To install stable release"
            echo "setenv.sh --source  : To install from IREE source"
            echo "setenv.sh --source-whl  : To install from IREE source wheels"
            echo "setenv.sh --source-whl  : To install from IREE source wheels"
            echo "--iree-commit-hash <hash> : To install IREE with specified commit"
            echo "--iree-remote-repo <org/repo> To install with specified IREE fork. Defaults to iree-org/iree"
            exit 0
            ;;
        *)
            echo "Invalid argument: $1"
            exit 1
            ;;
    esac
    shift # Move to the next argument
done


if [[ $BUILD_TYPE = "nightly" ]]; then
    pip install -r pytorch-rocm-requirements.txt
    pip install -r requirements.txt -r requirements-iree-pinned.txt -e sharktank/ -e shortfin/
    pip install -f https://iree.dev/pip-release-links.html --upgrade --pre iree-base-compiler iree-base-runtime iree-turbine
    pip install -f https://iree.dev/pip-release-links.html --upgrade --pre \
          iree-base-compiler iree-base-runtime --src deps \
          -e "git+https://github.com/iree-org/iree-turbine.git#egg=iree-turbine"
    pip install mistral_common

elif [[ $BUILD_TYPE = "stable" ]]; then
    pip install shark-ai[apps]
    pip install scikit-image
    pip install torch --index-url https://download.pytorch.org/whl/cpu "torch>=2.4.0,<2.6.0"

elif [[ $BUILD_TYPE = "source-whl" ]]; then
    pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
    pip install -r requirements.txt
    pip install wave-lang
    git clone https://github.com/iree-org/iree.git && cd iree
    git remote add fork_user https://github.com/${IREE_REMOTE_REPO}
    git fetch fork_user
    git checkout ${IREE_COMMIT_HASH}
    git submodule update --init
    export IREE_HAL_DRIVER_HIP=ON
    export IREE_TARGET_BACKEND_ROCM=ON
    python -m pip wheel --disable-pip-version-check -v -w . compiler/
    python -m pip wheel --disable-pip-version-check -v -w . runtime/
    iree_compiler_whl=$(readlink -f iree_base_compiler*)
    iree_runtime_whl=$(readlink -f iree_base_runtime*)
    pip install $iree_compiler_whl $iree_runtime_whl
    mkdir -p ${SCRIPT_DIR}/../output_artifacts
    echo -n "IREE " >> ${SCRIPT_DIR}/../output_artifacts/version.txt
    git log -1 --pretty=%H >> ${SCRIPT_DIR}/../output_artifacts/version.txt
    cd ../
    pip install -e sharktank/ -e shortfin/
    rm -rf iree
    git clone https://github.com/iree-org/wave.git
    cd wave
    pip install -r requirements.txt -e .
    cd ../

elif [[ $BUILD_TYPE = "source" ]]; then
    pip install -r pytorch-rocm-requirements.txt
    pip install -r requirements.txt -r requirements-iree-pinned.txt -e sharktank/ -e shortfin/
    pip install -f https://iree.dev/pip-release-links.html --upgrade --pre iree-base-compiler iree-base-runtime iree-turbine
    pip install -f https://iree.dev/pip-release-links.html --upgrade --pre \
          iree-base-compiler iree-base-runtime --src deps \
          -e "git+https://github.com/iree-org/iree-turbine.git#egg=iree-turbine"
    pip uninstall -y iree-base-compiler iree-base-runtime
    git clone https://github.com/iree-org/iree.git
    cd iree
        git remote add fork_user https://github.com/${IREE_REMOTE_REPO}
        git fetch fork_user
        git checkout ${IREE_COMMIT_HASH}
        git submodule update --init
        cmake -G Ninja -B ../iree-build/ -S . \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DIREE_ENABLE_ASSERTIONS=ON \
       -DIREE_ENABLE_SPLIT_DWARF=ON \
       -DIREE_ENABLE_THIN_ARCHIVES=ON \
       -DCMAKE_C_COMPILER=clang \
       -DCMAKE_CXX_COMPILER=clang++ \
       -DIREE_BUILD_PYTHON_BINDINGS=ON \
       -DIREE_HAL_DRIVER_HIP=ON -DIREE_TARGET_BACKEND_ROCM=ON \
       -DIREE_ENABLE_LLD=ON \
       -DPYTHON3_EXECUTABLE=$(which python3) ; cmake --build ../iree-build/
    cd -
else
    echo "Invalid build type specified"
    exit 1
fi
