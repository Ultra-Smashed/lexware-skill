# Vorbereitungsmodus (ohne direkten Zugang)

Gilt, wenn weder Plugin-Werkzeuge noch ein Skript mit Internetzugang verfügbar sind, z. B. in der Claude-App im Browser oder auf dem Handy. Die Code-Umgebung dort erreicht nur freigegebene Seiten wie GitHub oder PyPI, nicht Lexware.

Grundsatz: Der Mensch soll in Lexware nur noch übernehmen, nicht mehr nachdenken.

| Modul | Was du lieferst |
|---|---|
| Rechnung | Fertige Rechnungsdaten als Tabelle (Kunde, Positionen mit Name, Beschreibung, Menge, Einheit, Einzelpreis, USt-Satz, Leistungsdatum, Zahlungsziel) und die Klickfolge: Verkauf → Rechnung erstellen → Kunde wählen → Positionen übernehmen |
| Belege | Tabelle aller Belege + umbenannte Dateien als ZIP + Upload-Hinweis (siehe `modes/belege.md`) |
| Offene Posten | Der Mensch exportiert die offenen Posten aus Lexware (Verkauf → Rechnungen → Filter „Überfällig“ → Export) oder macht einen Screenshot. Du sortierst, rechnest und schreibst die Erinnerungstexte |
| Angebot | Fertiges Angebot als Dokument (Positionen, Einleitung, Schlusstext, Gültigkeit) |
| Monatsüberblick | Der Mensch exportiert die Belegliste des Monats als CSV/Excel oder schickt Screenshots der Auswertungen. Du rechnest mit Code und fasst zusammen |

Am Ende einmal der Hinweis: „In Claude Code oder mit dem Plugin in Claude Desktop kann ich das direkt in Lexware anlegen. Anleitung im Repo.“
