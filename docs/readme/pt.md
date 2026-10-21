# cs-study-map · Material de computação para estudo pessoal

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

O projeto serve principalmente ao estudo do mantenedor: seleciona temas de [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), reorganiza-os em material em chinês conforme os pré-requisitos e acrescenta explicações, exemplos originais, exercícios resolvidos e autoavaliação. Sincronização, classificação por IA e guias de fontes apoiam a seleção e atualização.

**[Material didático](../textbook/index.md)** · [Mapa de estudo](../index.md) · [Cobertura](../status.md) · [Uso](../usage.md) · [Fontes e licenças](../../ATTRIBUTION.md)

Este é um projeto pessoal de Pleniluner, sem vínculo oficial com a Universidade Tsinghua ou os mantenedores originais. O repositório público contém ferramentas próprias, rascunhos, índices de fontes e guias de IA. Materiais didáticos originais, slides, tarefas, código de estudantes e texto integral extraído não são publicados.

## Estude cinco capítulos em ordem

| # | Tema | Atividade |
| --- | --- | --- |
| 1 | [Binário, bytes e ordem little-endian](../textbook/01-data-and-bytes.md) | Dividir um número em bytes e reconstruí-lo a partir da memória |
| 2 | [Registradores, memória e pilha](../textbook/02-execution-and-stack.md) | Acompanhar passo a passo o estado de uma máquina simplificada |
| 3 | [Primeiro ajuste, divisão e fusão](../textbook/03-first-fit.md) | Simular alocação e liberação e explicar a fragmentação externa |
| 4 | [Sequências, condições e laços](../textbook/04-control-flow.md) | Acompanhar variáveis e verificar limites e condições de término |
| 5 | [Parâmetros, valores de retorno e funções](../textbook/05-functions.md) | Combinar funções e distinguir impressão, retorno e nomes locais |

Os capítulos 4 e 5 usam Python 3.11 ou superior e incluem 20 programas independentes com as saídas esperadas. A preparação e o método estão no [guia de prática de programação](../programming-practice.md), em chinês.

Cada capítulo inclui explicações detalhadas, 2 exemplos originais, 3 exercícios com soluções expansíveis, uma autoavaliação e as fontes dos temas. É um primeiro rascunho de IA, sem revisão por especialistas nem teste com estudantes; isso não significa que todos os cursos tenham um livro completo.

## O que oferece

Estude por capítulos e guarde notas particulares em `.local/`, ignorado pelo Git. Crie capítulos originais a partir dos temas identificados e registre as versões das fontes. Encontre materiais por área, curso ou tema identificado por IA e abra uma revisão fixa da fonte. Consulte temas, pré-requisitos, sugestões e locais das evidências; reutilize análises sem alterações e corrija a classificação automática com regras manuais.

Os guias de IA informam a cobertura da extração, o modelo e o estado sem verificação humana. A completude do catálogo e a cobertura dos guias são medidas separadamente. Extrações parciais, formatos não suportados e falhas são informados.

## Início rápido

Requer Python 3.11 ou mais recente. Estas etapas obtêm metadados e geram a navegação, sem chave de modelo nem download do conteúdo das fontes.

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e .
cs-study-map run --limit 0
```

## Execução de IA

Os dois modos usam a mesma validação e geração de guias. Para uma API, configure `CS_STUDY_API_BASE`, `CS_STUDY_MODEL` e `CS_STUDY_API_KEY`. Para Codex CLI local, configure `CS_STUDY_PROVIDER=codex` e `CS_STUDY_MODEL`, além de `CS_STUDY_CODEX_BIN` se necessário. A API suporta Chat Completions e Responses: o padrão é `chat`; `CS_STUDY_API_STYLE=responses` seleciona Responses. Use um modelo suportado pelo serviço. A versão do Codex CLI também deve suportar o modelo escolhido e gerencia suas próprias credenciais.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

Veja o [guia de uso](../usage.md) para configuração, exemplos de PowerShell e ajustes do GitHub.

## Sincronização agendada

O GitHub Actions verifica as fontes diariamente; **Sync study map** também pode ser iniciado manualmente. Com um modelo configurado, gera guias e capítulos dentro do orçamento, valida e registra as atualizações. Os limites padrão são 6 materiais analisados e 1 capítulo escrito por dia. O escopo fica em `config/curriculum.json`.

Sem modelo, o catálogo continua sendo sincronizado e o estado é `not-configured`. Os guias existentes permanecem disponíveis e as fontes alteradas aguardam análise. Regras de nomes e saídas simuladas não são apresentadas como trabalho de IA concluído. Consultar o mapa não exige conta de modelo. Forks precisam configurar sua própria API; o login local do Codex não é enviado ao GitHub. Após inatividade prolongada, o GitHub pode desativar o agendamento; reative-o em Actions.

## Estrutura

```text
config/                  rotas, fontes, classificação, mapeamentos e correções
catalog/                 metadados, análises, rascunhos e cobertura
docs/textbook/           Material didático legível no GitHub (atualmente em chinês)
docs/                    navegação por cursos e áreas, modelo de registro e instruções
src/cs_study_map/        sincronização, extração, classificação por IA e escrita
tests/                   verificações de sincronização, recuperação, procedência e publicação
.github/workflows/       sincronização agendada e integração contínua
.cache/                  arquivos locais e cache de extração; não enviar
.local/                  anotações privadas; não enviar
```

A tradução do README não significa que o material didático foi traduzido; ele está em chinês.

Os mapeamentos iniciais vêm da organização pessoal dos cursos pelo mantenedor e podem ser corrigidos. Não são categorias oficiais do projeto original nem um currículo universitário. Novos cursos ficam pendentes de classificação. São suportados texto, código comum, PDF com texto extraível, DOCX, PPTX e Notebook. OCR, DOC/PPT antigos e análise de arquivos compactados não estão implementados. Por padrão, a extração de PDF se limita a 8 páginas e 10.000 caracteres; materiais longos podem ser lidos apenas parcialmente.

## Validação e contribuição

Execute `python -m unittest discover -s tests -v` e `cs-study-map validate --tracked`. Informe erros em Issues. PRs podem melhorar código, mapeamentos e regras manuais; veja o [guia de contribuição](../../CONTRIBUTING.md).

Programas originais, textos didáticos e documentos de manutenção usam a licença MIT. Os direitos dos materiais de origem não mudam; veja [fontes e licenças](../../ATTRIBUTION.md).

Trabalho anterior: [mapa geral e 60 guias de cursos](../early-work/index.md), incluindo a visão das categorias e o README do material didático. Os documentos existentes foram incorporados ao Git com o conteúdo didático preservado e os caminhos locais absolutos removidos.
