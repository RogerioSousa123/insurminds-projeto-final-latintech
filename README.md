# InsurMinds — Plataforma Inteligente para Análise e Comparação de Apólices D&O

Protótipo acadêmico que lê apólices D&O em PDF ou imagem, organiza 26 critérios relevantes, compara documentos e responde perguntas com rastreabilidade por página e trecho.

O projeto foi desenvolvido pelo grupo **LatinTech** para o Projeto Final do módulo avançado do Instituto de Inteligência Artificial Aplicada (I2A2). Seu objetivo é apoiar o trabalho de especialistas, não substituir análise jurídica, atuarial, de subscrição ou corretagem.

**Aplicação:** [latintech.latin-re.com](https://latintech.latin-re.com)<br>
**Repositório:** [github.com/RogerioSousa123/insurminds-projeto-final-latintech](https://github.com/RogerioSousa123/insurminds-projeto-final-latintech)

## Principais funcionalidades

- upload de múltiplos PDFs e imagens;
- extração de texto nativo com PyMuPDF;
- OCR local com Tesseract para páginas digitalizadas;
- identificação e estruturação de cláusulas por IA generativa;
- validação de cada evidência contra o texto da página indicada;
- armazenamento local em SQLite;
- comparação determinística de até quatro apólices;
- resumo executivo gerado por IA;
- copiloto de perguntas e respostas fundamentado nas evidências;
- exportação da comparação em JSON, CSV e PDF;
- cache por hash para evitar processamento e custo duplicados;
- modo de demonstração offline para navegação da interface.

## Arquitetura

```text
PDF/Imagem
   │
   ▼
Ingestão e validação ──► hash/cache
   │
   ▼
PyMuPDF + Tesseract ──► texto identificado por página
   │
   ▼
Agente Extrator ──► Validador de evidências ──► Pydantic ──► SQLite
                                                    │
                         ┌──────────────────────────┴───────────────────────┐
                         ▼                                                  ▼
               Comparador determinístico                        Recuperação lexical
                         │                                                  │
                         ▼                                                  ▼
                  Analista por IA                                   Copiloto por IA
                         │                                                  │
                         └──────────────► Interface Streamlit ◄─────────────┘
```

A IA é utilizada onde existe linguagem jurídica e ambiguidade. Valores, estados, datas, diferenças e armazenamento são tratados por código tradicional. Consulte [a arquitetura detalhada](docs/ARQUITETURA.md).

## Requisitos

- Python 3.11 ou superior;
- acesso à API da Anthropic ou OpenAI;
- Tesseract OCR para PDFs digitalizados e imagens;
- Windows, Linux ou macOS.

O Tesseract é opcional para PDFs que já possuem camada de texto. No Windows, instale o executável e, se ele não estiver no `PATH`, informe seu caminho em `TESSERACT_CMD`.

## Instalação

No PowerShell:

```powershell
git clone https://github.com/RogerioSousa123/insurminds-projeto-final-latintech.git
cd insurminds-projeto-final-latintech
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

No Linux ou macOS:

```bash
git clone https://github.com/RogerioSousa123/insurminds-projeto-final-latintech.git
cd insurminds-projeto-final-latintech
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Configuração da IA

### Anthropic

```dotenv
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sua_chave
# Preencha se a API informar que a chave não está vinculada a um workspace:
ANTHROPIC_WORKSPACE_ID=wrkspc_...
ANTHROPIC_MODEL=modelo_disponivel_na_sua_conta
```

### OpenAI

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=modelo_disponivel_na_sua_conta
```

Os nomes dos modelos mudam ao longo do tempo; use um modelo conversacional disponível em sua conta. A chave fica apenas no arquivo `.env`, que está excluído do Git.

### Modo de demonstração

```dotenv
LLM_PROVIDER=demo
```

O modo demo usa regras locais para permitir navegação sem API. Ele **não é IA generativa** e não deve ser usado como evidência do requisito de IA na apresentação final.

## Execução

```powershell
.\start.ps1
```

Ou diretamente:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Depois, abra `http://localhost:8505`. Em produção, o Caddy publica a aplicação em `https://latintech.latin-re.com`.

Fluxo recomendado:

1. acesse **Documentos** e envie duas apólices;
2. confira campos, avisos e evidências em **Apólices**;
3. selecione os documentos em **Comparação**;
4. exporte o relatório e teste perguntas no **Copiloto**.

## Execução persistente e domínio

O arquivo `ecosystem.config.cjs` mantém a aplicação em `127.0.0.1:8505` pelo PM2:

```powershell
pm2 start ecosystem.config.cjs
pm2 save
```

O Caddyfile versionado em `deployment/Caddyfile` publica a aplicação em `https://latintech.latin-re.com`. O DNS precisa ter um registro `A` chamado `latintech` apontando para o mesmo servidor do domínio principal. Após alterar o Caddyfile ativo, valide e recarregue o Caddy antes da demonstração.

Comandos úteis:

```powershell
pm2 show insurminds
pm2 logs insurminds --lines 100 --nostream
Invoke-WebRequest http://127.0.0.1:8505/_stcore/health -UseBasicParsing
```

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest
```

A suíte possui 14 testes automatizados. Ela cobre parsing e recuperação de respostas JSON, rejeição de evidências inventadas, consolidação de cláusulas, extração de PDF, comparação, citações do copiloto, SQLite e geração do relatório PDF.

## Estrutura do repositório

```text
.
├── app.py
├── src/insurminds/
│   ├── domain/          # modelos e taxonomia D&O
│   ├── llm/             # adaptadores de IA conversacional
│   ├── services/        # OCR, extração, comparação, chat e relatórios
│   └── storage/         # persistência SQLite
├── tests/               # testes automatizados
├── examples/            # apólices sintéticas, sem dados reais
├── scripts/             # geração dos artefatos acadêmicos
├── docs/                # relatório, arquitetura, testes e roteiro
└── Projeto_Final_Artefatos/
    ├── InsurMinds_Projeto_Final.pptx
    ├── InsurMinds_Relatorio_Tecnico.pdf
    ├── InsurMinds_Projeto_Final_Codigo.zip
    ├── InsurMinds_Projeto_Final.mp4      # incluído após a gravação
    └── ROTEIRO_VIDEO.md
```

O vídeo final deve ser gravado como `Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4` após a validação com a chave de IA e os documentos escolhidos pelo grupo.

## Segurança, privacidade e confiabilidade

- arquivos são processados em memória; somente texto estruturado e evidências ficam no SQLite local;
- nenhuma credencial é gravada no banco ou versionada;
- o nome do arquivo é sanitizado antes do uso;
- PDFs protegidos por senha são rejeitados;
- documentos são tratados como conteúdo não confiável nos prompts;
- campos sem trecho verificável são descartados;
- “não localizado” nunca significa automaticamente “não coberto”;
- a interface mostra avisos e exige validação humana.

Para o MVP acadêmico, documentos enviados ao provedor de IA devem ser públicos, sintéticos ou previamente autorizados. Consulte a política de retenção do provedor escolhido antes de processar documentos confidenciais.

## Limitações conhecidas

- qualidade do OCR depende da resolução e da instalação do pacote de idioma português;
- layouts complexos, tabelas e apólices extensas podem exigir revisão manual;
- a validação confirma aderência textual, não validade jurídica da interpretação;
- recuperação do copiloto é lexical, sem banco vetorial;
- não há autenticação, controle de perfis ou infraestrutura de alta disponibilidade;
- valores em moedas e redações muito diferentes podem exigir normalização adicional.

## Integrantes

**Grupo: LatinTech**

- Fábio Castro
- Lucas Godois
- Pedro Campos
- Rogério Sousa
- Fernando Gonçalves

## Artefatos e documentação

- [Relatório técnico em Markdown](docs/RELATORIO_TECNICO.md)
- [Arquitetura detalhada](docs/ARQUITETURA.md)
- [Dicionário de dados](docs/DICIONARIO_DADOS.md)
- [Plano de testes](docs/PLANO_TESTES.md)
- [Roteiro do vídeo de cinco minutos](docs/ROTEIRO_VIDEO.md)

## Licença

Distribuído sob a [Licença MIT](LICENSE).
