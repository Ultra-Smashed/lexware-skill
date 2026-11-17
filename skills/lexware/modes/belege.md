# Modul Belege

Ziel: Quittungen und Eingangsrechnungen landen sauber in Lexware.

## Mit Zugang (Weg A oder B)

1. **Dateien sammeln.** Einzelne Dateien oder ein Ordner. Erlaubt: pdf, jpg, png, xml, je max. 5 MB. Größere Fotos vorher verkleinern (z. B. mit Python/Pillow auf 2000 px lange Kante, JPEG Qualität 85). HEIC vorher in JPG umwandeln.
2. **Kurz ansehen.** Öffne jedes Bild bzw. die erste PDF-Seite und notiere Datum, Händler, Betrag. So merkst du, wenn etwas kein Beleg ist (Screenshot, privates Foto) oder doppelt ist. Private Belege nicht hochladen, sondern nachfragen.
3. **Hochladen.** `python3 scripts/lexware.py beleg DATEI …` bzw. `lexware_upload_voucher` je Datei. Hat der Mensch „lad alle hoch“ gesagt, frag nicht nochmal nach.
4. **Abgeben:** Tabelle mit Datei, Datum, Händler, Betrag, hochgeladen ja/nein. Dann: „Lexware liest die Belege jetzt aus. Unter Belege → Zu prüfen kurz kontrollieren und die Kategorie bestätigen.“

## Ohne Zugang (Vorbereitungsmodus)

1. Lies jedes Foto bzw. PDF und erfasse: Datum, Händler, Rechnungsnummer (falls vorhanden), Netto, USt-Satz, USt-Betrag, Brutto, Zahlungsart, vermutete Kategorie (z. B. Bürobedarf, Bewirtung, Software, Reisekosten).
2. Benenne die Dateien einheitlich: `JJJJ-MM-TT_Händler_Betrag.ext` (z. B. `2026-11-03_Amazon_49,90.pdf`).
3. Gib zurück:
   - die Tabelle (als Tabelle im Chat oder, bei mehr als 10 Belegen, als CSV/XLSX-Datei),
   - eine ZIP mit den umbenannten Dateien, wenn du Dateien erzeugen kannst,
   - die Anleitung: „In Lexware unter Belege → Beleg hochladen alle Dateien auf einmal hineinziehen. Oder an deine Lexware-Belegadresse mailen (Einstellungen → Belegempfang).“

## Hinweise für den Menschen (nur wenn passend)

- Bewirtungsbelege brauchen Anlass und Teilnehmer. Frag danach und schreib es in die Tabelle.
- Fehlt auf einem Beleg die USt oder der Händler, markiere ihn in der Tabelle.
- Thermopapier verblasst: lieber gleich digital ablegen.
