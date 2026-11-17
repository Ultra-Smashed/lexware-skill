# Lexware-Skill

Ein Skill für Claude. Der Lexware-Skill verbindet Claude mit Lexware Office. Du sagst „Rechnung an Müller, acht Stunden Beratung“, und der Entwurf liegt in Lexware. Dazu Belege aus Quittungsfotos, offene Posten mit fertiger Zahlungserinnerung, Angebote aus einem Sprachmemo und ein Monatsüberblick. Alles landet als Entwurf, festschreiben und versenden machst du selbst. Kostenlos, MIT-Lizenz.

| Modul | Was es macht |
| --- | --- |
| **Rechnung** | Aus einem Satz wird ein Rechnungsentwurf. Claude sucht den Kunden, fragt nach, was fehlt, und zeigt dir Netto, Steuer und Brutto, bevor es anlegt. Auch mehrere Rechnungen auf einmal. |
| **Belege** | Quittungsfotos und PDFs werden in Lexware hochgeladen und dort automatisch ausgelesen. Du prüfst sie unter Belege → Zu prüfen. |
| **Offene Posten** | Wer hat noch nicht bezahlt, seit wann, wie viel? Dazu die passende Zahlungserinnerung oder ein Mahnungsentwurf in Lexware. |
| **Angebot** | Sprachmemo nach dem Kundentermin rein, fertiges Angebot raus. Sagt der Kunde Ja, wird mit einem Satz die Rechnung daraus. |
| **Monatsüberblick** | Umsatz, Ausgaben, offene und überfällige Rechnungen, Top-Kunden und ungeprüfte Belege, plus drei To-dos für den Monatsabschluss. |

## Was du brauchst

- Lexware Office im Tarif XL. Nur dort gibt es die Public API, und nur Admins können Schlüssel anlegen.
- Für den direkten Zugriff: Claude Code oder Claude Desktop mit dem Plugin. Die Claude-App im Browser und auf dem Handy erreicht Lexware nicht direkt (siehe unten).
- Ein Claude-Konto mit eingeschalteter Code-Ausführung.

## Wo es direkt funktioniert

| Wo | Was passiert |
| --- | --- |
| **Claude Code** | Direkt: Das Skript `scripts/lexware.py` spricht mit der API. |
| **Claude Desktop mit Plugin** | Direkt: Das Plugin bringt einen kleinen lokalen Server mit (`mcp/server.mjs`, braucht Node.js 18+). Der Schlüssel bleibt auf deinem Rechner. |
| **Claude-App (Web, Handy)** | Vorbereitungsmodus: Claude baut alles fertig, du übernimmst es selbst. Die Code-Umgebung dort erreicht nur freigegebene Seiten. |

## Installation

### Claude-App (Web, Desktop)

Am schnellsten: den Link in einen neuen Chat einfügen und Claude bitten, den Skill zu installieren:

```
https://github.com/Ultra-Smashed/lexware-skill

Installier diesen Skill für mich.
```

Oder von Hand:

1. [`lexware.zip`](https://github.com/Ultra-Smashed/lexware-skill/raw/main/lexware.zip) herunterladen (nicht entpacken).
2. In Claude unter **Settings → Capabilities** den Schalter **Code execution and file creation** einschalten. In der neueren Ansicht heißt er **Create and edit files**.
3. **Customize → Skills** öffnen, auf **+** klicken, dann **Create skill → Upload a skill** und die ZIP-Datei wählen.

Als Plugin: **Customize → Plugins**, bei den persönlichen Plugins auf **+**, dann **Add from a repository** und `Ultra-Smashed/lexware-skill` eintragen. Nur so kommt in Claude Desktop der lokale Server für den direkten Zugriff mit.

Die Menünamen stehen hier so, wie Anthropic sie in der Hilfe nennt. In der deutschen Oberfläche können sie übersetzt sein.

### Claude Code

Als Plugin:

```
/plugin marketplace add Ultra-Smashed/lexware-skill
/plugin install lexware@lexware
```

Oder den Ordner kopieren:

```bash
git clone https://github.com/Ultra-Smashed/lexware-skill.git
cp -r lexware-skill/skills/lexware ~/.claude/skills/
```

Mit `cp` bekommst du nur den Skill. Er arbeitet dann über das Skript (braucht Python 3).

## API-Schlüssel

1. **Schlüssel anlegen:** In Lexware Office unter Erweiterungen → Public API (direkt: app.lexware.de/addons/public-api) einen Schlüssel erstellen. Am besten mit Zugriff auf alle Bereiche.
2. **Claude geben:** Beim ersten Mal fragt Claude danach. Schick den Schlüssel einmal, Claude speichert ihn auf deinem Rechner und wiederholt ihn nie.
3. **Sicher bleiben:** Den Schlüssel nur in deinen eigenen Claude-Chat kopieren. Landet er woanders, lösch ihn in Lexware und leg einen neuen an.

Gespeichert wird er in `~/.config/lexware-skill/api-key` (nur für dich lesbar). Alternativ als Umgebungsvariable `LEXWARE_API_KEY`.

## Benutzen

Einfach schreiben, was du brauchst, zum Beispiel:

> Rechnung an Müller GmbH, 8 Stunden Beratung à 95 Euro, Leistung am 12. November.

> Wer hat noch nicht bezahlt? Schreib für alles über 14 Tage eine freundliche Zahlungserinnerung.

> Hier ist mein Sprachmemo vom Termin mit der Bäckerei Schulz. Mach daraus ein Angebot in Lexware.

Der Skill legt alles als Entwurf an. Festschreiben, versenden und als bezahlt markieren machst du in Lexware. Das ist Absicht: Eine festgeschriebene Rechnung lässt sich nicht mehr ändern.

## Dateien

```
skills/lexware/SKILL.md            Ablauf, Module, Regeln
skills/lexware/modes/               eine Anleitung pro Modul
skills/lexware/references/          Nachschlagewerk
skills/lexware/scripts/             Hilfsskripte (Python 3, ohne Zusatzpakete)
mcp/server.mjs                      lokaler Server für das Plugin (Node.js 18+, ohne Zusatzpakete)
.mcp.json                           bindet den Server ins Plugin ein
lexware.zip                       derselbe Skill-Ordner als ZIP für die Claude-App
.claude-plugin/                     plugin.json, marketplace.json
```

Nach einer Änderung im Skill-Ordner die ZIP neu bauen: `cd skills && zip -r ../lexware.zip lexware`.

**Keine Steuerberatung.** Der Skill ordnet, prüft und rechnet. Steuerliche Fragen klärst du mit deinem Steuerberater.

Nicht mit einem echten Konto getestet, gebaut nach der offiziellen API-Dokumentation. Alles Schreibende passiert als Entwurf und erst nach deinem Okay. Fehler gern als Issue melden.

Anleitung: [thanisch.co/wissen/guides/lexware-skill-claude](https://thanisch.co/wissen/guides/lexware-skill-claude)

MIT-Lizenz, siehe [LICENSE](LICENSE). Von [Christopher Thanisch](https://thanisch.co).
