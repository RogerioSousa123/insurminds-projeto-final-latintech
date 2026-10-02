# Roteiro do vídeo — máximo de 5 minutos

Nome obrigatório do arquivo final: `InsurMinds_Projeto_Final.mp4`.

## 0:00–0:35 — Problema

“Apólices D&O são documentos extensos e jurídicos. Comparar limites, franquias, coberturas e exclusões exige horas e ainda traz risco de deixar passar uma diferença importante. A InsurMinds organiza esse processo sem retirar o especialista da decisão.”

Mostrar o slide do problema e rapidamente duas apólices.

## 0:35–1:05 — Proposta

“Nossa plataforma recebe PDF ou imagem, extrai texto, utiliza IA generativa para identificar cláusulas, valida as evidências e apresenta uma comparação rastreável. Toda conclusão pode ser conferida na página de origem.”

Mostrar o slide de proposta e abrir a aplicação.

## 1:05–1:40 — Arquitetura

“O processamento é local até a chamada conversacional à IA. PyMuPDF lê o PDF e Tesseract atende páginas digitalizadas. Agentes especializados extraem, validam, comparam e explicam. Pydantic protege o contrato dos dados e SQLite armazena os resultados.”

Mostrar a aba Arquitetura por poucos segundos.

## 1:40–3:35 — Demonstração

1. Enviar duas apólices previamente testadas.
2. Mostrar progresso por etapa.
3. Abrir uma análise e destacar um limite, uma exclusão e suas páginas.
4. Abrir a matriz comparativa.
5. Mostrar quantidade de diferenças e semáforo de atenção.
6. Expandir evidências de uma diferença importante.
7. Fazer uma pergunta curta ao copiloto.
8. Exportar o relatório PDF.

Fala sugerida: “A ausência de evidência aparece como não localizada, nunca como ausência automática de cobertura. Essa distinção reduz conclusões indevidas.”

## 3:35–4:15 — Decisões técnicas

“Não usamos o modelo para tudo. Comparações objetivas são feitas em código; a IA interpreta linguagem. Também validamos se o trecho devolvido realmente existe na página, usamos hash para evitar custo duplicado e escondemos as chaves em variáveis de ambiente.”

## 4:15–4:45 — Resultados e limitações

“O MVP analisa 26 critérios, compara até quatro apólices e exporta dados auditáveis. Ainda há limitações de OCR e interpretação jurídica. Por isso, a decisão permanece humana.”

## 4:45–5:00 — Encerramento

“A InsurMinds transforma documentos complexos em informação comparável, explicável e verificável. Este é um protótipo acadêmico preparado para evoluir com novos produtos, taxonomias e avaliações.”

## Checklist de gravação

- [ ] duração entre 4:20 e 4:50;
- [ ] resolução mínima 1920×1080;
- [ ] zoom do navegador entre 90% e 110%;
- [ ] notificações e dados pessoais ocultos;
- [ ] chave da API nunca exibida;
- [ ] documentos e perguntas já testados;
- [ ] análises mantidas no cache como contingência;
- [ ] áudio inteligível e cursor sem movimentos excessivos;
- [ ] arquivo exportado e reproduzido antes da entrega.

