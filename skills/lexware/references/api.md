# Lexware Office Public API · Spickzettel

Quelle: https://developers.lexware.io/docs/ (Stand November 2026). Bei Fehlern dort nachsehen.

- Basis-URL: `https://api.lexware.io`
- Header: `Authorization: Bearer <Schlüssel>`, `Accept: application/json`, bei Body `Content-Type: application/json`
- Limit: 2 Anfragen pro Sekunde, sonst HTTP 429 (Skript und Plugin warten automatisch)
- Public API nur im Tarif XL

## Wichtige Endpunkte

| Zweck | Aufruf |
|---|---|
| Profil | `GET /v1/profile` (smallBusiness, taxType) |
| Kontakte suchen | `GET /v1/contacts?name=…` (mind. 3 Zeichen), auch `email=`, `number=`, `customer=true` |
| Kontakt anlegen | `POST /v1/contacts` |
| Artikel | `GET /v1/articles` |
| Rechnung anlegen | `POST /v1/invoices` (Entwurf), `?finalize=true` = offen |
| Rechnung aus Vorgänger | `POST /v1/invoices?precedingSalesVoucherId=<id>` |
| Angebot anlegen | `POST /v1/quotations` |
| Mahnung anlegen | `POST /v1/dunnings?precedingSalesVoucherId=<rechnungs-id>` (immer Entwurf) |
| Gutschrift | `POST /v1/credit-notes` |
| PDF | `GET /v1/{invoices|quotations|dunnings|credit-notes}/{id}/file` (nicht für Entwürfe, dann 409) |
| Zahlungsstand | `GET /v1/payments/{voucherId}` (openAmount, paymentStatus) |
| Belegliste | `GET /v1/voucherlist?voucherType=…&voucherStatus=…` (beide Pflicht) |
| Beleg hochladen | `POST /v1/files` multipart, Felder `file` und `type=voucher` (pdf, jpg, png, xml, max. 5 MB) |
| Buchungskategorien | `GET /v1/posting-categories` |
| Wiederkehrende Vorlagen | `GET /v1/recurring-templates` (nur lesen) |

`voucherType`: `salesinvoice`, `salescreditnote`, `purchaseinvoice`, `purchasecreditnote`, `invoice`, `creditnote`, `orderconfirmation`, `quotation`, `downpaymentinvoice`, `deliverynote`, `any`
`voucherStatus`: `draft`, `open`, `overdue`, `paid`, `paidoff`, `voided`, `transferred`, `sepadebit`, `accepted`, `rejected`, `unchecked`, `any` (`overdue` nicht kombinierbar)
Paging: `size` bis 250, `page` ab 0. Antwortfelder u. a. `voucherNumber`, `voucherDate`, `dueDate`, `contactName`, `totalAmount`, `openAmount`.

## Rechnung (POST /v1/invoices)

Pflicht: `voucherDate`, `address`, `lineItems`, `totalPrice`, `taxConditions`, `shippingConditions`.

```json
{
  "voucherDate": "2026-11-17T00:00:00.000+01:00",
  "address": { "contactId": "UUID-AUS-KONTAKTSUCHE" },
  "lineItems": [
    {
      "type": "custom",
      "name": "Beratung",
      "description": "Strategieworkshop am 12.11.2026",
      "quantity": 8,
      "unitName": "Stunde",
      "unitPrice": { "currency": "EUR", "netAmount": 95.00, "taxRatePercentage": 19 }
    }
  ],
  "totalPrice": { "currency": "EUR" },
  "taxConditions": { "taxType": "net" },
  "shippingConditions": { "shippingType": "service", "shippingDate": "2026-11-12T00:00:00.000+01:00" },
  "paymentConditions": {
    "paymentTermLabel": "Zahlbar innerhalb von 14 Tagen ohne Abzug.",
    "paymentTermDuration": 14
  },
  "title": "Rechnung",
  "introduction": "Vielen Dank für Ihren Auftrag. Wir berechnen Ihnen folgende Leistungen:",
  "remark": "Vielen Dank für die gute Zusammenarbeit."
}
```

