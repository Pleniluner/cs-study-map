# cs-study-map · Un manuel d’informatique pour apprendre par soi-même

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

Ce projet sert d’abord à l’apprentissage personnel de son mainteneur. Il sélectionne des sujets dans [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), les réorganise en un manuel en chinois selon les prérequis, puis ajoute des explications, exemples originaux, exercices corrigés et autoévaluations. La synchronisation, la classification IA et les guides appuient le choix et la mise à jour du contenu.

**[Manuel](../textbook/index.md)** · [Carte d’étude](../index.md) · [Couverture](../status.md) · [Utilisation](../usage.md) · [Sources et licences](../../ATTRIBUTION.md)

Ce projet personnel est maintenu par Pleniluner, sans affiliation officielle avec l’Université Tsinghua ni les responsables amont. Le dépôt public contient des outils originaux, des brouillons, des index de sources et des guides IA. Les supports originaux, diapositives, devoirs, codes d’étudiants et textes extraits intégralement ne sont pas publiés.

## Commencer par trois chapitres

| # | Sujet | Activité |
| --- | --- | --- |
| 1 | [Binaire, octets et ordre petit-boutiste](../textbook/01-data-and-bytes.md) | Décomposer un nombre en octets, puis le reconstituer depuis la mémoire |
| 2 | [Registres, mémoire et pile](../textbook/02-execution-and-stack.md) | Suivre pas à pas l’état d’une machine simplifiée |
| 3 | [Premier ajustement, division et fusion](../textbook/03-first-fit.md) | Simuler allocation et libération, puis expliquer la fragmentation externe |

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
