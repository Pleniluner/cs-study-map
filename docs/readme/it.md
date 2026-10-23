# cs-study-map · Un testo di informatica per lo studio personale

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

Il progetto serve soprattutto allo studio del manutentore: seleziona argomenti da [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), li riorganizza in un testo in cinese secondo i prerequisiti e aggiunge spiegazioni, esempi originali, esercizi svolti e autoverifiche. Sincronizzazione, classificazione AI e guide alle fonti aiutano a scegliere e aggiornare i contenuti.

**[Testo didattico](../textbook/index.md)** · [Mappa di studio](../index.md) · [Copertura](../status.md) · [Uso](../usage.md) · [Fonti e licenze](../../ATTRIBUTION.md)

È un progetto personale di Pleniluner, senza affiliazione ufficiale con la Tsinghua University o i manutentori upstream. Il repository pubblico contiene strumenti originali, bozze, indici delle fonti e guide AI. Materiali didattici originali, slide, compiti, codice degli studenti e testi estratti integralmente non sono pubblicati.

## Studia 33 capitoli in ordine

| # | Argomento | Attività |
| --- | --- | --- |
| 1 | [Binario, byte e ordine little-endian](../textbook/01-data-and-bytes.md) | Scomporre un numero in byte e ricostruirlo dalla memoria |
| 2 | [Registri, memoria e stack](../textbook/02-execution-and-stack.md) | Seguire passo per passo lo stato di una macchina semplificata |
| 3 | [Primo adattamento, divisione e fusione](../textbook/03-first-fit.md) | Simulare allocazione e rilascio e spiegare la frammentazione esterna |
| 4 | [Sequenze, condizioni e cicli](../textbook/04-control-flow.md) | Seguire le variabili e verificare i casi limite e la terminazione dei cicli |
| 5 | [Parametri, valori restituiti e funzioni](../textbook/05-functions.md) | Combinare funzioni e distinguere stampa, restituzione e nomi locali |
| 6 | [Array e liste sequenziali](../textbook/06-arrays.md) | Seguire indici, capacità, liste condivise e spostamenti degli elementi |
| 7 | [Liste concatenate semplici](../textbook/07-linked-lists.md) | Seguire i riferimenti ed eseguire inserimento, rimozione e inversione |
| 8 | [Pile](../textbook/08-stacks.md) | Applicare LIFO all’annullamento e al controllo delle parentesi |
| 9 | [Code e array circolari](../textbook/09-queues.md) | Verificare FIFO, il ritorno all’inizio e gli stati vuoto o pieno |
| 10 | [Analisi degli algoritmi](../textbook/10-algorithm-analysis.md) | Contare le operazioni, confrontare la crescita e valutare la memoria aggiuntiva |
| 11 | [Ricerca sequenziale e binaria](../textbook/11-searching.md) | Seguire limiti, duplicati e valori assenti |
| 12 | [Ordinamento per selezione, inserimento e fusione](../textbook/12-sorting.md) | Verificare ordine, molteplicità, stabilità e ricerca dopo l’ordinamento |
| 13 | [Ricorsione, valori restituiti e pila delle chiamate](../textbook/13-recursion.md) | Seguire casi base, riduzione, numero di chiamate e profondità massima |
| 14 | [Divide et impera e ordinamento ricorsivo per fusione](../textbook/14-divide-and-conquer.md) | Dividere intervalli, combinare risultati e contare inversioni |
| 15 | [Quicksort e partizionamento a tre vie](../textbook/15-quick-sort.md) | Verificare partizioni, duplicati, casi peggiori e profondità della pila |
| 16 | [Alberi, alberi binari e visite](../textbook/16-trees.md) | Verificare altezza, ordine di visita, riflessione e completezza |
| 17 | [Alberi binari di ricerca](../textbook/17-binary-search-trees.md) | Mantenere ordine globale, collegamenti dopo la rimozione, intervalli e altezza |
| 18 | [Heap binari e code con priorità](../textbook/18-heaps.md) | Ripristinare l’ordine, costruire e ordinare heap, scegliere i k maggiori e fondere liste |
| 19 | [Tabelle hash, collisioni e ridimensionamento](../textbook/19-hash-tables.md) | Gestire chiavi e valori e distinguere costi attesi, peggiori e ammortizzati |
| 20 | [Grafi e rappresentazioni](../textbook/20-graphs.md) | Verificare direzione, liste di adiacenza, matrici, gradi e archi invertiti |
| 21 | [DFS, BFS e cammini minimi senza pesi](../textbook/21-graph-traversal.md) | Tracciare la scoperta, ricostruire percorsi e gestire componenti e più sorgenti |
| 22 | [Ordinamento topologico e applicazioni ai DAG](../textbook/22-topological-sort.md) | Gestire dipendenze, ricostruire cicli e pianificare attività |
| 23 | [Cammini minimi pesati e rilassamento](../textbook/23-weighted-shortest-paths.md) | Confrontare Dijkstra, Bellman–Ford, ordine dei DAG e limiti sugli archi |
| 24 | [Alberi ricoprenti minimi e insiemi disgiunti](../textbook/24-minimum-spanning-trees.md) | Spiegare Prim e Kruskal, verificare foreste e aggiunta di archi |
| 25 | [Backtracking e potatura](../textbook/25-backtracking.md) | Ripristinare lo stato e verificare che la ricerca conservi tutte le soluzioni |
| 26 | [Algoritmi greedy e argomenti di scambio](../textbook/26-greedy-algorithms.md) | Costruire controesempi e verificare intervalli, fusioni e codici prefissi |
| 27 | [Introduzione alla programmazione dinamica](../textbook/27-dynamic-programming.md) | Definire gli stati, ricostruire le soluzioni e controllare gli aggiornamenti |
| 28 | [Problemi dello zaino e conteggio](../textbook/28-knapsack.md) | Distinguere capacità, peso esatto, riuso, combinazioni e sequenze |
| 29 | [Programmazione dinamica sulle sequenze](../textbook/29-sequence-dp.md) | Ricostruire sottosequenze comuni, allineamenti e sottosequenze crescenti |
| 30 | [Programmazione dinamica su intervalli e alberi](../textbook/30-interval-tree-dp.md) | Pianificare fusioni adiacenti e verificare insiemi indipendenti e coperture |
| 31 | [Ricerca di stringhe e KMP](../textbook/31-string-matching.md) | Seguire prefissi, sovrapposizioni, blocchi e rotazioni |
| 32 | [Trie e ricerca per prefisso](../textbook/32-trie.md) | Gestire parole ripetute, cancellazione, enumerazione e conteggi |
| 33 | [Somme prefisse, due puntatori e finestre scorrevoli](../textbook/33-prefix-window.md) | Verificare estremi, monotonia e regole di conteggio |

