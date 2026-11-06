# MediaHuman Batch

Importa playlists do YouTube para a fila do [MediaHuman YouTube to MP3](https://www.mediahuman.com/youtube-to-mp3-converter/). Você cola as URLs das playlists numa janela, a ferramenta extrai os vídeos com o `yt-dlp` e envia cada um ao MediaHuman pela linha de comando (`YouTubeToMP3 <url>`), do mesmo jeito que o app recebe links abertos de fora.

A ferramenta não inicia downloads: apenas adiciona os vídeos à lista do app. Não controla mouse nem teclado, então funciona em qualquer sessão (Wayland ou X11) e você pode continuar usando o computador durante a importação.

Suporte atual: **Ubuntu**.

## Instalação

```bash
git clone https://github.com/NelioGouvea/mediahuman-batch.git
cd mediahuman-batch
./install.sh
```

O instalador pede a senha do `sudo` e:

- instala os pacotes do sistema (`python3-venv`, `python3-tk`, `wget`);
- cria o ambiente Python em `.venv/` e instala o `yt-dlp`;
- baixa e instala o MediaHuman YouTube to MP3, se ainda não estiver instalado;
- cria o atalho **MediaHuman Batch** no menu de aplicativos;
- abre o MediaHuman Batch pela primeira vez.

Se o MediaHuman não for instalado automaticamente, baixe o `.deb` na [página oficial](https://www.mediahuman.com/youtube-to-mp3-converter/) e instale com:

```bash
sudo apt install ./YouTubeToMP3.amd64.deb
```

## Uso

1. Abra **MediaHuman Batch** no menu (ou rode `./run.sh`).
2. Cole uma ou mais URLs de playlists, uma por linha.
3. Clique em **Importar**.

Se o MediaHuman estiver fechado, a ferramenta o abre e espera alguns segundos antes de enviar as URLs.

Os vídeos extraídos vão para o arquivo `lista.txt`, que funciona como fila: cada URL sai do arquivo assim que é enviada ao MediaHuman. Se a importação for interrompida (por exemplo, fechando a janela), as URLs restantes continuam em `lista.txt` e são enviadas no próximo **Importar**, mesmo com o campo vazio.

URLs de vídeos avulsos também funcionam. Vídeos privados e removidos das playlists são ignorados.

## Problemas comuns

| Problema | Solução |
| :---- | :---- |
| "MediaHuman YouTube to MP3 não está instalado" | Instale o `.deb` da página oficial (veja [Instalação](#instalação)). |
| Os primeiros vídeos não aparecem quando o MediaHuman estava fechado | O app demorou para abrir. Aumente `APP_STARTUP_DELAY` em `app/config.py` ou abra o MediaHuman antes de importar. |
| "Falha ao ler" uma playlist | Confira se a playlist é pública. Se for, atualize o `yt-dlp`: `.venv/bin/pip install -U yt-dlp`. |

## Estrutura

```
app/
├── __init__.py      pacote Python
├── __main__.py      ponto de entrada
├── config.py        caminhos e tempos
├── gui.py           janela principal (Tkinter)
├── playlist.py      extração das URLs com yt-dlp
├── url_queue.py     fila persistida em lista.txt
└── mediahuman.py    abre o MediaHuman e envia as URLs
install.sh           instalador
run.sh               inicia a ferramenta
requirements.txt     dependências Python
```

## Uso responsável

Baixar conteúdo do YouTube fora dos meios oficiais vai contra os Termos de Serviço da plataforma. Use apenas com conteúdo próprio, em domínio público, sob licença livre ou com autorização do detentor dos direitos.
