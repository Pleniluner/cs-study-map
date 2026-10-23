# cs-study-map · Un manuel d’informatique pour apprendre par soi-même

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

Ce projet sert d’abord à l’apprentissage personnel de son mainteneur. Il sélectionne des sujets dans [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), les réorganise en un manuel en chinois selon les prérequis, puis ajoute des explications, exemples originaux, exercices corrigés et autoévaluations. La synchronisation, la classification IA et les guides appuient le choix et la mise à jour du contenu.

**[Manuel](../textbook/index.md)** · [Carte d’étude](../index.md) · [Couverture](../status.md) · [Utilisation](../usage.md) · [Sources et licences](../../ATTRIBUTION.md)

Ce projet personnel est maintenu par Pleniluner, sans affiliation officielle avec l’Université Tsinghua ni les responsables amont. Le dépôt public contient des outils originaux, des brouillons, des index de sources et des guides IA. Les supports originaux, diapositives, devoirs, codes d’étudiants et textes extraits intégralement ne sont pas publiés.

## Étudier 36 chapitres dans l’ordre

| # | Sujet | Activité |
| --- | --- | --- |
| 1 | [Binaire, octets et ordre petit-boutiste](../textbook/01-data-and-bytes.md) | Décomposer un nombre en octets, puis le reconstituer depuis la mémoire |
| 2 | [Registres, mémoire et pile](../textbook/02-execution-and-stack.md) | Suivre pas à pas l’état d’une machine simplifiée |
| 3 | [Premier ajustement, division et fusion](../textbook/03-first-fit.md) | Simuler allocation et libération, puis expliquer la fragmentation externe |
| 4 | [Séquences, conditions et boucles](../textbook/04-control-flow.md) | Suivre les variables et vérifier les limites et la terminaison des boucles |
| 5 | [Paramètres, valeurs de retour et fonctions](../textbook/05-functions.md) | Combiner des fonctions et distinguer affichage, retour et noms locaux |
| 6 | [Tableaux et listes séquentielles](../textbook/06-arrays.md) | Suivre les indices, la capacité, les listes partagées et les décalages |
| 7 | [Listes simplement chaînées](../textbook/07-linked-lists.md) | Suivre les références et réaliser insertion, suppression et inversion |
| 8 | [Piles](../textbook/08-stacks.md) | Appliquer LIFO à l’annulation et à la vérification des parenthèses |
| 9 | [Files et tableaux circulaires](../textbook/09-queues.md) | Vérifier FIFO, le retour en début de tableau et les états vide ou plein |
| 10 | [Analyse des algorithmes](../textbook/10-algorithm-analysis.md) | Compter les opérations, comparer la croissance et évaluer la mémoire supplémentaire |
| 11 | [Recherche séquentielle et dichotomique](../textbook/11-searching.md) | Suivre les bornes, les doublons et les valeurs absentes |
| 12 | [Tris par sélection, insertion et fusion](../textbook/12-sorting.md) | Vérifier l’ordre, les multiplicités, la stabilité et la recherche après tri |
| 13 | [Récursivité, retours et pile d’appels](../textbook/13-recursion.md) | Suivre les cas de base, la progression, les appels et la profondeur maximale |
| 14 | [Diviser pour régner et tri fusion récursif](../textbook/14-divide-and-conquer.md) | Découper les intervalles, combiner les résultats et compter les inversions |
| 15 | [Tri rapide et partitionnement en trois parties](../textbook/15-quick-sort.md) | Vérifier les partitions, les doublons, les pires cas et la profondeur de pile |
| 16 | [Arbres, arbres binaires et parcours](../textbook/16-trees.md) | Vérifier hauteur, ordre de parcours, miroir et complétude |
| 17 | [Arbres binaires de recherche](../textbook/17-binary-search-trees.md) | Maintenir l’ordre global, les liens après suppression, les intervalles et la hauteur |
| 18 | [Tas binaires et files de priorité](../textbook/18-heaps.md) | Rétablir l’ordre, construire et trier un tas, sélectionner les k plus grands et fusionner |
| 19 | [Tables de hachage, collisions et redimensionnement](../textbook/19-hash-tables.md) | Gérer les paires clé-valeur et distinguer coûts espérés, au pire et amortis |
| 20 | [Graphes et représentations](../textbook/20-graphs.md) | Vérifier orientation, listes d’adjacence, matrices, degrés et arcs inversés |
| 21 | [DFS, BFS et plus courts chemins sans poids](../textbook/21-graph-traversal.md) | Suivre la découverte, reconstruire les chemins et traiter composantes et sources multiples |
| 22 | [Tri topologique et applications aux DAG](../textbook/22-topological-sort.md) | Suivre les dépendances, retrouver les cycles et planifier les tâches |
| 23 | [Plus courts chemins pondérés et relaxation](../textbook/23-weighted-shortest-paths.md) | Comparer Dijkstra, Bellman–Ford, l’ordre d’un DAG et les limites de parcours |
| 24 | [Arbres couvrants minimaux et ensembles disjoints](../textbook/24-minimum-spanning-trees.md) | Expliquer Prim et Kruskal, vérifier les forêts et l’ajout d’une arête |
| 25 | [Retour sur trace et élagage](../textbook/25-backtracking.md) | Restaurer les états et vérifier que tous les résultats sont conservés |
| 26 | [Algorithmes gloutons et arguments d’échange](../textbook/26-greedy-algorithms.md) | Construire des contre-exemples et vérifier les choix, les fusions et les codes préfixes |
| 27 | [Introduction à la programmation dynamique](../textbook/27-dynamic-programming.md) | Définir les états, reconstruire les solutions et vérifier l’ordre des mises à jour |
| 28 | [Problèmes de sac à dos et dénombrement](../textbook/28-knapsack.md) | Distinguer capacité, poids exact, réutilisation, combinaisons et séquences |
| 29 | [Programmation dynamique sur les séquences](../textbook/29-sequence-dp.md) | Reconstruire les sous-séquences communes, les alignements et les sous-séquences croissantes |
| 30 | [Programmation dynamique sur les intervalles et les arbres](../textbook/30-interval-tree-dp.md) | Planifier les fusions adjacentes et vérifier ensembles indépendants et couvertures |
| 31 | [Recherche de motifs et KMP](../textbook/31-string-matching.md) | Suivre les préfixes, les chevauchements, les blocs et les rotations |
| 32 | [Tries et recherche par préfixe](../textbook/32-trie.md) | Gérer les mots répétés, la suppression, l’énumération et les comptes |
| 33 | [Sommes préfixes, deux pointeurs et fenêtres glissantes](../textbook/33-prefix-window.md) | Justifier les bornes, la monotonie et le dénombrement |
| 34 | [Piles et files monotones](../textbook/34-monotonic-structures.md) | Justifier le retrait des candidats et vérifier les intervalles avec valeurs négatives |
| 35 | [Arbres de Fenwick et rangs de fréquences](../textbook/35-fenwick-tree.md) | Maintenir les blocs préfixes, les différences et les fréquences non négatives |
| 36 | [Arbres de segments et propagation différée](../textbook/36-segment-tree.md) | Fusionner les résumés et suivre l’ordre des requêtes et les mises à jour |

