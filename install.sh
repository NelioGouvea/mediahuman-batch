#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(dirname "$(readlink -f "$0")")"
MEDIAHUMAN_EXECUTABLE="/opt/youtube-to-mp3/YouTubeToMP3"
MEDIAHUMAN_DEB_URL="https://www.mediahuman.com/files/YouTubeToMP3.amd64.deb"
MEDIAHUMAN_PAGE="https://www.mediahuman.com/youtube-to-mp3-converter/"
LAUNCHER_FILE="$HOME/.local/share/applications/mediahuman-batch.desktop"

step() {
    echo
    echo "==> $1"
}

install_system_packages() {
    step "Instalando pacotes do sistema"
    sudo apt-get update
    sudo apt-get install -y python3-venv python3-tk wget
}

install_python_environment() {
    step "Criando ambiente Python"
    python3 -m venv "$PROJECT_DIR/.venv"
    "$PROJECT_DIR/.venv/bin/pip" install --upgrade pip
    "$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
}

install_mediahuman() {
    step "Verificando o MediaHuman YouTube to MP3"
    if [[ -x "$MEDIAHUMAN_EXECUTABLE" ]] || command -v YouTubeToMP3 >/dev/null; then
        echo "MediaHuman já instalado."
        return
    fi

    local deb_file
    deb_file="$(mktemp --suffix=.deb)"
    chmod 644 "$deb_file"

    if wget -O "$deb_file" "$MEDIAHUMAN_DEB_URL" && sudo apt-get install -y "$deb_file"; then
        echo "MediaHuman instalado."
    else
        echo "Não foi possível instalar o MediaHuman automaticamente."
        echo "Baixe o .deb em $MEDIAHUMAN_PAGE e instale com:"
        echo "    sudo apt install ./YouTubeToMP3.amd64.deb"
    fi

    rm -f "$deb_file"
}

create_launcher() {
    step "Criando atalho no menu"
    chmod +x "$PROJECT_DIR/run.sh"
    mkdir -p "$(dirname "$LAUNCHER_FILE")"
    cat > "$LAUNCHER_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=MediaHuman Batch
Comment=Importa playlists do YouTube para o MediaHuman YouTube to MP3
Exec=$PROJECT_DIR/run.sh
Icon=multimedia-player
Terminal=false
Categories=AudioVideo;Utility;
EOF
    echo "Atalho criado em $LAUNCHER_FILE"
}

launch_app() {
    step "Abrindo o MediaHuman Batch"
    if [[ -z "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
        echo "Nenhuma sessão gráfica detectada. Abra pelo menu quando estiver na área de trabalho."
        return
    fi
    setsid "$PROJECT_DIR/run.sh" >/dev/null 2>&1 &
}

install_system_packages
install_python_environment
install_mediahuman
create_launcher
launch_app

step "Instalação concluída"
echo "Nas próximas vezes, abra \"MediaHuman Batch\" no menu de aplicativos ou rode ./run.sh"
