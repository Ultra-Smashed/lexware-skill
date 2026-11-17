# Modul Rechnung

Ziel: Aus einem Satz wird ein fertiger Rechnungsentwurf in Lexware.

## Ablauf

1. **Satz zerlegen.** Kunde, Leistung, Menge, Einheit, Preis, Leistungsdatum oder -zeitraum, Zahlungsziel.
   - „8 Stunden Beratung“ → quantity 8, unitName „Stunde“, name „Beratung“
   - „Pauschale Logo 1.200“ → quantity 1, unitName „Pauschal“, netAmount 1200
   - Preise ohne Zusatz sind netto, außer der Mensch sagt „brutto“ oder ist Kleinunternehmer.
2. **Kunde finden.** `kontakt NAME` bzw. `GET /v1/contacts?name=NAME`.
   - Ein Treffer: nimm ihn.
   - Mehrere: zeig sie kurz und frag, welcher.
   - Keiner: frag nach Firmenname, Anschrift und E-Mail und leg den Kontakt nach Okay an (`POST /v1/contacts` mit `roles: {"customer": {}}`). Alternativ Rechnung mit Adresse ohne Kontakt.
3. **Preis.** Fehlt er: Gibt es einen Artikel mit passendem Namen (`GET /v1/articles`)? Dann dessen Preis vorschlagen. Hat der Mensch dem Kunden schon einmal dieselbe Leistung berechnet (`voucherlist` mit `voucherType=invoice`, dann `GET /v1/invoices/{id}`), schlag diesen Preis vor. Sonst fragen.
4. **Leistungsdatum.** Pflichtangabe auf jeder Rechnung. Fehlt es, nimm den letzten Tag des Vormonats nur, wenn der Mensch „für letzten Monat“ o. ä. sagt, sonst frag. Zeitraum → `serviceperiod`.
5. **Zusammenfassung zeigen** (Tabelle):

   | | |
   |---|---|
   | Kunde | Müller GmbH |
   | Leistung | 8 Std. Beratung à 95,00 € |
   | Leistungsdatum | 12.11.2026 |
   | Netto / USt 19 % / Brutto | 760,00 € / 144,40 € / 904,40 € |
   | Zahlungsziel | 14 Tage |

   Summen mit Code nachrechnen. Bei Kleinunternehmern keine USt-Zeile, stattdessen „Kleinunternehmer, keine USt“.
6. **Nach Okay anlegen.** Body nach `references/api.md`, als Datei speichern, dann `request POST /v1/invoices --data rechnung.json` (bzw. `lexware_request`). Ohne `finalize`.
7. **Abgeben:** „Liegt als Entwurf in Lexware unter Verkauf → Rechnungen. Prüfen, festschreiben, versenden.“

## Serienrechnungen

„Rechnung an alle Retainer-Kunden, je 1.500 € für November“:
1. Kundenliste klären (Namen nennen lassen oder aus früheren Rechnungen ableiten und bestätigen lassen).
2. Eine Tabelle mit allen Rechnungen zeigen, ein Okay für alle.
3. Nacheinander anlegen (das Limit von 2 Anfragen pro Sekunde beachtet das Skript).
4. Am Ende Liste: Kunde, Betrag, angelegt ja/nein.

Für Rechnungen, die jeden Monat gleich sind, auf die wiederkehrenden Rechnungen in Lexware hinweisen (Vorlage einmal in Lexware anlegen). Die API kann solche Vorlagen nur lesen.

## Gutschrift

„Gutschrift über 200 € an Müller wegen Verzögerung“ → `POST /v1/credit-notes` mit derselben Struktur (ohne `shippingConditions`-Pflicht laut Doku nicht nötig, aber schadet nicht). Bezieht sie sich auf eine Rechnung: `?precedingSalesVoucherId=<rechnungs-id>`.

## Qualität

- Positionsnamen kurz und klar, Details in `description`.
- Einheit passend: Stunde, Tag, Stück, Pauschal, Monat.
- Einleitungstext und Schlusstext nur setzen, wenn der Mensch etwas Bestimmtes will. Sonst nimmt Lexware die Standardtexte des Accounts.
