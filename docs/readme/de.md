# cs-study-map · Ein Informatik-Lehrbuch zum Selbststudium

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

Dieses Projekt dient vor allem dem Selbststudium des Maintainers. Es wählt geeignete Themen aus [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), ordnet sie nach Voraussetzungen in einem chinesischsprachigen Lehrbuch neu und ergänzt Erklärungen, eigene Beispiele, gelöste Übungen und Selbsttests. Synchronisierung, KI-Klassifikation und Quellenführer unterstützen Auswahl und Aktualisierung.

**[Lehrbuch](../textbook/index.md)** · [Lernkarte](../index.md) · [Abdeckung](../status.md) · [Nutzung](../usage.md) · [Quellen und Lizenzen](../../ATTRIBUTION.md)

Dies ist ein persönliches Lernprojekt von Pleniluner ohne offizielle Verbindung zur Tsinghua-Universität oder den Betreuern des Ursprungsprojekts. Das öffentliche Repository enthält eigene Werkzeuge, Lehrbuchentwürfe, Quellenverzeichnisse und KI-Leitfäden. Originale Kursmaterialien, Folien, Aufgaben, studentischer Quellcode und vollständig extrahierte Texte werden nicht veröffentlicht.

## Dreißig Kapitel der Reihe nach lernen

| # | Thema | Übung |
| --- | --- | --- |
| 1 | [Binärzahlen, Bytes und Little-Endian](../textbook/01-data-and-bytes.md) | Eine Zahl in Bytes zerlegen und aus dem Speicher rekonstruieren |
| 2 | [Register, Speicher und Stack](../textbook/02-execution-and-stack.md) | Den Zustand einer vereinfachten Maschine schrittweise verfolgen |
| 3 | [First Fit, Aufteilen und Zusammenführen](../textbook/03-first-fit.md) | Zuweisung und Freigabe durchrechnen und externe Fragmentierung erklären |
| 4 | [Sequenzen, Verzweigungen und Schleifen](../textbook/04-control-flow.md) | Variablen verfolgen sowie Grenzfälle und Schleifenenden prüfen |
| 5 | [Parameter, Rückgabewerte und Funktionen](../textbook/05-functions.md) | Funktionen kombinieren und Ausgabe, Rückgabe und lokale Namen unterscheiden |
| 6 | [Arrays und sequenzielle Listen](../textbook/06-arrays.md) | Indizes, Kapazität, gemeinsame Listen und Elementverschiebungen verfolgen |
| 7 | [Einfach verkettete Listen](../textbook/07-linked-lists.md) | Knotenreferenzen verfolgen sowie Einfügen, Löschen und Umkehren üben |
| 8 | [Stapel](../textbook/08-stacks.md) | LIFO zum Rückgängigmachen und zur Klammerprüfung anwenden |
| 9 | [Warteschlangen und Ringpuffer](../textbook/09-queues.md) | FIFO, umlaufende Indizes und leere oder volle Zustände prüfen |
| 10 | [Algorithmenanalyse](../textbook/10-algorithm-analysis.md) | Operationen zählen, Wachstum vergleichen und Zusatzspeicher berücksichtigen |
| 11 | [Lineare und binäre Suche](../textbook/11-searching.md) | Grenzen, doppelte Werte und fehlende Ziele verfolgen |
| 12 | [Sortieren durch Auswahl, Einfügen und Zusammenführen](../textbook/12-sorting.md) | Reihenfolge, Häufigkeiten, Stabilität und Suche nach dem Sortieren prüfen |
| 13 | [Rekursion, Rückgaben und Aufrufstapel](../textbook/13-recursion.md) | Basisfälle, Verkleinerung, Aufrufzahl und maximale Tiefe verfolgen |
| 14 | [Teile und herrsche und rekursives Mergesort](../textbook/14-divide-and-conquer.md) | Bereiche teilen, Ergebnisse kombinieren und Inversionen zählen |
| 15 | [Quicksort und Dreiwegepartitionierung](../textbook/15-quick-sort.md) | Partitionen, Duplikate, schlechteste Fälle und Stapeltiefe prüfen |
| 16 | [Bäume, Binärbäume und Traversierungen](../textbook/16-trees.md) | Höhe, Besuchsreihenfolge, Spiegelung und Vollständigkeit prüfen |
| 17 | [Binäre Suchbäume](../textbook/17-binary-search-trees.md) | Globale Schlüsselordnung, Löschverknüpfungen, Bereichssuche und Höhe prüfen |
| 18 | [Binäre Heaps und Prioritätswarteschlangen](../textbook/18-heaps.md) | Heapordnung reparieren, Heaps aufbauen und sortieren, die k größten Werte wählen und Listen zusammenführen |
| 19 | [Hashtabellen, Kollisionen und Vergrößerung](../textbook/19-hash-tables.md) | Schlüssel-Wert-Paare verwalten und erwartete, schlechteste und amortisierte Kosten unterscheiden |
| 20 | [Graphen und Speicherformen](../textbook/20-graphs.md) | Richtung, Adjazenzlisten, Matrizen, Grade und umgekehrte Kanten prüfen |
| 21 | [DFS, BFS und ungewichtete kürzeste Wege](../textbook/21-graph-traversal.md) | Entdeckung und Pfade verfolgen sowie Komponenten und mehrere Startpunkte behandeln |
| 22 | [Topologische Sortierung und DAG-Anwendungen](../textbook/22-topological-sort.md) | Abhängigkeiten verwalten, Zyklen finden und Aufgaben planen |
| 23 | [Gewichtete kürzeste Wege und Relaxation](../textbook/23-weighted-shortest-paths.md) | Dijkstra, Bellman–Ford, DAG-Reihenfolge und begrenzte Kantenzahl vergleichen |
| 24 | [Minimale Spannbäume und disjunkte Mengen](../textbook/24-minimum-spanning-trees.md) | Prim und Kruskal erklären sowie Wälder und neue Kanten prüfen |
| 25 | [Backtracking und Beschneidung](../textbook/25-backtracking.md) | Suchzustände wiederherstellen und Vollständigkeit der Ergebnisse prüfen |
| 26 | [Greedy-Algorithmen und Austauschargumente](../textbook/26-greedy-algorithms.md) | Gegenbeispiele entwickeln sowie Zeitpläne, Zusammenführungen und Präfixcodes prüfen |
| 27 | [Einführung in die dynamische Programmierung](../textbook/27-dynamic-programming.md) | Zustände definieren, Lösungen rekonstruieren und Aktualisierungsreihenfolgen prüfen |
| 28 | [Rucksackprobleme und Zählen von Lösungen](../textbook/28-knapsack.md) | Kapazität, genaues Gewicht, Wiederverwendung und Reihenfolge unterscheiden |
| 29 | [Dynamische Programmierung für Sequenzen](../textbook/29-sequence-dp.md) | Gemeinsame Teilfolgen, Editierausrichtungen und steigende Teilfolgen rekonstruieren |
| 30 | [Dynamische Programmierung für Intervalle und Bäume](../textbook/30-interval-tree-dp.md) | Benachbarte Bereiche zusammenführen sowie unabhängige Mengen und Knotenüberdeckungen prüfen |

