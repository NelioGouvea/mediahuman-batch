# mediahuman-batch

Automação local que adiciona em lote URLs do YouTube ao [MediaHuman YouTube to MP3](https://www.mediahuman.com/youtube-to-mp3-converter/), clicando no botão **"Colar endereço"** para cada URL de uma lista.

O script não inicia downloads: apenas adiciona os vídeos à fila do app.

## Como funciona

Para cada URL da lista:

1. Copia a URL para o clipboard.
2. Localiza o botão "Colar endereço" na tela por reconhecimento de imagem e clica.
3. Aguarda o app terminar de carregar o vídeo antes da próxima URL.

## Requisitos

- Linux com sessão **X11** (no Wayland o `pyautogui` não consegue capturar a tela nem controlar o mouse)
- Python 3.10+
- MediaHuman YouTube to MP3 instalado
- Pacotes de sistema:

```bash
sudo apt install python3-venv python3-tk python3-dev xclip gnome-screenshot
```

> No Ubuntu 25.10+ a sessão "Ubuntu on Xorg" foi removida. Uma alternativa é usar o Xfce (`sudo apt install xfce4`) e escolher **Xfce Session** na tela de login.

## Instalação

```bash
git clone <url-do-repo>
cd mediahuman-batch
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Os recortes de tela dependem de tema, fonte e escala, então cada máquina precisa gerar os seus em `assets/`:

| Arquivo | Obrigatório | Conteúdo |
| :---- | :---- | :---- |
| `colar_endereco.png` | Sim | Recorte justo do botão "Colar endereço" |
| `carregando.png` | Não | Recorte de um elemento visível só durante o carregamento (prefira texto estático a spinner) |

```bash
xfce4-screenshooter -r -s assets/colar_endereco.png
```

Se o executável não estiver em `/opt/youtube-to-mp3/YouTubeToMP3`, ajuste `APP_PATH` no topo do script.

## Uso

```bash
cp lista.example.txt lista.txt
python mediahuman_batch.py --file lista.txt --no-launch
```

| Opção | Descrição |
| :---- | :---- |
| `urls` | URLs passadas direto no comando, entre aspas |
| `--file` | Arquivo `.txt` com uma URL por linha |
| `--no-launch` | Usa a janela do app já aberta |
| `--delay` | Espera fixa em segundos entre URLs quando não há `carregando.png` (padrão: 10) |

Durante a execução, não use mouse nem teclado. Para abortar, mova o mouse para um canto da tela.

## Modos de espera

- **Indicador visual** (com `assets/carregando.png`): espera o indicador aparecer e sumir antes da próxima URL.
- **Espera fixa** (sem o recorte): aguarda `--delay` segundos entre URLs.

## Uso responsável

Baixar conteúdo do YouTube fora dos meios oficiais vai contra os Termos de Serviço da plataforma. Use apenas com conteúdo próprio, em domínio público, sob licença livre ou com autorização do detentor dos direitos.
