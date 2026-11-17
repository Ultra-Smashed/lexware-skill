---
name: lexware
description: "Erledigt Buchhaltungsaufgaben in Lexware Office (früher lexoffice). Fünf Module. Rechnungen aus einem Satz anlegen („Rechnung an Müller, 8 Stunden Beratung“), Quittungen und Belege hochladen, offene und überfällige Rechnungen finden und Zahlungserinnerungen oder Mahnungen schreiben, Angebote aus Notizen oder einem Sprachmemo bauen und später in eine Rechnung umwandeln, Monatsüberblick mit Umsatz und offenen Posten. Benutze diesen Skill immer, wenn jemand Lexware, Lexware Office, lexoffice, Rechnung schreiben, Angebot erstellen, Beleg hochladen, Quittung erfassen, offene Posten, wer hat noch nicht bezahlt, Zahlungserinnerung, Mahnung oder Monatsabschluss erwähnt, auch bei „create an invoice in Lexware“."
---

# Lexware-Skill

Erledigt den Papierkram in Lexware Office. Alles wird als **Entwurf** angelegt. Festschreiben und Versenden macht der Mensch selbst in Lexware, außer er sagt ausdrücklich etwas anderes.

## Module

| Modul | Wann | Anleitung |
|---|---|---|
| **Rechnung** | „Rechnung an …“, Serienrechnungen, Gutschrift | `modes/rechnung.md` |
| **Belege** | Quittungen, Eingangsrechnungen, Fotos, PDF-Ordner | `modes/belege.md` |
| **Offene Posten** | Wer hat nicht bezahlt, Zahlungserinnerung, Mahnung | `modes/offene-posten.md` |
| **Angebot** | Angebot aus Notizen oder Sprachmemo, Angebot → Rechnung | `modes/angebot.md` |
| **Monatsüberblick** | Umsatz, offene Posten, Top-Kunden, Monatsabschluss | `modes/monatsueberblick.md` |

Lies nur die Anleitung des passenden Moduls. Bei API-Fragen zusätzlich `references/api.md`.

## Schritt 1: Zugang klären (einmal pro Gespräch)

Es gibt drei Wege. Nimm den ersten, der funktioniert, und sag dem Menschen nicht, welche du ausprobiert hast.

**A · Plugin-Werkzeuge.** Gibt es Werkzeuge namens `lexware_status`, `lexware_request`, `lexware_upload_voucher` (Plugin in Claude Desktop oder Claude Code), nutze sie. Ruf zuerst `lexware_status` auf.

**B · Skript.** Kannst du Befehle mit Internetzugang ausführen (Claude Code), nutze `python3 scripts/lexware.py`. Test: `python3 scripts/lexware.py profil`.

**C · Vorbereitungsmodus.** Klappt beides nicht (z. B. in der Claude-App, deren Code-Umgebung Lexware nicht erreicht), bereite alles so vor, dass der Mensch es in Lexware nur noch übernehmen muss. Details in `references/vorbereitung.md`. Sag einmal kurz, warum: „Von hier aus komme ich nicht direkt an Lexware. Ich bereite alles fertig vor, du musst es nur noch übernehmen. In Claude Code oder mit dem Plugin in Claude Desktop lege ich es direkt in Lexware an.“

### API-Schlüssel

Fehlt der Schlüssel (Fehlermeldung „Kein API-Schlüssel“ oder `lexware_status` meldet es):

1. Erkläre: Lexware Office → Erweiterungen → **Public API** (direkt: https://app.lexware.de/addons/public-api) → Schlüssel erstellen. Die Public API gibt es nur im Tarif **XL**, und nur Admins können Schlüssel erstellen.
2. Der Mensch schickt den Schlüssel. Speichere ihn sofort:
   - Weg A: `lexware_set_api_key`
   - Weg B: `printf '%s' 'SCHLÜSSEL' | python3 scripts/lexware.py key-speichern`
3. Wiederhole den Schlüssel nie im Chat, schreib ihn in keine andere Datei und in keinen Befehl außer diesem einen.
4. Empfiehl einmal: Den Schlüssel nicht in fremde Chats kopieren, und ihn in Lexware löschen, falls er irgendwo gelandet ist, wo er nicht hingehört.

### Firmenprofil

Hol beim ersten Schreibzugriff das Profil (`profil` bzw. `lexware_request GET /v1/profile`). Wichtig sind:
- `smallBusiness: true` → Kleinunternehmer nach § 19 UStG. Dann `taxType: "vatfree"` und `taxRatePercentage: 0` auf allen Positionen.
- `taxType` → Standard für `taxConditions.taxType` (meist `net`).

## Schritt 2: Arbeiten

Folge der Modul-Anleitung. Dabei gilt immer:

1. **Erst zeigen, dann schreiben.** Bevor du etwas in Lexware anlegst, zeig eine kurze Zusammenfassung (Kunde, Positionen, Netto, Steuer, Brutto, Datum) und warte auf ein Okay. Ausnahme: reines Lesen (Listen, Überblick) und Belege hochladen, wenn der Mensch das ausdrücklich verlangt hat.
2. **Nur Entwürfe.** Rechnungen, Angebote und Gutschriften ohne `finalize=true`. Mahnungen sind in Lexware immer Entwürfe.
3. **Nichts erfinden.** Fehlen Preis, Menge, Leistungsdatum oder Kunde, frag in einer Nachricht nach allem, was fehlt. Rate keine Preise.
4. **Rechnen.** Beträge rechnet Lexware selbst. Wenn du eine Summe nennst, rechne sie mit Code nach.
5. **Grenzen ehrlich sagen.** Status ändern (bezahlt, storniert), Rechnungen versenden und Abschlagsrechnungen anlegen geht über die API nicht. Sag dann, wo es in Lexware geht.

## Schritt 3: Abgeben

Kurz und konkret:
- was angelegt oder gefunden wurde (Nummer bzw. Entwurf, Kunde, Betrag)
- wo es in Lexware liegt („Verkauf → Rechnungen, Filter Entwurf“)
- der nächste Schritt für den Menschen („prüfen und festschreiben“)
- ein Vorschlag als Satz, den man zurückschicken kann („Schreib Müller eine freundliche Zahlungserinnerung“)

Erwähne nicht, wie der Skill technisch arbeitet. Keine Steuerberatung: Bei Fragen zu Steuersätzen in Sonderfällen (Ausland, Reverse Charge, § 13b) auf den Steuerberater verweisen.
