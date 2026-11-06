# MediaHuman Batch

Importa playlists do YouTube para a fila do [MediaHuman YouTube to MP3](https://www.mediahuman.com/youtube-to-mp3-converter/). Você cola as URLs das playlists numa janela, a ferramenta extrai os vídeos com o `yt-dlp` e envia cada um ao MediaHuman pela linha de comando (`YouTubeToMP3 <url>`), do mesmo jeito que o app recebe links abertos de fora.

A ferramenta não inicia downloads: apenas adiciona os vídeos à lista do app. Não controla mouse nem teclado, então funciona em qualquer sessão (Wayland ou X11) e você pode continuar usando o computador durante a importação.

Suporte atual: **Ubuntu** e **Windows 10/11 (64 bits)**.

## Instalação no Windows

1. Baixe o arquivo `MediaHumanBatch.exe` na página de [Releases](https://github.com/NelioGouvea/mediahuman-batch/releases/latest).
2. Dê dois cliques no arquivo. Não é preciso instalar: o programa abre direto.

Na primeira vez, o Windows pode mostrar "O Windows protegeu o computador", porque o executável não tem assinatura digital. Clique em **Mais informações** e depois em **Executar assim mesmo**.

Se o MediaHuman YouTube to MP3 não estiver instalado, a janela oferece instalá-lo e pede permissão de administrador.

Para ter um atalho, clique com o botão direito no `MediaHumanBatch.exe` e escolha **Fixar em Iniciar** ou **Fixar na barra de tarefas**.

## Instalação no Ubuntu

### Pelo pacote `.deb` (recomendado)

1. Baixe o arquivo `mediahuman-batch_<versão>_all.deb` na página de [Releases](https://github.com/NelioGouvea/mediahuman-batch/releases/latest).
2. Dê dois cliques no arquivo e clique em **Instalar**, ou rode no terminal, na pasta do download:

```bash
sudo apt install ./mediahuman-batch_*_all.deb
```

Se aparecer a nota "O download é executado sem isolamento e como root", pode ignorar: o `apt` só avisa que leu o arquivo direto da sua pasta pessoal.

A instalação precisa de internet para baixar o `yt-dlp`. Depois, abra **MediaHuman Batch** no menu de aplicativos. Se o MediaHuman YouTube to MP3 não estiver instalado, a janela oferece instalá-lo e pede a senha de administrador.

Para desinstalar:

```bash
sudo apt remove mediahuman-batch
```

### Pelo código-fonte

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

1. Abra **MediaHuman Batch** no menu (no Ubuntu) ou o `MediaHumanBatch.exe` (no Windows).
2. Cole uma ou mais URLs de playlists, uma por linha.
3. Clique em **Importar** e espere o log mostrar **Concluído.**
4. No MediaHuman YouTube to MP3, clique em **Iniciar todos**, no canto superior direito, para baixar os vídeos.

Se o MediaHuman estiver fechado, a ferramenta o abre e espera alguns segundos antes de enviar as URLs.

Os vídeos extraídos vão para o arquivo `lista.txt`, que funciona como fila. Ele fica em `~/.local/share/mediahuman-batch/` no Ubuntu e em `%APPDATA%\mediahuman-batch\` no Windows. Cada URL sai do arquivo assim que é enviada ao MediaHuman. Se a importação for interrompida (por exemplo, fechando a janela), as URLs restantes continuam na fila e são enviadas no próximo **Importar**, mesmo com o campo vazio.

URLs de vídeos avulsos também funcionam. Vídeos privados e removidos das playlists são ignorados.

## Problemas comuns

| Problema | Solução |
| :---- | :---- |
| "MediaHuman YouTube to MP3 não está instalado" | Feche e abra o MediaHuman Batch para ver a oferta de instalação, ou instale o `.deb` da [página oficial](https://www.mediahuman.com/youtube-to-mp3-converter/) com `sudo apt install ./YouTubeToMP3.amd64.deb`. |
| Os primeiros vídeos não aparecem quando o MediaHuman estava fechado | O app demorou para abrir. Abra o MediaHuman antes de importar, ou aumente `APP_STARTUP_DELAY` em `app/config.py`. |
| "Falha ao ler" uma playlist | Confira se a playlist é pública. Se for, atualize o `yt-dlp`: no pacote `.deb`, `sudo dpkg-reconfigure mediahuman-batch`; no código-fonte, `.venv/bin/pip install -U yt-dlp`; no Windows, baixe o `MediaHumanBatch.exe` mais recente. |
| Erro ao abrir depois de atualizar o Ubuntu | Rode `sudo dpkg-reconfigure mediahuman-batch` para recriar o ambiente Python. |
| Antivírus bloqueia o `MediaHumanBatch.exe` | É um falso positivo comum em executáveis gerados com PyInstaller sem assinatura. Libere o arquivo no antivírus. |

## Gerar o executável do Windows

O executável é gerado automaticamente pelo GitHub Actions (workflow `Windows`) a cada push: ele fica disponível como artefato **MediaHumanBatch** na execução do workflow. Quando um release é publicado, o workflow anexa o `MediaHumanBatch.exe` a ele.

Para gerar num computador com Windows e Python 3.10+:

```powershell
.\build-exe.ps1
```

O executável é gerado em `dist\MediaHumanBatch.exe`, com o Python e o `yt-dlp` embutidos.

## Gerar o pacote `.deb`

```bash
./build-deb.sh 1.0.0
```

O pacote é gerado em `dist/mediahuman-batch_1.0.0_all.deb`. Ele instala a ferramenta em `/opt/mediahuman-batch`, o comando `mediahuman-batch` e o atalho no menu. O ambiente Python com o `yt-dlp` é criado durante a instalação.

## Estrutura

```
app/
├── __init__.py      pacote Python
├── __main__.py      ponto de entrada
├── config.py        caminhos e tempos
├── gui.py           janela principal (Tkinter)
├── playlist.py      extração das URLs com yt-dlp
├── url_queue.py     fila persistida em lista.txt
├── mediahuman.py    instala e abre o MediaHuman e envia as URLs
├── linux.py         localiza, detecta e instala o MediaHuman no Ubuntu
└── windows.py       localiza, detecta e instala o MediaHuman no Windows
.github/workflows/
└── windows.yml      gera o MediaHumanBatch.exe no GitHub Actions
packaging/
├── control          metadados do pacote .deb
├── postinst         cria o ambiente Python na instalação
├── postrm           remove o ambiente Python na desinstalação
├── mediahuman-batch          comando que abre a ferramenta
└── mediahuman-batch.desktop  atalho do menu
build-deb.sh         gera o pacote .deb
build-exe.ps1        gera o executável do Windows
install.sh           instalador a partir do código-fonte
run.sh               inicia a ferramenta a partir do código-fonte
requirements.txt     dependências Python
```

## Uso responsável

Baixar conteúdo do YouTube fora dos meios oficiais vai contra os Termos de Serviço da plataforma. Use apenas com conteúdo próprio, em domínio público, sob licença livre ou com autorização do detentor dos direitos.
