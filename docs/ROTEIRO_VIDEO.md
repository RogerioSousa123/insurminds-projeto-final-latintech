# Roteiro de gravação com explicações técnicas simples

**Arquivo final:** `InsurMinds_Projeto_Final.mp4`<br>
**Grupo:** LatinTech<br>
**Duração planejada:** entre 4 minutos e 30 segundos e 4 minutos e 50 segundos.

## Preparação

1. Abra este roteiro em uma segunda tela.
2. Na tela que será gravada, abra o Pitch Deck e `https://latintech.latin-re.com`.
3. Separe `examples/Apolice_Demo_A.pdf` e `examples/Apolice_Demo_B.pdf`.
4. Processe os dois arquivos antes da gravação para deixar o cache preparado.
5. Teste no Copiloto: “Quais são as principais diferenças de limite, franquia, multas e jurisdição entre as duas apólices?”
6. Feche notificações e qualquer tela que possa mostrar chave de API ou dados pessoais.

Leia somente os parágrafos marcados como **Falar**. As instruções de tela não devem ser lidas.

## 0:00–0:25 — Abertura

**Mostrar:** slide inicial.

**Falar:**

“Olá. Somos o grupo LatinTech e este é o InsurMinds, nosso projeto final do I2A2. Criamos uma plataforma para apoiar a leitura e a comparação de apólices D&O. D&O é o seguro que protege administradores e executivos diante de reclamações relacionadas às suas decisões de gestão.”

## 0:25–0:55 — Problema

**Mostrar:** slide do problema.

**Falar:**

“Essas apólices são longas e usam linguagem jurídica. Limites, franquias, coberturas, exclusões e prazos podem estar espalhados por várias páginas. A comparação manual exige tempo e pode deixar passar uma diferença importante. Além disso, uma conclusão sem página e sem trecho de origem é difícil de conferir.”

## 0:55–1:35 — As seis etapas da proposta de valor

**Mostrar:** slide **Da leitura dispersa à comparação verificável**. Aponte cada etapa conforme ela for citada e depois abra a aplicação.

**Falar:**

“Nossa proposta possui seis etapas. Primeiro, Enviar: recebemos o PDF ou a imagem. Segundo, Extrair: lemos o conteúdo e usamos OCR nas páginas escaneadas; OCR transforma imagem em texto. Terceiro, Estruturar: a IA generativa interpreta a linguagem e organiza tudo nos vinte e seis critérios da nossa taxonomia, a lista padronizada do que procuramos. Quarto, Validar: conferimos página e trecho. Quinto, Comparar: colocamos os campos lado a lado e destacamos diferenças. Sexto, Consultar: o Copiloto responde usando as evidências. Assim, transformamos documentos em dados comparáveis e verificáveis.”

## 1:35–2:25 — Os seis agentes do projeto

**Mostrar:** slide **Agentes pequenos, especializados e testáveis**. Aponte cada agente conforme ele for citado.

**Falar:**

“Criamos seis agentes especializados. Um agente é um módulo com uma responsabilidade específica, não um robô que decide sozinho. O Agente Leitor valida o arquivo e extrai o texto, usando OCR em páginas que são imagens. O Agente Extrator envia o texto à IA e procura os vinte e seis critérios. O Agente Auditor verifica se a página e o trecho comprovam cada informação. O Agente Comparador confronta as apólices e aponta itens iguais, diferentes ou pendentes. O Agente Relator prepara as exportações. O Agente Copiloto recupera evidências e responde perguntas com citações. Todos trabalham em sequência. O Pydantic valida o formato dos dados, e o SQLite os guarda em um banco local.”

## 2:25–2:50 — Envio e processamento

**Mostrar:** aba **Documentos**. Envie as duas apólices sintéticas e inicie o processamento.

**Falar:**

“Na área Documentos enviamos as apólices. Nesta demonstração usamos arquivos sintéticos, sem informações reais e sem validade contratual. O sistema calcula um hash, que funciona como uma impressão digital do arquivo. Se o mesmo documento já foi analisado, o cache reutiliza o resultado anterior, reduzindo tempo e novas chamadas ao modelo de IA.”

## 2:50–3:10 — Análise individual

**Mostrar:** aba **Apólices**. Selecione a Apólice A e abra a evidência de um limite.

**Falar:**

“Na área Apólices, cada resultado mostra valor, página, trecho e confiança. O sistema separa informação encontrada, não localizada, ambígua e não aplicável. Portanto, não localizar uma cláusula não significa afirmar que a cobertura não existe.”

## 3:10–3:45 — Comparação

**Mostrar:** aba **Comparação**, com as duas apólices selecionadas. Destaque limite, franquia, multas e jurisdição.

**Falar:**

“A comparação objetiva é determinística, ou seja, os mesmos dados sempre produzem o mesmo resultado. A Apólice A tem limite de dez milhões de reais e franquia de cem mil. A Apólice B tem limite de quinze milhões e franquia de duzentos e cinquenta mil. Também encontramos diferenças em multas, investigações, retroatividade, território e jurisdição. O semáforo apenas indica pontos de atenção para revisão humana; ele não recomenda qual apólice contratar.”

## 3:45–4:15 — Copiloto e exportação

**Mostrar:** aba **Copiloto**, faça a pergunta testada e depois mostre os botões de exportação.

**Falar:**

“O Copiloto primeiro recupera os trechos mais relacionados à pergunta e só então pede à IA que redija a resposta. Por isso, ele consegue citar documento e página. O resultado também pode ser exportado em PDF, CSV e JSON. O CSV pode ser aberto como planilha, enquanto o JSON preserva a estrutura completa para uso em outros sistemas.”

## 4:15–4:40 — Confiabilidade e limites

**Mostrar:** evidências ou slide de controles.

**Falar:**

“A confiabilidade não depende apenas do prompt, que é o conjunto de instruções enviado à IA. O sistema confere chaves, páginas e trechos antes de salvar. JSON é o formato de texto usado na resposta estruturada; se ele vier com erro, a aplicação tenta recuperá-lo sem perder os lotes válidos. Mesmo com esses controles, OCR e interpretação jurídica podem falhar. Por isso, a análise é assistiva e precisa de validação profissional.”

## 4:40–4:55 — Encerramento

**Mostrar:** slide final.

**Falar:**

“O InsurMinds transforma documentos complexos em uma comparação estruturada, explicável e verificável. Assim, reunimos OCR, IA generativa, agentes especializados, banco de dados e interface em uma solução funcional, mantendo a decisão final com o especialista. Obrigado.”

## Plano de contingência

- Se o processamento demorar, corte a espera na edição e continue com os resultados previamente salvos.
- Se a API estiver indisponível, mostre as análises persistidas no banco local.
- Se o Copiloto demorar, deixe a pergunta respondida antes e mostre o histórico.
- Nunca abra o arquivo `.env` durante a gravação.

## Checklist final

- [ ] duração inferior a 5 minutos;
- [ ] problema, solução, arquitetura, demonstração e resultados aparecem;
- [ ] áudio claro;
- [ ] textos da aplicação legíveis;
- [ ] nenhuma credencial ou informação pessoal visível;
- [ ] MP4 reproduzido do início ao fim;
- [ ] arquivo salvo como `Projeto_Final_Artefatos/InsurMinds_Projeto_Final.mp4`.