Les chapitres 4 à 36 utilisent Python 3.11 ou une version ultérieure et proposent 330 programmes autonomes avec leur sortie attendue. Consultez les guides de [programmation](../programming-practice.md), de [structures de données](../data-structures-practice.md) et d’[algorithmes](../algorithms-practice.md), en chinois. [Exercices de récursivité et de division du problème (en chinois)](../recursion-practice.md). [Exercices sur les arbres et les tas (en chinois)](../trees-practice.md). [Exercices sur les tables de hachage et les graphes (en chinois)](../hash-graphs-practice.md). [Exercices sur le tri topologique et les graphes pondérés (en chinois)](../weighted-graphs-practice.md). [Exercices de recherche, d’algorithmes gloutons et de programmation dynamique (en chinois)](../strategy-practice.md). [Exercices avancés de programmation dynamique (en chinois)](../advanced-dp-practice.md). [Exercices sur les chaînes, les tries et les intervalles (en chinois)](../string-window-practice.md). [Exercices sur les structures monotones et les requêtes dynamiques par intervalle (en chinois)](../range-structures-practice.md).

Chaque chapitre contient des explications détaillées, 2 exemples originaux, 3 exercices avec solutions dépliables, une autoévaluation et les sources des sujets. Il s’agit d’un premier jet produit par IA, sans validation par des spécialistes ni essai auprès d’apprenants ; tous les cours ne disposent pas encore d’un manuel.

## Fonctionnalités