I capitoli dal 4 al 33 usano Python 3.11 o successivo e includono 300 programmi autonomi con l’output atteso. Consulta le guide alla [programmazione](../programming-practice.md), alle [strutture dati](../data-structures-practice.md) e agli [algoritmi](../algorithms-practice.md), in cinese. [Esercizi su ricorsione e divide et impera (in cinese)](../recursion-practice.md). [Esercizi su alberi e heap (in cinese)](../trees-practice.md). [Esercizi su tabelle hash e grafi (in cinese)](../hash-graphs-practice.md). [Esercizi su ordinamento topologico e grafi pesati (in cinese)](../weighted-graphs-practice.md). [Esercizi su backtracking, algoritmi greedy e programmazione dinamica (in cinese)](../strategy-practice.md). [Esercizi avanzati di programmazione dinamica (in cinese)](../advanced-dp-practice.md). [Esercizi su stringhe, trie e intervalli (in cinese)](../string-window-practice.md).

Ogni capitolo contiene spiegazioni dettagliate, 2 esempi originali, 3 esercizi con soluzioni espandibili, un’autoverifica e le fonti degli argomenti. È una prima bozza AI, non revisionata da esperti né sperimentata con studenti; non significa che tutti i corsi abbiano un manuale completo.

## Cosa offre

Studia per capitoli e conserva gli appunti privati in `.local/`, esclusa da Git. Crea capitoli originali dai temi identificati registrando le versioni delle fonti. Cerca materiali per area, corso o tema individuato dall’AI e apri una revisione fissa della fonte. Consulta temi, prerequisiti, suggerimenti e punti di riscontro; riutilizza le analisi invariate e correggi la classificazione automatica con regole manuali.

