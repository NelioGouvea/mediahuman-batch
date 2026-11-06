# MediaHuman Batch

Importa playlists do YouTube para a fila do [MediaHuman YouTube to MP3](https://www.mediahuman.com/youtube-to-mp3-converter/). Você cola as URLs das playlists numa janela, a ferramenta extrai os vídeos com o `yt-dlp` e cola cada um no MediaHuman clicando no botão **"Colar endereço"**.

A ferramenta não inicia downloads: apenas adiciona os vídeos à lista do app.

Suporte atual: **Ubuntu em sessão X11**.

## Instalação

```bash
git clone https://github.com/NelioGouvea/mediahuman-batch.git
cd mediahuman-batch
./install.sh
```

O instalador pede a senha do `sudo` e:

- instala os pacotes do sistema (`python3-venv`, `python3-tk`, `python3-dev`, `xclip`, `xdotool`, `gnome-screenshot`, `wget`);
- cria o ambiente Python em `.venv/` e instala as dependências;
- baixa e instala o MediaHuman YouTube to MP3, se ainda não estiver instalado;
- cria o atalho **MediaHuman Batch** no menu de aplicativos;
- avisa se a sessão atual não for X11.

Se o MediaHuman não for instalado automaticamente, baixe o `.deb` na [página oficial](https://www.mediahuman.com/youtube-to-mp3-converter/) e instale com:

```bash
sudo apt install ./YouTubeToMP3.amd64.deb
```

## Sessão X11

A automação controla o mouse e captura a tela, o que não funciona no Wayland. Para conferir a sessão atual:

```bash
echo $XDG_SESSION_TYPE
```

Se aparecer `wayland`:

- **Ubuntu até 25.04:** saia da sessão e, na tela de login, clique na engrenagem e escolha **Ubuntu on Xorg**.
- **Ubuntu 25.10 ou mais novo:** a sessão Xorg do GNOME foi removida. Instale o Xfce e escolha **Xfce Session** na tela de login:

```bash
sudo apt install xfce4
```

## Primeiro uso

Os recortes de tela dependem de tema, fonte e escala, por isso cada máquina precisa calibrar os seus. Eles ficam em `assets/`.

### 1. Calibrar o botão (obrigatório)

1. Abra **MediaHuman Batch** e clique em **Calibrar botão**.
2. Confirme. O MediaHuman abre e a janela da ferramenta é minimizada.
3. Deixe o mouse parado sobre o botão **"Colar endereço"** por 5 segundos.
4. O recorte é salvo em `assets/colar_endereco.png`.

### 2. Calibrar o carregamento (opcional, recomendado)

Sem essa calibração, a ferramenta espera um tempo fixo entre as URLs (campo **Espera fixa**). Com ela, espera o MediaHuman terminar de carregar cada vídeo.

1. Copie a URL de um vídeo qualquer.
2. Clique em **Calibrar carregamento** e confirme.
3. Em até 10 segundos, cole a URL no MediaHuman e deixe o mouse parado sobre o texto exibido durante o carregamento.
4. O recorte é salvo em `assets/carregando.png`.

## Uso

1. Abra **MediaHuman Batch** no menu (ou rode `./run.sh`).
2. Cole uma ou mais URLs de playlists, uma por linha.
3. Clique em **Importar**.
4. A janela é minimizada enquanto as URLs são coladas. **Não use mouse nem teclado** até ela voltar.

Os vídeos extraídos vão para o arquivo `lista.txt`, que funciona como fila: cada URL sai do arquivo assim que termina de carregar no MediaHuman.

Para interromper, mova o mouse para um canto da tela. As URLs que ainda não foram coladas continuam em `lista.txt` e são processadas no próximo **Importar**, mesmo com o campo vazio.

URLs de vídeos avulsos também funcionam. Vídeos privados e removidos das playlists são ignorados.

## Problemas comuns

| Problema | Solução |
| :---- | :---- |
| Botão "Colar endereço" não encontrado | Clique em **Calibrar botão** de novo. |
| Vídeos se sobrescrevendo no MediaHuman | Aumente a **Espera fixa** ou faça a calibração do carregamento. |
| Vídeos duplicados no MediaHuman | Nas preferências do MediaHuman, desative a opção de adicionar automaticamente a partir da área de transferência. |
| Janela do MediaHuman não encontrada | Ajuste `APP_WINDOW_NAME` em `app/config.py` com o título real da janela. |
| Aviso de sessão ao abrir | Veja a seção [Sessão X11](#sessão-x11). |

## Estrutura

```
app/
├── __init__.py      pacote Python
├── __main__.py      ponto de entrada e verificação da sessão
├── config.py        caminhos, tempos e nome da janela
├── gui.py           janela principal (Tkinter)
├── playlist.py      extração das URLs com yt-dlp
├── url_queue.py     fila persistida em lista.txt
└── automation.py    controle do MediaHuman, mouse e calibração
assets/              recortes de tela gerados na calibração
install.sh           instalador
run.sh               inicia a ferramenta
requirements.txt     dependências Python
```

## Uso responsável

Baixar conteúdo do YouTube fora dos meios oficiais vai contra os Termos de Serviço da plataforma. Use apenas com conteúdo próprio, em domínio público, sob licença livre ou com autorização do detentor dos direitos.