Étudiez par chapitre et conservez vos notes privées dans `.local/`, ignoré par Git. Créez des chapitres originaux à partir des thèmes identifiés en conservant les versions des sources. Retrouvez les documents par domaine, cours ou sujet identifié par IA, puis ouvrez une révision amont fixe. Consultez thèmes, prérequis, suggestions et emplacements des preuves ; réutilisez les analyses inchangées et corrigez le classement automatique avec des règles manuelles.

Les guides IA indiquent la couverture de l’extraction, le modèle et l’absence de vérification humaine. L’exhaustivité du catalogue et la couverture des guides sont mesurées séparément. Les extractions partielles, formats non pris en charge et échecs sont signalés.

## Démarrage rapide

Python 3.11 ou ultérieur est requis. Ces étapes récupèrent les métadonnées et créent la navigation, sans clé de modèle ni téléchargement du texte des sources.

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

## Exécution de l’IA

Les deux modes partagent les mêmes étapes de validation et de génération. Pour une API, définissez `CS_STUDY_API_BASE`, `CS_STUDY_MODEL` et `CS_STUDY_API_KEY`. Pour Codex CLI local, définissez `CS_STUDY_PROVIDER=codex` et `CS_STUDY_MODEL`, ainsi que `CS_STUDY_CODEX_BIN` si nécessaire. L’API prend en charge Chat Completions et Responses : `chat` est le mode par défaut ; `CS_STUDY_API_STYLE=responses` sélectionne Responses. Choisissez un modèle pris en charge par le service. La version de Codex CLI doit également le prendre en charge ; le CLI gère ses identifiants.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

Consultez le [guide d’utilisation](../usage.md) pour la configuration, les exemples PowerShell et les réglages GitHub.

## Synchronisation planifiée

GitHub Actions vérifie les sources chaque jour ; **Sync study map** permet aussi un lancement manuel. Si un modèle est configuré, le processus génère guides et chapitres dans les limites du budget, les valide et enregistre les modifications. Par défaut : au plus 6 documents analysés et 1 chapitre rédigé par jour. Le périmètre figure dans `config/curriculum.json`.

Sans modèle, le catalogue est synchronisé avec le statut `not-configured`. Les guides existants restent consultables et les sources modifiées attendent leur analyse. Les règles sur les noms de fichiers et les sorties simulées ne sont jamais présentées comme du travail IA terminé. La consultation ne nécessite pas de compte de modèle. Les forks doivent configurer leur propre API ; la connexion Codex locale n’est pas envoyée à GitHub. Après une longue inactivité, GitHub peut suspendre la planification ; réactivez-la dans Actions.

## Organisation

```text
config/                  parcours, sources, classement, correspondances et corrections
catalog/                 métadonnées, analyses, brouillons et couverture
docs/textbook/           Manuel lisible sur GitHub (actuellement en chinois)
docs/                    Navigation par cours et domaine, modèle de notes et guide
src/cs_study_map/        synchronisation, extraction, classification IA et rédaction
tests/                   vérifications de synchronisation, reprise, provenance et publication
.github/workflows/       synchronisation planifiée et intégration continue
.cache/                  Sources locales et cache d’extraction ; ne pas committer
.local/                  Notes privées ; ne pas committer
```

La traduction du README ne signifie pas que le manuel est traduit : son texte est actuellement en chinois.

Les correspondances initiales proviennent du classement personnel du mainteneur et restent modifiables. Elles ne constituent ni une classification officielle amont ni un cursus universitaire. Les nouveaux cours attendent leur classement. Formats pris en charge : texte, code courant, PDF avec texte extractible, DOCX, PPTX et Notebook. L’OCR, les anciens DOC/PPT et l’analyse d’archives ne sont pas implémentés. L’extraction PDF est limitée par défaut à 8 pages et 10 000 caractères ; un long support peut donc être lu partiellement.

## Validation et contribution

Exécutez `python -m unittest discover -s tests -v` et `cs-study-map validate --tracked`. Signalez les erreurs dans les Issues. Les PR peuvent améliorer le code, les correspondances et les règles manuelles ; consultez le [guide de contribution](../../CONTRIBUTING.md).

Les programmes originaux, textes du manuel et documents de maintenance sont sous licence MIT. Les droits sur les sources restent inchangés ; consultez les [sources et licences](../../ATTRIBUTION.md).

Travaux antérieurs : [vue d’ensemble et 60 guides de cours](../early-work/index.md), avec le panorama des catégories et le README du manuel. Ces documents préexistants ont été intégrés à Git en conservant le contenu pédagogique et en supprimant les chemins locaux absolus.
