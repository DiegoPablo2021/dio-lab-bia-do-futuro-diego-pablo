# Pitch (3 minutos)

## Versão pronta para falar

### 0:00 a 0:30 - Problema
Hoje, muita gente quer organizar melhor a vida financeira, mas trava em conceitos básicos, leitura de gastos e escolha do que realmente importa no dia a dia.

O problema não é só falta de conteúdo. Conteúdo existe. O problema é que quase nunca esse conteúdo vem com contexto, linguagem acessível e segurança.

Foi pensando nisso que eu criei a Aura, uma mentora de saúde financeira com inteligência artificial.

### 0:30 a 1:10 - Solução
A Aura foi desenhada para atuar como uma mentora digital educativa.

Ela analisa dados financeiros, explica conceitos como Selic e Tesouro Selic, ajuda a interpretar gastos, contextualiza a reserva de emergência e sugere próximos passos de forma responsável.

O ponto mais importante é que ela não recomenda investimentos de forma direta, não inventa dados e trabalha com guardrails para manter coerência, segurança e rastreabilidade.

### 1:10 a 2:10 - Demonstração
Aqui no app, eu tenho dois modos.

O primeiro é a demonstração guiada, que usa um cenário consistente para apresentar o desafio.

O segundo é o agente livre, onde eu posso personalizar o nome da pessoa, renda mensal, objetivo principal, reserva atual e perfil investidor.

Isso permite demonstrar injeção de contexto dinâmico.

Por exemplo, se eu usar um perfil conservador, a Aura responde de forma mais didática, prudente e focada em segurança e liquidez.

Se eu trocar para um perfil arrojado, ela passa a responder com mais profundidade sobre risco, volatilidade e horizonte de longo prazo.

Além disso, eu posso testar perguntas de negócio, como:

- Onde estou gastando mais?
- Como está minha reserva de emergência?
- O que é Selic?

E também perguntas fora do escopo, como clima ou futebol, para mostrar que os guardrails funcionam corretamente.

### 2:10 a 2:45 - Diferenciais
Os principais diferenciais do projeto são:

- interface com cara de produto, e não só de protótipo técnico;
- integração com Gemini API e fallback local;
- uso de dados da DIO enriquecidos com fontes oficiais do Banco Central e do Tesouro Direto;
- documentação completa de agente, base de conhecimento, prompts, métricas, evidências e pitch;
- testes automatizados e estrutura organizada para portfólio.

### 2:45 a 3:00 - Fechamento
A Aura não foi pensada apenas para responder perguntas.

Ela foi pensada para demonstrar arquitetura, engenharia de prompt, segurança, UX e capacidade de transformar dados em uma experiência útil e explicável.

Esse projeto representa a forma como eu gosto de construir soluções: com clareza técnica, contexto de negócio e foco real em quem vai usar.

## Versão resumida em tópicos

### Problema
- pessoas iniciantes em finanças têm dificuldade para interpretar gastos, taxas e produtos;
- chatbots genéricos costumam responder sem contexto ou com risco de alucinação.

### Solução
- Aura, uma mentora de saúde financeira com IA;
- educativa, segura, contextualizada e sem recomendação direta de investimento.

### Demonstração sugerida
1. mostrar a tela inicial;
2. usar `Demonstração guiada`;
3. perguntar `Onde estou gastando mais?`;
4. perguntar `Como está minha reserva de emergência?`;
5. perguntar `O que é Selic?`;
6. testar uma pergunta fora do escopo;
7. trocar para `Agente livre` e mostrar a diferença entre personas.

### Diferencial
- contexto dinâmico por nome, renda, objetivo e perfil investidor;
- duas experiências no mesmo app;
- guardrails + fontes oficiais + testes + documentação.