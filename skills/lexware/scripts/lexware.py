#!/usr/bin/env python3
"""Kleiner Client für die Lexware Office Public API (ohne Zusatzpakete).

API-Schlüssel: Umgebungsvariable LEXWARE_API_KEY oder Datei
~/.config/lexware-skill/api-key (eine Zeile). Den Schlüssel nie ausgeben.

Befehle:
  key-speichern            liest den Schlüssel von stdin und speichert ihn (chmod 600)
  profil                   Firmenprofil (zeigt u. a. Kleinunternehmer, Steuerart)
  kontakt NAME             Kontakte nach Name suchen
  offen [--ueberfaellig]   offene bzw. überfällige Ausgangsrechnungen
  monat JJJJ-MM            Monatsüberblick (Umsatz, offen, überfällig, Ausgaben)
  beleg DATEI [DATEI ...]  Belege hochladen (pdf, jpg, png, xml, max. 5 MB)
  pdf TYP ID ZIEL          PDF laden, TYP = invoices | quotations | dunnings | credit-notes
  request METHODE PFAD [--data DATEI|-] [--query k=v ...]
                           beliebiger Aufruf, z. B. request POST /v1/invoices --data rechnung.json

Basis-URL: https://api.lexware.io . Limit: 2 Anfragen pro Sekunde, wird hier eingehalten.
"""
import json
import mimetypes
import os
import sys
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

BASE = os.environ.get("LEXWARE_BASE_URL", "https://api.lexware.io")
KEY_FILE = Path.home() / ".config" / "lexware-skill" / "api-key"
_last_call = [0.0]


def api_key():
    key = os.environ.get("LEXWARE_API_KEY", "").strip()
    if not key and KEY_FILE.exists():
        key = KEY_FILE.read_text().strip()
    if not key:
        sys.exit("FEHLER: Kein API-Schlüssel. Setze LEXWARE_API_KEY oder führe "
                 "'lexware.py key-speichern' aus (Schlüssel über stdin).")
    return key


def _wait():
    gap = time.time() - _last_call[0]
    if gap < 0.55:
        time.sleep(0.55 - gap)
    _last_call[0] = time.time()


def call(method, path, body=None, query=None, raw=None, content_type=None, accept="application/json"):
    url = BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    headers = {"Authorization": "Bearer " + api_key(), "Accept": accept}
    data = None
    if raw is not None:
        data = raw
        headers["Content-Type"] = content_type
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    for attempt in range(4):
        _wait()
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
                if accept != "application/json":
                    return payload
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(1.5 * (attempt + 1))
                continue
            detail = e.read().decode(errors="replace")[:2000]
            sys.exit(f"FEHLER {e.code} bei {method} {path}: {detail}")
        except urllib.error.URLError as e:
            sys.exit(f"FEHLER: Lexware nicht erreichbar ({e.reason}). Ist Netzwerkzugriff erlaubt?")


def voucherlist(vtype, status, max_pages=40):
    out = []
    for page in range(max_pages):
        res = call("GET", "/v1/voucherlist", query={
            "voucherType": vtype, "voucherStatus": status,
            "page": page, "size": 250, "sort": "voucherDate,DESC"})
        out += res.get("content", [])
        if res.get("last", True):
            break
    return out


def eur(x):
    return f"{(x or 0):,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def tage_seit(datum):
    if not datum:
        return None
    d = datetime.fromisoformat(datum.replace("Z", "+00:00")).date()
    return (date.today() - d).days


def cmd_key_speichern(_):
    key = sys.stdin.read().strip()
    if not key:
        sys.exit("FEHLER: Kein Schlüssel auf stdin.")
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    KEY_FILE.write_text(key + "\n")
    os.chmod(KEY_FILE, 0o600)
    print(f"Gespeichert in {KEY_FILE}")


def cmd_profil(_):
    p = call("GET", "/v1/profile")
    keep = {k: p.get(k) for k in ("companyName", "smallBusiness", "taxType", "businessFeatures", "distanceSalesPrinciple")}
    print(json.dumps(keep, ensure_ascii=False, indent=2))


def cmd_kontakt(args):
    if not args:
        sys.exit("Aufruf: kontakt NAME")
    name = " ".join(args)
    if len(name) < 3:
        sys.exit("Name braucht mindestens 3 Zeichen.")
    res = call("GET", "/v1/contacts", query={"name": name, "size": 25})
    for c in res.get("content", []):
        comp = (c.get("company") or {}).get("name")
        pers = c.get("person") or {}
        label = comp or " ".join(x for x in (pers.get("firstName"), pers.get("lastName")) if x)
        rollen = ",".join(k for k in (c.get("roles") or {}).keys())
        mails = c.get("emailAddresses") or {}
        mail = next((v[0] for v in mails.values() if v), "")
        print(f"{c['id']}\t{label}\t{rollen}\t{mail}")
    if not res.get("content"):
        print("Kein Kontakt gefunden.")


