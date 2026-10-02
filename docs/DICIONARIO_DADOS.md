# Dicionário de dados

## Entidades principais

### DocumentInfo

| Campo | Tipo | Descrição |
|---|---|---|
| id | string | prefixo do SHA-256 do arquivo |
| filename | string | nome sanitizado |
| sha256 | string | hash completo para cache e integridade |
| mime_type | string | tipo de mídia detectado |
| page_count | inteiro | quantidade de páginas |
| character_count | inteiro | caracteres extraídos |
| ocr_pages | lista de inteiros | páginas tratadas por OCR |

### ExtractedField

| Campo | Tipo | Descrição |
|---|---|---|
| key | string | identificador estável da taxonomia |
| label | string | nome apresentado ao usuário |
| category | string | agrupamento funcional |
| status | enum | encontrado, não localizado, ambíguo ou não aplicável |
| value_text | string/nulo | valor legível preservado |
| normalized_value | qualquer/nulo | forma adequada à comparação |
| unit | string/nulo | moeda, meses, percentual etc. |
| summary | string/nulo | síntese factual da condição |
| evidences | lista | páginas, trechos e confiança |
| confidence | decimal | confiança entre zero e um |

### PolicyAnalysis

Contém o documento, os 26 campos, avisos, modelo, versão de prompt, consumo de tokens, duração e data.

### ComparisonResult

Contém os IDs comparados, uma linha por critério, resumo executivo, ressalvas, modelo responsável e data.

## Estados semânticos

- **encontrado:** existe evidência suficiente para registrar o campo;
- **não localizado:** a análise não encontrou evidência suficiente;
- **ambíguo:** existem valores conflitantes ou redação sem conclusão segura;
- **não aplicável:** reservado para condições explicitamente inaplicáveis.

“Não localizado” nunca deve ser exibido ou interpretado como “não coberto”.

## Taxonomia D&O

A taxonomia atual possui 26 critérios em identificação, condições gerais, limites e franquias, coberturas, exclusões, temporalidade, jurisdição e eventos societários. A fonte canônica está em `src/insurminds/domain/taxonomy.py`.

