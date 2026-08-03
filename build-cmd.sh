#!/usr/bin/env bash

# turn on verbose debugging output for parabuild logs.
exec 4>&1; export BASH_XTRACEFD=4; set -x
# make errors fatal
set -e
# complain about unset env variables
set -u

# check autobuild is around or fail
if [ -z "$AUTOBUILD" ] ; then
    exit 1
fi

if [ "$OSTYPE" = "cygwin" ] ; then
    autobuild="$(cygpath -u $AUTOBUILD)"
else
    autobuild="$AUTOBUILD"
fi

STAGING_DIR="$(pwd)"
TOP_DIR="$(dirname "$0")"
INTER_DIR="${TOP_DIR}/Inter"
SYMBOLS2_DIR="${TOP_DIR}/Noto_Sans_Symbols_2"

# load autobuild provided shell functions and variables
source_environment_tempfile="$STAGING_DIR/source_environment.sh"
"$autobuild" source_environment > "$source_environment_tempfile"
set +x
. "$source_environment_tempfile"
set -x

mkdir -p "${STAGING_DIR}/LICENSES"
cp "${INTER_DIR}/OFL.txt" "${STAGING_DIR}/LICENSES/google_inter.txt"
cp "${SYMBOLS2_DIR}/OFL.txt" "${STAGING_DIR}/LICENSES/google_noto_sans_symbols_2.txt"

# 1.1.0: add Noto Sans Symbols 2
fonts_version="1.1.0"
build=${AUTOBUILD_BUILD_ID:=0}
echo "${fonts_version}.${build}" > "${STAGING_DIR}/VERSION.txt"

FONTS_DIR="${STAGING_DIR}/fonts"
test -d ${FONTS_DIR} || mkdir ${FONTS_DIR}

# Copy and rename variable fonts to remove commas (viewer builds don't like them)
cp -v "${INTER_DIR}/Inter-Italic-VariableFont_opsz,wght.ttf" "${FONTS_DIR}/InterItalicVariableFont.ttf"
cp -v "${INTER_DIR}/Inter-VariableFont_opsz,wght.ttf" "${FONTS_DIR}/InterVariableFont.ttf"

# Edit unicode-blocks.txt to add ranges
if ! python3 -c "import fontTools" >/dev/null 2>&1; then
    echo "error: fontTools is required to build Noto Sans Symbols 2 subset" >&2
    echo "  pip install fonttools" >&2
    exit 1
fi
python3 "${SYMBOLS2_DIR}/subset_symbols.py" \
    --blocks "${SYMBOLS2_DIR}/unicode-blocks.txt" \
    --source "${SYMBOLS2_DIR}/NotoSansSymbols2-Regular-hinted.ttf" \
    --output "${FONTS_DIR}/NotoSansSymbols2-Regular.ttf"
