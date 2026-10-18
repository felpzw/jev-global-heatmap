# Como estender a JEV

A versatilidade demonstrada está na separação entre conceito, dados, regra,
seleção e explicação. A JEV deste repositório é o motor local de afinidade;
não é uma biblioteca externa instalada ou um modelo treinado. Um novo conceito
precisa de uma definição mensurável, com confirmação do usuário.

1. Defina atributo, escopo, unidade, evidências admissíveis e limites. “Praia boa”
   não pode ser implementada apenas renomeando “litoral”. Registre uma ADR se a
   semântica de score ou dados mudar.
2. Publique catálogo e dataset com versões novas, licença, fontes, lacunas e
   transformação reproduzível. Amplie `Attribute` e limites dos contratos quando
   adicionar critérios; a release atual admite somente dois booleanos.
3. Adicione sinônimos e ambiguidades em `input_parser.py`, e a revisão na UI.
   Termos desconhecidos devem continuar visíveis, sem interpretação silenciosa.
4. Critérios booleanos reutilizam o comparador e a média ponderada. Indicadores
   numéricos exigem novos tipos de evidência e uma normalização fixa, com direção,
   unidade e limites definidos; não aplicar min-max do resultado da consulta.
5. Adicione casos anotados separados entre ajuste/teste, inclusive negativas,
   missing, contradição e filtros. Avalie cobertura, falsos descartes e desempates.
6. O adaptador de explicação continua recebendo apenas os selecionados. Amplie
   o payload tipado e templates, sem dar à LLM poder de alterar scores ou ranking.

Exemplos de novas linhas de investigação: critérios climáticos sazonais com
resolução regional, indicadores econômicos com período explícito, ou infraestrutura
digital com evidência comparável. São extensões propostas, sem dados ou capacidades
implementadas nesta entrega. O registro e o mapa podem ser substituídos para usar
a mesma arquitetura com cidades, produtos ou documentos; essa generalização exige
contratos e avaliação próprios.
