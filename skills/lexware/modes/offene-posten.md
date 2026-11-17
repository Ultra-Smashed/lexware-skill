# Modul Offene Posten

Ziel: Der Mensch weiß in einer Minute, wer ihm wie viel schuldet, und hat die passende Nachricht fertig.

## Ablauf

1. **Liste holen.** `offen` (alle offenen) und `offen --ueberfaellig` (über Fälligkeit). Bzw. `voucherlist` mit `voucherType=invoice` und `voucherStatus=open` / `overdue`.
2. **Zeigen**, sortiert nach Tagen über Fälligkeit:

   | Kunde | Rechnung | Fällig seit | Offen |
   |---|---|---|---|

   Darunter Summe offen und Summe überfällig. Rechne die Summen mit Code nach.
3. **Stufe vorschlagen** je überfälliger Rechnung:
   - 1–14 Tage: freundliche **Zahlungserinnerung** (Kontrolle, ob die Rechnung angekommen ist)
   - 15–30 Tage: **1. Mahnung**, sachlich, neue Frist 7–10 Tage
   - ab 30 Tage nach der ersten Mahnung: **2. Mahnung**, bestimmt, Hinweis auf nächste Schritte (Mahnbescheid, Inkasso). Nur nennen, wenn der Mensch das wirklich vorhat.
4. **Text schreiben.** Kurz, ohne Vorwurf, mit Rechnungsnummer, Datum, Betrag, neuer Frist (konkretes Datum) und Bankverbindung-Hinweis („wie auf der Rechnung angegeben“). Der Mensch kann den Ton wählen: freundlich, neutral, bestimmt.
5. **Optional in Lexware anlegen.** Will der Mensch die Mahnung als Dokument: `POST /v1/dunnings?precedingSalesVoucherId=<id>` (Body in `references/api.md`). Ist immer ein Entwurf. Danach in Lexware prüfen und versenden.

## Recht in Kürze (nur erwähnen, wenn gefragt oder relevant)

- Verzug tritt spätestens 30 Tage nach Fälligkeit und Zugang der Rechnung ein, bei Privatkunden nur, wenn die Rechnung darauf hinweist (§ 286 Abs. 3 BGB). Mit einer Mahnung nach Fälligkeit tritt Verzug sofort ein.
- Verzugszinsen: Firmenkunden 9 Prozentpunkte, Privatkunden 5 Prozentpunkte über dem Basiszinssatz (§ 288 BGB). Den aktuellen Basiszinssatz bei der Bundesbank nachsehen, nicht aus dem Gedächtnis nennen.
- Firmenkunden: Verzugspauschale 40 € (§ 288 Abs. 5 BGB).
- Keine Rechtsberatung. Bei Streit oder hohen Beträgen: Anwalt oder Inkasso.

## Muster Zahlungserinnerung (freundlich)

Betreff: Zahlungserinnerung Rechnung {Nummer}

Hallo {Name},

ich hoffe, bei euch läuft alles gut. Beim Durchsehen meiner Buchhaltung ist mir aufgefallen, dass die Rechnung {Nummer} vom {Datum} über {Betrag} noch offen ist. Vielleicht ist sie im Postfach untergegangen?

Ich wäre dir dankbar, wenn du den Betrag bis zum {Frist} überweist. Falls du schon bezahlt hast, betrachte diese Nachricht als erledigt.

Viele Grüße
{Absender}