- Ohne Kontakt: `"address": { "name": "Firma GmbH", "street": "…", "zip": "…", "city": "…", "countryCode": "DE" }`
- `shippingType`: `service` (Datum), `serviceperiod` (Datum + `shippingEndDate`), `delivery`, `deliveryperiod`, `none`
- Kleinunternehmer: `taxConditions.taxType: "vatfree"`, alle `taxRatePercentage: 0`
- `type`: `custom` (frei), `service`/`material` (mit Artikel-`id`), `text` (nur Text, nur `name`/`description`)
- Brutto-Preise: `taxType: "gross"` und `grossAmount` statt `netAmount`
- Max. 300 Positionen. `paymentConditions`, `title`, `introduction`, `remark` sind optional (sonst Standardtexte des Accounts).
- Datumsformat immer mit Zeitzone wie oben.

## Angebot (POST /v1/quotations)

Wie Rechnung, aber mit `expirationDate` (Pflicht) und ohne `shippingConditions`-Pflicht.

```json
{
  "voucherDate": "2026-11-17T00:00:00.000+01:00",
  "expirationDate": "2026-12-17T00:00:00.000+01:00",
  "address": { "contactId": "UUID" },
  "lineItems": [ { "type": "custom", "name": "…", "quantity": 1, "unitName": "Pauschal", "unitPrice": { "currency": "EUR", "netAmount": 1200, "taxRatePercentage": 19 } } ],
  "totalPrice": { "currency": "EUR" },
  "taxConditions": { "taxType": "net" },
  "introduction": "…",
  "remark": "…"
}
```

## Angebot → Rechnung

`POST /v1/invoices?precedingSalesVoucherId=<angebots-id>` mit vollständigem Rechnungs-Body (Positionen aus dem Angebot übernehmen: `GET /v1/quotations/{id}`, dann `lineItems`, `address`, `taxConditions` kopieren, `shippingConditions` ergänzen).

- 406 = Schritt in der Belegkette nicht erlaubt, Angebot noch Entwurf, oder Angebot hat Alternativ-/Optional-Positionen. Dann: Rechnung ohne `precedingSalesVoucherId` mit denselben Positionen anlegen und im `introduction`-Text auf das Angebot verweisen („gemäß Angebot AG0012“).

## Mahnung (POST /v1/dunnings?precedingSalesVoucherId=<rechnungs-id>)

Pflicht wie Rechnung (inkl. `shippingConditions`), `taxConditions.taxType` muss zur Rechnung passen. Die offenen Positionen werden aus der Rechnung übernommen; zusätzliche Positionen (z. B. Mahngebühr) als `custom` anhängen. Immer Entwurf. Typischer Body:

```json
{
  "voucherDate": "2026-11-17T00:00:00.000+01:00",
  "address": { "contactId": "UUID" },
  "lineItems": [ { "type": "custom", "name": "Mahngebühr", "quantity": 1, "unitName": "Pauschal", "unitPrice": { "currency": "EUR", "netAmount": 5, "taxRatePercentage": 0 } } ],
  "totalPrice": { "currency": "EUR" },
  "taxConditions": { "taxType": "net" },
  "shippingConditions": { "shippingType": "none" },
  "title": "Zahlungserinnerung",
  "introduction": "…"
}
```

Mahngebühren nur, wenn der Mensch das will. Bei Firmenkunden darf nach § 288 Abs. 5 BGB eine Verzugspauschale von 40 € verlangt werden, sobald Verzug vorliegt.

## Belege hochladen

`POST /v1/files` mit `file` und `type=voucher`. Antwort 202 mit `id` und `voucherId`. Lexware liest den Beleg per Texterkennung aus (Status `blank` → `unchecked`). Doppelte Dateien werden erkannt (gleiche IDs zurück). Danach prüft der Mensch den Beleg in Lexware unter „Belege → Zu prüfen“. Einkaufsbelege lassen sich über die API nicht vollständig bearbeiten.

## Was nicht geht

Status ändern (bezahlt markieren, stornieren), E-Mail-Versand, Abschlagsrechnungen anlegen, Bankumsätze lesen. Dafür in Lexware selbst klicken.
