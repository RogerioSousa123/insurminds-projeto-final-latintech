# Roteiro pronto para gravação — máximo de 5 minutos

**Arquivo final:** `InsurMinds_Projeto_Final.mp4`<br>
**Grupo:** LatinTech<br>
**Duração planejada:** aproximadamente 4 minutos e 40 segundos.

## Preparação antes de gravar

1. Abra o roteiro em uma segunda tela.
2. Abra o slide inicial do Pitch Deck e a aplicação em `https://latintech.latin-re.com`.
3. Deixe separados os arquivos `examples/Apolice_Demo_A.pdf` e `examples/Apolice_Demo_B.pdf`.
4. Processe os dois arquivos uma vez antes da gravação. Assim, o cache evita espera longa durante o vídeo.
5. Na aplicação, deixe selecionadas as duas apólices e teste esta pergunta no Copiloto: “Quais são as principais diferenças de limite, franquia, multas e jurisdição entre as duas apólices?”
6. Feche notificações e qualquer tela que possa mostrar chave de API, e-mail ou dados pessoais.

O texto abaixo pode ser lido como teleprompter. As orientações entre colchetes não devem ser faladas.

## 0:00–0:25 — Abertura

**Mostrar:** primeiro slide do Pitch Deck.

**Falar:**

“Olá. Nós somos o grupo LatinTech e este é o InsurMinds, nosso projeto final para o módulo avançado do I2A2. O InsurMinds é uma plataforma inteligente criada para apoiar a análise e a comparação de apólices de seguro D&O, mantendo o especialista no controle da decisão.”

## 0:25–0:55 — Problema

**Mostrar:** slide do problema, com os três cartões.

**Falar:**

“Apólices D&O são documentos extensos, técnicos e frequentemente redigidos em linguagem jurídica. Informações como limites, franquias, coberturas, exclusões, territorialidade e prazos podem estar espalhadas por várias páginas. A comparação manual consome tempo e ainda pode deixar passar uma diferença importante. Além disso, um resumo sem página e sem trecho de origem é difícil de auditar.”

## 0:55–1:20 — Solução

**Mostrar:** slide da proposta de valor e, em seguida, abrir a aplicação.

**Falar:**

“Nossa solução recebe documentos em PDF ou imagem, extrai o texto, aplica OCR quando necessário e utiliza inteligência artificial generativa para identificar informações relevantes. Os dados são organizados em uma taxonomia de vinte e seis critérios de D&O. Cada informação aceita preserva a página e o trecho que servem como evidência.”

## 1:20–1:55 — Arquitetura

**Mostrar:** aba **Como funciona** da aplicação ou o slide de arquitetura.

**Falar:**

“A arquitetura foi dividida em componentes especializados. O agente leitor valida o arquivo e preserva o texto por página. PyMuPDF atende documentos com camada textual e o Tesseract executa OCR em páginas digitalizadas. O agente extrator conversa com o modelo generativo. Em seguida, o agente auditor valida a taxonomia, a página e a evidência. Os resultados são validados com Pydantic e armazenados em SQLite. A comparação objetiva é feita por código, enquanto a IA é utilizada para explicar diferenças e responder perguntas em linguagem natural.”

## 1:55–2:25 — Entrada e processamento

**Mostrar:** aba **Documentos**. Selecione `Apolice_Demo_A.pdf` e `Apolice_Demo_B.pdf` e clique para processar. Se o cache responder rapidamente, isso é esperado.

**Falar:**

“Na área Documentos podemos enviar uma ou mais apólices. Para esta demonstração usamos dois documentos sintéticos, sem dados reais e sem validade contratual. A interface mostra as etapas do processamento. Também calculamos o hash de cada arquivo; assim, um documento já analisado pode ser recuperado do cache, reduzindo tempo e custo de API.”

## 2:25–2:55 — Análise individual

**Mostrar:** aba **Apólices**. Selecione a Apólice A, mostre as métricas, um limite e expanda sua evidência.

**Falar:**

“Na área Apólices vemos o resultado estruturado. Aqui, por exemplo, encontramos o limite máximo de garantia e podemos abrir a evidência correspondente. A plataforma diferencia informação encontrada, não localizada, ambígua e não aplicável. Portanto, não localizar uma cláusula não significa concluir que a cobertura não existe.”

## 2:55–3:40 — Comparação

**Mostrar:** aba **Comparação**, com as duas apólices selecionadas. Percorra o resumo e a tabela. Destaque limite, franquia e pelo menos uma diferença textual.

**Falar:**

“Na comparação lado a lado, a Apólice A apresenta limite de dez milhões de reais e franquia de cem mil reais. A Apólice B apresenta limite de quinze milhões e franquia de duzentos e cinquenta mil reais. Também existem diferenças relevantes em multas, investigações, retroatividade, território e jurisdição. O sistema reúne o que é comum, o que é diferente e o que precisa de revisão. O semáforo indica atenção para conferência; ele não representa uma recomendação automática de contratação.”

## 3:40–4:10 — Copiloto e exportação

**Mostrar:** aba **Copiloto**. Faça a pergunta previamente testada. Depois volte à comparação e mostre rapidamente os botões de exportação.

**Pergunta:** “Quais são as principais diferenças de limite, franquia, multas e jurisdição entre as duas apólices?”

**Falar:**

“O Copiloto permite fazer perguntas sobre as apólices selecionadas. A resposta utiliza o contexto extraído e apresenta citações por documento e página. Os resultados também podem ser exportados em PDF, CSV e JSON, facilitando revisão, auditoria e reutilização das informações.”

## 4:10–4:35 — Confiabilidade e limitações

**Mostrar:** slide de controles ou permanecer na comparação com as evidências abertas.

**Falar:**

“A confiabilidade não depende somente do prompt. Chaves desconhecidas são rejeitadas, trechos são conferidos contra a página original, respostas JSON malformadas recebem tratamento controlado e as credenciais ficam fora do código. Ainda existem limitações de OCR e interpretação jurídica. Por isso, a solução é assistiva e exige validação profissional.”

## 4:35–4:50 — Encerramento

**Mostrar:** último slide do Pitch Deck.

**Falar:**

“O InsurMinds transforma leitura dispersa em uma comparação estruturada, explicável e verificável. Com isso, demonstramos a integração entre OCR, inteligência artificial generativa, agentes especializados, banco de dados, automação e interface. Obrigado.”

## Plano de contingência

- Se o processamento ao vivo demorar, corte a espera na edição e continue com as análises previamente salvas.
- Se a API estiver indisponível, mostre os resultados persistidos no SQLite e explique que o processamento já foi executado.
- Se o Copiloto demorar, deixe a pergunta previamente respondida e mostre o histórico.
- Não abra o arquivo `.env` e não mostre telas do provedor da API.

## Checklist final da gravação

- [ ] duração menor que 5 minutos;
- [ ] resolução de 1920 × 1080, quando possível;
- [ ] áudio claro e sem ruído excessivo;
- [ ] navegador com zoom entre 90% e 110%;
- [ ] problema, arquitetura, funcionamento e resultados aparecem no vídeo;
- [ ] nomes de arquivos e páginas ficam legíveis;
- [ ] nenhuma credencial ou informação pessoal aparece;
- [ ] MP4 reproduzido do início ao fim após a exportação;
- [ ] arquivo salvo em `Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4`.