def cmd_offen(args):
    status = "overdue" if "--ueberfaellig" in args else "open"
    rows = voucherlist("invoice", status)
    if not rows:
        print("Keine " + ("überfälligen" if status == "overdue" else "offenen") + " Rechnungen.")
        return
    summe = 0
    print("Nummer\tKunde\tDatum\tFällig\tTage über Fälligkeit\tOffen\tID")
    for r in rows:
        ueber = tage_seit(r.get("dueDate"))
        summe += r.get("openAmount") or 0
        print(f"{r.get('voucherNumber')}\t{r.get('contactName')}\t{(r.get('voucherDate') or '')[:10]}\t"
              f"{(r.get('dueDate') or '')[:10]}\t{ueber if ueber and ueber > 0 else 0}\t{eur(r.get('openAmount'))}\t{r['id']}")
    print(f"\nSumme offen: {eur(summe)} ({len(rows)} Rechnungen)")


def cmd_monat(args):
    if not args:
        sys.exit("Aufruf: monat JJJJ-MM")
    monat = args[0]

    def im_monat(r):
        return (r.get("voucherDate") or "")[:7] == monat

    rechnungen = [r for r in voucherlist("invoice", "any") if im_monat(r) and r.get("voucherStatus") not in ("draft", "voided")]
    gutschriften = [r for r in voucherlist("creditnote", "any") if im_monat(r) and r.get("voucherStatus") not in ("draft", "voided")]
    ausgaben = [r for r in voucherlist("purchaseinvoice", "any") if im_monat(r) and r.get("voucherStatus") != "voided"]
    offen = voucherlist("invoice", "open")
    ueberfaellig = voucherlist("invoice", "overdue")
    kunden = {}
    for r in rechnungen:
        kunden[r.get("contactName") or "ohne Kontakt"] = kunden.get(r.get("contactName") or "ohne Kontakt", 0) + (r.get("totalAmount") or 0)
    out = {
        "monat": monat,
        "umsatz_brutto": round(sum(r.get("totalAmount") or 0 for r in rechnungen) - sum(r.get("totalAmount") or 0 for r in gutschriften), 2),
        "anzahl_rechnungen": len(rechnungen),
        "ausgaben_brutto": round(sum(r.get("totalAmount") or 0 for r in ausgaben), 2),
        "offen_gesamt": round(sum(r.get("openAmount") or 0 for r in offen), 2),
        "ueberfaellig_gesamt": round(sum(r.get("openAmount") or 0 for r in ueberfaellig), 2),
        "ueberfaellig_anzahl": len(ueberfaellig),
        "top_kunden": sorted(([k, round(v, 2)] for k, v in kunden.items()), key=lambda x: -x[1])[:5],
        "ungepruefte_belege": len(voucherlist("any", "unchecked")),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_beleg(args):
    if not args:
        sys.exit("Aufruf: beleg DATEI [DATEI ...]")
    for name in args:
        p = Path(name)
        if not p.is_file():
            print(f"ÜBERSPRUNGEN {name}: Datei nicht gefunden")
            continue
        if p.stat().st_size > 5 * 1024 * 1024:
            print(f"ÜBERSPRUNGEN {name}: größer als 5 MB")
            continue
        if p.suffix.lower() not in (".pdf", ".jpg", ".jpeg", ".png", ".xml"):
            print(f"ÜBERSPRUNGEN {name}: nur pdf, jpg, png, xml")
            continue
        boundary = uuid.uuid4().hex
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\nvoucher\r\n"
                f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{p.name}\"\r\n"
                f"Content-Type: {ctype}\r\n\r\n").encode() + p.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        res = call("POST", "/v1/files", raw=body, content_type=f"multipart/form-data; boundary={boundary}")
        print(f"OK {p.name}\tvoucherId={res.get('voucherId')}")


def cmd_pdf(args):
    if len(args) != 3:
        sys.exit("Aufruf: pdf TYP ID ZIEL")
    typ, vid, ziel = args
    data = call("GET", f"/v1/{typ}/{vid}/file", accept="application/pdf")
    Path(ziel).write_bytes(data)
    print(f"Gespeichert: {ziel}")


def cmd_request(args):
    if len(args) < 2:
        sys.exit("Aufruf: request METHODE PFAD [--data DATEI|-] [--query k=v ...]")
    method, path, rest = args[0].upper(), args[1], args[2:]
    body, query = None, {}
    i = 0
    while i < len(rest):
        if rest[i] == "--data":
            src = rest[i + 1]
            body = json.load(sys.stdin) if src == "-" else json.loads(Path(src).read_text())
            i += 2
        elif rest[i] == "--query":
            k, _, v = rest[i + 1].partition("=")
            query[k] = v
            i += 2
        else:
            sys.exit(f"Unbekannt: {rest[i]}")
    print(json.dumps(call(method, path, body=body, query=query or None), ensure_ascii=False, indent=2))


BEFEHLE = {
    "key-speichern": cmd_key_speichern, "profil": cmd_profil, "kontakt": cmd_kontakt,
    "offen": cmd_offen, "monat": cmd_monat, "beleg": cmd_beleg, "pdf": cmd_pdf, "request": cmd_request,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in BEFEHLE:
        print(__doc__)
        sys.exit(1)
    BEFEHLE[sys.argv[1]](sys.argv[2:])
