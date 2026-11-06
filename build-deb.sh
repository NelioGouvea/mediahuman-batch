#!/usr/bin/env bash
set -euo pipefail
umask 022

VERSION="${1:-1.0.0}"
PROJECT_DIR="$(dirname "$(readlink -f "$0")")"
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT

PACKAGE_DIR="$BUILD_DIR/mediahuman-batch"
APP_DIR="$PACKAGE_DIR/opt/mediahuman-batch"
OUTPUT="$PROJECT_DIR/dist/mediahuman-batch_${VERSION}_all.deb"

cd "$PROJECT_DIR"

install -d -m 755 "$PACKAGE_DIR/DEBIAN" "$APP_DIR/app" "$PACKAGE_DIR/usr/bin" "$PACKAGE_DIR/usr/share/applications"
install -m 644 app/*.py "$APP_DIR/app/"
install -m 644 requirements.txt "$APP_DIR/"
install -m 755 packaging/mediahuman-batch "$PACKAGE_DIR/usr/bin/"
install -m 644 packaging/mediahuman-batch.desktop "$PACKAGE_DIR/usr/share/applications/"
install -m 755 packaging/postinst packaging/postrm "$PACKAGE_DIR/DEBIAN/"
sed "s/@VERSION@/$VERSION/" packaging/control > "$PACKAGE_DIR/DEBIAN/control"

mkdir -p dist
dpkg-deb --root-owner-group --build "$PACKAGE_DIR" "$OUTPUT"
echo "Pacote gerado: $OUTPUT"
