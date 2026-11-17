# Modul Angebot

Ziel: Aus einem Sprachmemo oder Notizen nach dem Kundentermin wird ein fertiges Angebot. Sagt der Kunde Ja, wird mit einem Satz die Rechnung daraus.

## Angebot bauen

1. **Eingabe verstehen.** Sprachmemo (Transkript, Audio in der App diktiert) oder Stichpunkte. Zieh heraus:
   - Kunde und Ansprechpartner
   - Ausgangslage und Ziel des Kunden (1–2 Sätze, für den Einleitungstext)
   - Leistungen als einzelne Positionen
   - Preise, Mengen, Zeitrahmen, Sonderwünsche
2. **Lücken in einer Nachricht klären.** Höchstens fünf Fragen, nummeriert. Typisch: fehlende Preise, Umfang einer Position („wie viele Korrekturschleifen?“), Gültigkeit.
3. **Positionen formulieren.** Jede Position: kurzer Name, in `description` was genau enthalten ist und was nicht. Optionale Leistungen nicht als optionale Positionen anlegen (blockiert später die Umwandlung), sondern als eigenes zweites Angebot oder im Schlusstext erwähnen.
4. **Zusammenfassung zeigen:** Kunde, Positionen mit Preisen, Netto/USt/Brutto (mit Code gerechnet), gültig bis (Standard: 30 Tage).
5. **Nach Okay anlegen:** `POST /v1/quotations` als Entwurf. `introduction` greift das Ziel des Kunden in einem Satz auf („Wie besprochen unterstütze ich euch dabei, …“).
6. **Abgeben:** „Liegt als Entwurf unter Verkauf → Angebote. Prüfen, festschreiben und versenden.“ Dazu ein kurzer Mailtext zum Angebot (3–4 Sätze), wenn der Mensch will.

## Angebot → Rechnung

„Müller hat zugesagt, mach die Rechnung“:
1. Angebot finden: `voucherlist` mit `voucherType=quotation`, `voucherStatus=any`, Kunde filtern. Bei mehreren das neueste nehmen und nachfragen.
2. `GET /v1/quotations/{id}`, Positionen übernehmen. Leistungsdatum oder -zeitraum erfragen, falls nicht klar.
3. Zusammenfassung zeigen, nach Okay `POST /v1/invoices?precedingSalesVoucherId={id}`.
4. Bei 406 (Angebot noch Entwurf, Alternativpositionen, nicht erlaubter Schritt): Rechnung ohne Verknüpfung mit denselben Positionen anlegen, im Einleitungstext „gemäß Angebot {Nummer}“. Sag kurz, warum.

## Ohne Zugang

Gib das Angebot als fertiges Dokument zurück (in der Claude-App als Doc bzw. Datei): Positionen als Tabelle, Einleitung, Schlusstext, Gültigkeit. Dazu: „In Lexware unter Verkauf → Angebot erstellen die Positionen übernehmen.“
