# Drehwerkantrieb eines Baggeroberwagens

Zweistufiges Planetengetriebe mit integrierter Lamellen-Haltebremse zur Positionierung und
Arretierung des Oberwagens eines 30-Tonnen-Kettenbaggers. Entstanden als Semesterprojekt im
Modul Konstruktionslehre 3 an der TU Berlin (SoSe 2025), bearbeitet im Dreierteam.

## Aufgabenstellung

Der Oberwagen soll mit 7 min⁻¹ (± 2 %) gedreht werden können. Angetrieben wird über einen
Hydraulikmotor; der gesamte Antrieb muss in einem Bauraum von 400 × 400 mm untergebracht werden
und für eine Serienfertigung von 200 Einheiten ausgelegt sein.

| Kenngröße | Wert |
|---|---|
| Abtriebsdrehzahl Oberwagen | 6,863 min⁻¹ |
| Gesamtübersetzung | 27,95 |
| Abtriebsmoment am Ritzel | 7.715 Nm |
| Eingangsmoment (Hydraulikmotor) | 276 Nm |
| Aufbau | zwei Planetenstufen + Drehkranzübersetzung |
| Bremse | nasslaufende Lamellenbremse, hydraulisch gelüftet |

## Konstruktion

![Schnittansicht](bilder/schnittansicht.png)

*Schnittansicht: links die Lamellenbremse mit Federpaket und Lüftkolben, in der Mitte die beiden
Planetenstufen, rechts die Abtriebswelle in Kegelrollenlagern (O-Anordnung) mit Abtriebsritzel.*

![Isometrische Ansicht](bilder/isometrie.png)

*Gesamtbaugruppe: Topfgehäuse mit Deckelteilung, Motorflansch links, Anschlussplatte und
Abtriebsritzel rechts.*

Ausgewählte konstruktive Merkmale:

- **Radialer Lastausgleich nach dem Flexpin-Prinzip** — die Planetenachsen sind elastisch
  nachgiebig ausgeführt, sodass sich die Planetenräder unter Last selbsttätig ausrichten und
  die Zahnkräfte gleichmäßig verteilt werden. Der Planetenträger bleibt dabei steif.
- **Konstruktive Trennung von Bremse und Getrieberaum** über angepasste Flansch- und
  Dichtungsauslegung; die Bremse ist im eingebauten Zustand nachstellbar.
- **Fest-Los-Lagerung** zur Vermeidung von Zwängungen, Abtriebswelle in O-Anordnung.
- **Direkte Integration des Hydraulikmotors** in das Gehäuse über die Flanschgeometrie des
  Herstellers, Abdichtung statisch über O-Ring, Zentrierung über H7/h6.

## Mein Beitrag

Das Projekt wurde im Team bearbeitet, mit klar aufgeteilten Arbeitspaketen. Mein Schwerpunkt lag
auf der konstruktiven Umsetzung und der zeichnerischen Dokumentation:

- Prinzipskizzen der Konzeptvarianten und erste CAD-Modelle zur Bauraumbewertung
- Aufbau der Gesamtbaugruppe in Solid Edge, einschließlich Integration von Bremse, Kupplung
  und Lagerstellen
- Zeichnungsableitung: Schnittdarstellungen, Einzelheiten, isometrische Ansicht
- Festlegung und Kennzeichnung von Passungen und Toleranzen, Erstellung der Passungstabelle
- Erstellung der Stückliste (85 Positionen)
- Ausarbeitung der Montageanleitung mit Explosionsdarstellungen der neun Montageschritte
- Export der Zeichnungen und des STEP-Modells

Die rechnerische Auslegung (Verzahnung, Wellen, Lager, Welle-Nabe-Verbindungen, Bremse) wurde von
einem Teammitglied in KISSsoft/KISSsys durchgeführt, die Projektplanung und die schriftliche
Dokumentation von einem weiteren. Die konstruktiven Entscheidungen wurden gemeinsam abgestimmt.

## Grundlagen der Auslegung

Die Konstruktion wurde gegen folgende Normen und Richtlinien ausgelegt und nachgewiesen:

| Bereich | Norm / Richtlinie |
|---|---|
| Verzahnung | DIN 3990 |
| Wellen | DIN 743 |
| Passverzahnungen | DIN 5480 |
| Passfedern | DIN 6885 |
| Keilwellen | DIN ISO 14 |
| Pressverbände | DIN 7190 |
| Wälzlager | DIN ISO 281 |
| Bremse | VDI 2241 |
| Schraubenverbindungen | VDI 2230 |
| Toleranzen | DIN EN ISO 286 |

**Werkzeuge:** Solid Edge (CAD, Zeichnungsableitung), KISSsoft/KISSsys (Auslegung, im Team),
LaTeX (Dokumentation)

---

*Zusammenbauzeichnung und STEP-Modell sind hier nicht veröffentlicht,
da es sich um eine bewertete Studienleistung handelt. Auf Anfrage zeige ich die Unterlagen gerne
im Gespräch.*

*Projektteam: Alpay Kocatürk, Abdelrahman Askar, Ali Basta — Veröffentlichung der Abbildungen
mit Zustimmung aller Beteiligten.*
