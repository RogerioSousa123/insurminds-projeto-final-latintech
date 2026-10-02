# Arquitetura da solução

## Visão geral

A InsurMinds adota uma arquitetura modular em camadas. O Streamlit coordena a experiência do usuário, mas regras de negócio, fornecedores de IA e persistência permanecem separados. Isso permite trocar interface, modelo ou banco sem reescrever o domínio.

## Componentes

| Componente | Responsabilidade | Entrada | Saída |
|---|---|---|---|
| Ingestão | Validar extensão, tamanho, senha, páginas e hash | bytes do arquivo | documento validado |
| Leitor | Extrair texto preservando a página | PDF ou imagem | páginas de texto |
| OCR | Ler páginas sem camada textual | imagem rasterizada | texto por página |
| Extrator IA | Identificar somente campos da taxonomia | lotes de páginas | itens JSON candidatos |
| Validador | Confirmar página, trecho e chave permitida | candidatos da IA | campos confiáveis |
| Repositório | Persistir análises e comparações | modelos Pydantic | SQLite |
| Comparador | Comparar estados e valores normalizados | duas a quatro análises | matriz de diferenças |
| Analista IA | Explicar diferenças estruturadas | matriz reduzida | resumo executivo |
| Recuperador | Selecionar evidências relevantes | pergunta | contexto fundamentado |
| Copiloto IA | Responder com citações | pergunta + contexto | resposta textual |
| Relator | Gerar documento auditável | comparação | PDF, CSV e JSON |

## Agentes especializados

Os agentes são papéis lógicos implementados como módulos Python com prompts e contratos distintos. Essa escolha evita a complexidade de um framework agentic para um fluxo majoritariamente determinístico.

1. **Agente Leitor:** transforma o arquivo em páginas textuais.
2. **Agente Extrator:** identifica cláusulas usando uma taxonomia fechada.
3. **Agente Auditor:** rejeita evidências cuja página ou texto não possa ser confirmado.
4. **Agente Comparador:** recebe apenas dados já validados e interpreta diferenças.
5. **Agente Relator:** converte a comparação em comunicação executiva.
6. **Agente Copiloto:** responde perguntas usando contexto recuperado.

## Decisões arquiteturais

### Texto por página

O texto não é concatenado sem metadados. Cada página permanece identificada durante todo o processamento para permitir auditoria.

### Taxonomia fechada

O modelo só pode devolver uma das 26 chaves definidas. Campos desconhecidos são descartados, reduzindo deriva de formato e facilitando comparação.

### Evidência antes da persistência

Um campo identificado pela IA somente é aceito se contiver trecho e página válidos. Uma verificação lexical compara o trecho à página original; baixa aderência reduz confiança ou elimina o candidato.

### Separação entre fato e interpretação

O comparador em Python detecta diferenças. A IA apenas explica os dados fornecidos. Isso reduz custo, aumenta repetibilidade e evita delegar operações objetivas ao modelo.

### Provedor substituível

Uma interface comum permite Anthropic, OpenAI ou modo demo. O provedor e o modelo são configurações de ambiente.

### Persistência local

SQLite é suficiente para o volume e a finalidade didática. O JSON completo preserva a evolução do esquema sem introduzir uma estrutura relacional prematura.

## Fluxo de processamento

1. arquivo recebido em memória;
2. validação de tipo, tamanho, senha e quantidade de páginas;
3. cálculo SHA-256 e consulta ao cache;
4. extração nativa; páginas pobres em texto seguem para OCR;
5. agrupamento de páginas respeitando limite de caracteres;
6. chamada conversacional à IA para cada lote;
7. parsing, validação da taxonomia e confirmação das evidências;
8. consolidação de duplicidades e marcação de ambiguidades;
9. preenchimento explícito de campos não localizados;
10. persistência local e exibição ao usuário;
11. comparação determinística e interpretação opcional por IA;
12. consulta fundamentada ou exportação do relatório.

## Controles de falha

- cache por hash e modelo;
- até três tentativas para falhas transitórias do SDK;
- uma tentativa de reparação de JSON malformado;
- limite de 50 MB e quantidade configurável de páginas;
- avisos específicos para OCR indisponível e páginas vazias;
- transações curtas, WAL e chaves primárias no SQLite;
- fallback determinístico para resumo quando a IA não é usada;
- exportação dos dados em formatos independentes da interface.

## Ameaças consideradas

| Risco | Mitigação do MVP |
|---|---|
| Prompt injection no documento | prompts declaram documento como dado não confiável |
| Alucinação de fonte | validação do trecho contra a página |
| Vazamento de chave | `.env` ignorado pelo Git e chave fora do banco |
| Confusão semântica | estados separados: encontrado, ambíguo e não localizado |
| Custo duplicado | cache SHA-256 por modelo e versão de prompt |
| Indisponibilidade da API | dados persistidos, comparador local e modo demo identificado |
| Decisão automatizada indevida | ressalvas e validação humana obrigatória |