Kapitel 4–30 verwenden Python ab Version 3.11 und enthalten 270 eigenständig ausführbare Programme mit erwarteten Ausgaben. Siehe die Leitfäden für [Programmierübungen](../programming-practice.md), [Datenstrukturen](../data-structures-practice.md) und [Algorithmen](../algorithms-practice.md), alle auf Chinesisch. [Übungen zu Rekursion und Teile und herrsche (auf Chinesisch)](../recursion-practice.md). [Übungen zu Bäumen und Heaps (auf Chinesisch)](../trees-practice.md). [Übungen zu Hashtabellen und Graphen (auf Chinesisch)](../hash-graphs-practice.md). [Übungen zu topologischer Sortierung und gewichteten Graphen (auf Chinesisch)](../weighted-graphs-practice.md). [Übungen zu Backtracking, Greedy-Algorithmen und dynamischer Programmierung (auf Chinesisch)](../strategy-practice.md). [Fortgeschrittene Übungen zur dynamischen Programmierung (auf Chinesisch)](../advanced-dp-practice.md).

Jedes Kapitel enthält ausführliche Erklärungen, 2 eigene Beispiele, 3 Aufgaben mit ausklappbaren Lösungen, einen Selbsttest und Themenquellen. Es handelt sich um einen KI-Erstentwurf ohne fachliche Begutachtung oder Erprobung durch Lernende. Das bedeutet nicht, dass für jeden Kurs ein Lehrbuch vorliegt.

## Funktionen

Lerne kapitelweise und speichere persönliche Notizen im von Git ignorierten Ordner `.local/`. Erstelle eigene Kapitel aus erkannten Themen und dokumentiere die Quellversionen. Suche nach Fachgebiet, Kurs oder KI-Thema und öffne eine feste Version der Ursprungsquelle. Prüfe Themen, Voraussetzungen, Vorschläge und Belegstellen, verwende unveränderte Analysen erneut und korrigiere automatische Zuordnungen mit manuellen Regeln.

KI-Leitfäden nennen Extraktionsumfang, Modell und den noch ungeprüften Status. Vollständigkeit des Katalogs und Abdeckung durch KI-Leitfäden werden getrennt erfasst. Teilauszüge, nicht unterstützte Formate und Fehler werden ausgewiesen.

## Schnellstart

