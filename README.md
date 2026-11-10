# 🎬 AI Cloud Documentary Production Engine

Um sistema autônomo na nuvem (executado via **GitHub Actions** sem custos de servidor) para gerar documentários longos em inglês, com **voz neural estilo BBC/History Channel**, **acervos históricos de domínio público em altíssima resolução** e **sincronização milimétrica entre voz e imagem**.

---

## 🌟 Funcionalidades

- **100% Gratuito & Na Nuvem:** Roda inteiramente dentro do GitHub Actions. Se o repositório for público, as horas de execução no Linux são ilimitadas (até 6 horas contínuas por vídeo!).
- **Roteirização Cinematográfica:** Utiliza a API do Google Gemini com saída estruturada (cenas, narração, termos precisos de acervo e sugestões de movimento de câmera).
- **Voz Neural Ultra-Realista:** Locuções em inglês com Microsoft Edge Neural (`en-US-ChristopherNeural`, `en-US-BrianNeural`, etc.) sem custo e sem limite de caracteres.
- **Sincronia Milimétrica (Voice-First Timeline):** O tempo de cada cena é determinado exatamente pela duração do áudio da voz em milissegundos. A imagem se adapta à fala, nunca o contrário.
- **Mineração Automática de Acervos:** Busca inteligente no **Wikimedia Commons** (milhões de pinturas, manuscritos, mapas, bustos e fotos históricas em 4K/Full HD) e opcionalmente **Pexels/Pixabay**.
- **Efeito Ken Burns Cinematográfico:** Panorâmicas e zooms lentos suaves em fotos de arquivo via FFmpeg, eliminando a sensação estática de imagens paradas.
- **Mixagem de Áudio & Auto-Ducking:** Suporte a trilha sonora ambiente com redução de volume automática durante as falas do narrador.

---

## 🚀 Como Usar no Novo GitHub

### Passo 1: Criar o Repositório no GitHub
1. Crie uma nova conta ou use seu novo perfil do GitHub.
2. Crie um novo repositório (ex: `ai-documentary-engine`).
   > **Dica de Custo:** Repositórios **Públicos** têm minutos ilimitados de GitHub Actions para runners padrão. Se preferir privado, você tem 2.000 minutos/mês grátis.
3. Suba os arquivos deste projeto para o repositório.

### Passo 2: Configurar os Segredos (GitHub Secrets)
No seu repositório no GitHub:
1. Vá em **Settings** > **Secrets and variables** > **Actions**.
2. Clique em **New repository secret**.
3. Adicione:
   - `GEMINI_API_KEY`: Sua chave da Gemini API.
   - `PEXELS_API_KEY`: (Opcional) Chave gratuita do Pexels para B-roll moderno.
   - `PIXABAY_API_KEY`: (Opcional) Chave gratuita do Pixabay.

### Passo 3: Gerar Documentários com 1 Clique
1. Vá na aba **Actions** do seu repositório.
2. Selecione o workflow **Generate AI Documentary**.
3. Clique em **Run workflow**.
4. Preencha os campos:
   - **Topic:** Ex: `The Secrets of the Library of Alexandria` ou `The Rise and Fall of the Roman Empire`.
   - **Scenes:** Quantidade de cenas (ex: `5` para teste rápido, `15` para médio, `30+` para documentário longo).
   - **Voice:** Escolha a voz do narrador (ex: `en-US-ChristopherNeural` ou `en-US-BrianNeural`).
5. Clique no botão verde **Run workflow**!

O GitHub vai rodar todo o pipeline nos servidores deles e, ao final:
- O vídeo `.mp4` e o roteiro ficam disponíveis nos **Artifacts** e em **Releases** para download direto!

---

## 🛠️ Execução Local (Opcional)

Se quiser rodar localmente no seu computador:
```bash
# Com uv (recomendado):
uv run python main.py --topic "The Pyramids of Giza" --scenes 3

# Ou com pip tradicional:
pip install -r requirements.txt
python main.py --topic "The Pyramids of Giza" --scenes 3
```