Le guide AI dichiarano copertura dell’estrazione, modello e stato non verificato da persone. Completezza del catalogo e copertura delle guide sono misurate separatamente. Sono segnalati estrazioni parziali, formati non supportati ed errori.

## Avvio rapido

Serve Python 3.11 o successivo. Questi passaggi recuperano metadati e creano la navigazione, senza chiave del modello né download del contenuto delle fonti.

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

## Esecuzione AI

Entrambe le modalità usano la stessa validazione e generazione delle guide. Per un’API imposta `CS_STUDY_API_BASE`, `CS_STUDY_MODEL` e `CS_STUDY_API_KEY`. Per Codex CLI locale imposta `CS_STUDY_PROVIDER=codex` e `CS_STUDY_MODEL`, ed eventualmente `CS_STUDY_CODEX_BIN`. L’API supporta Chat Completions e Responses: il valore predefinito è `chat`; `CS_STUDY_API_STYLE=responses` seleziona Responses. Usa un modello supportato dal servizio. Anche la versione di Codex CLI deve supportare il modello scelto; il CLI gestisce le proprie credenziali.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

Per configurazione, esempi PowerShell e impostazioni GitHub consulta la [guida all’uso](../usage.md).

## Sincronizzazione pianificata

GitHub Actions controlla le fonti ogni giorno; **Sync study map** si può avviare anche manualmente. Con un modello configurato, genera guide e capitoli entro il budget, li verifica e registra gli aggiornamenti. I limiti predefiniti sono 6 materiali analizzati e 1 capitolo scritto al giorno. L’ambito è definito in `config/curriculum.json`.

Senza modello, il catalogo viene comunque sincronizzato e viene segnalato `not-configured`. Le guide esistenti restano disponibili e le fonti modificate attendono l’analisi. Regole sui nomi e risultati simulati non sono indicati come lavoro AI completato. Per leggere la mappa non serve un account del modello. I fork richiedono una propria configurazione API; l’accesso Codex locale non viene caricato su GitHub. Dopo lunga inattività GitHub può disattivare la pianificazione, riattivabile in Actions.

## Struttura

```text
config/                  percorsi, fonti, classificazione, corrispondenze e correzioni
catalog/                 metadati, analisi, bozze e copertura
docs/textbook/           Testo consultabile su GitHub (attualmente in cinese)
docs/                    navigazione per corsi e aree, modello di registro e istruzioni
src/cs_study_map/        sincronizzazione, estrazione, classificazione AI e scrittura
tests/                   verifiche di sincronizzazione, ripristino, provenienza e pubblicazione
.github/workflows/       sincronizzazione pianificata e integrazione continua
.cache/                  file sorgente locali e cache di estrazione; non committare
.local/                  note private; non committare
```

La traduzione del README non significa che il testo didattico sia tradotto; al momento è in cinese.

Le corrispondenze iniziali derivano dall’organizzazione personale dei corsi del manutentore e sono modificabili. Non sono categorie ufficiali del progetto originale né un piano universitario. I corsi nuovi attendono classificazione. Sono supportati testo, codice comune, PDF con testo estraibile, DOCX, PPTX e Notebook. OCR, vecchi DOC/PPT e analisi di archivi compressi non sono implementati. L’estrazione PDF è limitata per impostazione predefinita a 8 pagine e 10.000 caratteri; un documento lungo può essere letto solo in parte.

## Verifica e contributi

Esegui `python -m unittest discover -s tests -v` e `cs-study-map validate --tracked`. Segnala gli errori nelle Issue. Le PR possono migliorare codice, corrispondenze e regole manuali; vedi la [guida ai contributi](../../CONTRIBUTING.md).

Programmi originali, testi del manuale e documenti di manutenzione usano la licenza MIT. I diritti sui materiali di origine non cambiano; vedi [fonti e licenze](../../ATTRIBUTION.md).

Lavori precedenti: [mappa generale e 60 guide ai corsi](../early-work/index.md), con la panoramica delle categorie e il README del manuale. I documenti preesistenti sono stati inseriti in Git conservando il contenuto didattico e rimuovendo i percorsi locali assoluti.