Python 3.11 oder neuer ist erforderlich. Diese Schritte laden Metadaten und erstellen die Navigation. Ein Modellschlüssel ist nicht nötig; Quelltexte der Materialien werden nicht heruntergeladen.

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

## KI-Ausführung

Beide Betriebsarten verwenden dieselbe Validierung und Leitfadenerzeugung. Für eine Modell-API setze `CS_STUDY_API_BASE`, `CS_STUDY_MODEL` und `CS_STUDY_API_KEY`. Für die lokale Codex CLI setze `CS_STUDY_PROVIDER=codex` und `CS_STUDY_MODEL`, bei Bedarf auch `CS_STUDY_CODEX_BIN`. Die API unterstützt Chat Completions und Responses. Standard ist `chat`; `CS_STUDY_API_STYLE=responses` wählt Responses. Das Modell muss vom Dienst unterstützt werden. Auch die Codex-CLI-Version muss das gewählte Modell unterstützen; Zugangsdaten verwaltet die CLI selbst.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

Konfiguration, PowerShell-Beispiele und GitHub-Einstellungen stehen in der [Nutzungsanleitung](../usage.md).

## Geplante Synchronisierung

GitHub Actions prüft die Ursprungsquellen täglich; **Sync study map** lässt sich auch manuell starten. Mit konfiguriertem Modell werden Leitfäden und Kapitel innerhalb des Budgets erzeugt, geprüft und als Commit gespeichert. Standardmäßig werden täglich höchstens 6 Materialien analysiert und 1 Kapitel geschrieben. Den Umfang legt `config/curriculum.json` fest.

Ohne Modell wird der Katalog weiterhin synchronisiert und `not-configured` gemeldet. Vorhandene Leitfäden bleiben nutzbar; geänderte Quellen warten auf Analyse. Dateinamenregeln und simulierte Ausgaben gelten nicht als abgeschlossene KI-Arbeit. Zum Lesen ist kein Modellkonto nötig. Forks benötigen eine eigene API-Konfiguration; die lokale Codex-Anmeldung wird nicht zu GitHub übertragen. Nach langer Inaktivität kann GitHub Zeitpläne deaktivieren; sie lassen sich unter Actions wieder aktivieren.

## Projektstruktur

```text
config/                  Lernpfade, Quellen, Klassifikation, Kurszuordnung und Korrekturen
catalog/                 Metadaten, Analysen, Lehrbuchentwürfe und Abdeckung
docs/textbook/           Auf GitHub lesbares Lehrbuch (derzeit auf Chinesisch)
docs/                    Navigation nach Kurs und Fachgebiet, Lernprotokollvorlage und Nutzungshinweise
src/cs_study_map/        Synchronisierung, Extraktion, KI-Klassifikation und Texterstellung
tests/                   Prüfungen für Synchronisierung, Wiederherstellung, Herkunft und Veröffentlichung
.github/workflows/       geplante Synchronisierung und kontinuierliche Integration
.cache/                  Lokale Quelldateien und Extraktionscache; nicht committen
.local/                  Private Lernnotizen; nicht committen
```

Die Übersetzung der README bedeutet nicht, dass auch das Lehrbuch übersetzt ist. Der Lehrbuchtext ist derzeit auf Chinesisch.

Die anfängliche Fachzuordnung stammt aus der persönlichen Kursordnung des Maintainers und ist korrigierbar. Sie ist weder eine offizielle Klassifikation des Ursprungsprojekts noch ein Hochschulcurriculum. Neue Kurse warten auf Zuordnung. Unterstützt werden Text, üblicher Quellcode, PDF mit extrahierbarem Text, DOCX, PPTX und Notebook. Scan-OCR, alte DOC/PPT-Dateien und Archivanalyse sind nicht implementiert. PDF-Extraktion ist standardmäßig auf 8 Seiten und 10.000 Zeichen begrenzt; lange Unterlagen werden daher möglicherweise nur teilweise gelesen.

## Prüfung und Mitwirkung

Führe `python -m unittest discover -s tests -v` und `cs-study-map validate --tracked` aus. Fehler können als Issue gemeldet werden. PRs können Code, Zuordnungen oder manuelle Regeln verbessern; siehe [Beitragsleitfaden](../../CONTRIBUTING.md).

Eigene Programme, Lehrbuchtexte und Wartungsdokumente stehen unter der MIT-Lizenz. Rechte an Quellenmaterial bleiben unverändert; siehe [Quellen und Lizenzen](../../ATTRIBUTION.md).

Frühere Arbeiten: [Wissensübersicht und 60 Kursleitfäden](../early-work/index.md), einschließlich Kategorienübersicht und Lehrbuch-README. Die bestehenden Dokumente wurden mit erhaltenen Lerninhalten und ohne lokale absolute Pfade in Git aufgenommen.
