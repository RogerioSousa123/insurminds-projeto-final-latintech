# Plano de testes

## Objetivo

Demonstrar que a plataforma processa documentos, controla respostas da IA, persiste dados e compara apólices sem confundir ausência de evidência com ausência de cobertura.

## Testes automatizados

| Área | Cenário | Resultado esperado |
|---|---|---|
| JSON | resposta pura ou cercada por Markdown | objeto extraído corretamente |
| JSON | lista ou conteúdo inválido | erro controlado |
| Extração | campo permitido com trecho literal | campo aceito |
| Extração | chave inventada pelo modelo | campo descartado e aviso registrado |
| Evidência | trecho inexistente na página | campo descartado |
| Comparação | limites normalizados distintos | diferença e atenção alta |
| Persistência | salvar e recarregar análise | igualdade dos campos principais |
| PDF | documento com camada textual | texto preservado por página |
| Relatório | comparação válida | arquivo iniciado com assinatura `%PDF` |

## Testes manuais antes da entrega

- [ ] processar duas apólices reais ou públicas com a API configurada;
- [ ] conferir manualmente dez campos de cada apólice;
- [ ] confirmar páginas e trechos em pelo menos cinco diferenças;
- [ ] testar PDF textual, PDF digitalizado e uma imagem;
- [ ] testar documento protegido por senha;
- [ ] desligar a internet e demonstrar análises persistidas;
- [ ] exportar JSON, CSV e PDF;
- [ ] perguntar algo presente e algo ausente ao copiloto;
- [ ] conferir que uma pergunta ausente não gera fato inventado;
- [ ] executar a demonstração completa em menos de três minutos;
- [ ] remover chaves e documentos confidenciais antes de publicar.

## Métricas sugeridas

Em uma amostra rotulada manualmente, calcular por campo:

- precisão: proporção dos campos encontrados que estão corretos;
- cobertura: proporção dos campos existentes que foram encontrados;
- acurácia de página: proporção das evidências com página correta;
- taxa de “não localizado” indevido;
- tempo médio e tokens por documento.

Para o MVP, uma planilha com 20 a 30 verificações manuais já demonstra avaliação responsável.

