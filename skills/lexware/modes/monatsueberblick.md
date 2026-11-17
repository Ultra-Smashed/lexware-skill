# Modul Monatsüberblick

Ziel: In 30 Sekunden sehen, wie der Monat gelaufen ist und was noch offen ist.

## Ablauf

1. Monat klären (Standard: letzter abgeschlossener Monat; „diesen Monat“ = laufender).
2. `python3 scripts/lexware.py monat JJJJ-MM` bzw. dieselben Abfragen über `lexware_request` (Belegliste für Rechnungen, Gutschriften, Eingangsrechnungen, offen, überfällig, ungeprüfte Belege).
3. Zeigen:
   - **Umsatz** (brutto, Rechnungen minus Gutschriften, nur festgeschriebene) und Anzahl Rechnungen
   - **Ausgaben** laut Eingangsbelegen
   - **Offen** und **überfällig** (Summe, Anzahl)
   - **Top 5 Kunden** im Monat
   - **Ungeprüfte Belege** in Lexware
   - Vergleich zum Vormonat, wenn der Mensch das will (zweiten Monat genauso abfragen)
4. **Drei To-dos** daraus ableiten, z. B. „3 überfällige Rechnungen anmahnen“, „12 Belege in Lexware prüfen“, „Rechnung für Projekt X fehlt noch?“
5. Wenn Dateien möglich sind und der Mensch es will: eine kleine HTML-Seite mit den Zahlen als Kacheln.

## Hinweise

- Beträge sind brutto. Für Netto oder Gewinn auf die Auswertungen in Lexware verweisen (Auswertungen → EÜR bzw. BWA).
- Keine steuerliche Bewertung. Bei „Wie viel Steuern muss ich zahlen?“ auf Steuerberater bzw. die Lexware-Auswertungen verweisen.
