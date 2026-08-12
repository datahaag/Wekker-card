# Wekker-card voor Home Assistant

[![Validate](https://github.com/datahaag/Wekker-card/actions/workflows/validate.yml/badge.svg)](https://github.com/datahaag/Wekker-card/actions/workflows/validate.yml)

Wekker-card is één HACS-integratie met een retro dashboardkaart, een gebeurtenisgestuurde Sonos-wekker en een optionele lichtwekker. Vanaf versie 2.0 zijn geen ZIP, Terminal-opdracht, package of wijzigingen in `configuration.yaml` meer nodig.

![Wekker-card bevat een retro digitale wekker met een apart instellingentabblad](https://raw.githubusercontent.com/datahaag/Wekker-card/main/docs/wekker-card-preview.svg)

## Functies

- aparte week- en weekendwektijd;
- duidelijke actuele tijd, volgende wektijd en beide ingestelde tijden;
- Sonos-speler kiezen uit de officiële Sonos-integratie;
- Radio 538, Qmusic, Sublime en andere opgeslagen Mijn Sonos/Favorieten kiezen;
- geleidelijke volume-opbouw zonder periodieke statuscontrole;
- optionele lamp die dezelfde opbouw volgt;
- alle `light.*`- en `switch.*`-entiteiten, duidelijk gemarkeerd als `LAMP` of `SCHAKELAAR`;
- onbeperkte snooze en STOP voor alleen de actuele wekcyclus;
- persistente instellingen die na een herstart worden hersteld;
- kaart en backend samen onder `custom_components/wekker_card`.

## Installeren: één geheel via HACS

1. Open **HACS** in Home Assistant.
2. Open rechtsboven **⋮ → Aangepaste repositories**.
3. Voeg `https://github.com/datahaag/Wekker-card` toe als type **Integratie**.
4. Open **Wekker-card** en kies **Downloaden**.
5. Herstart Home Assistant.
6. Open **Instellingen → Apparaten & diensten → Integratie toevoegen**.
7. Zoek **Wekker-card** en kies **Toevoegen**.

De integratie registreert de frontendkaart zelf. Er hoeft geen dashboardbron te worden aangemaakt.

## Kaart toevoegen

Open een dashboard, kies **Dashboard bewerken → Kaart toevoegen** en selecteer **Wekker-card (Sonos retro)**. Handmatig kan ook:

```yaml
type: custom:wekker-card
```

## Wekker bedienen

Open de kaarttab **WEKKER** en druk op de brede knop **WEKKER UIT**. De knop verandert in **WEKKER AAN** en het statuslampje wordt groen. **STOP** beëindigt alleen de huidige cyclus; het weekschema blijft ingeschakeld. **SNOOZE** pauzeert de actieve cyclus gedurende de ingestelde snoozeduur.

Open **INSTELLINGEN** om de Sonos-speler, favoriet of stream, tijden, volumes, lichtbron en helderheid te kiezen. Druk op **VERVERS** wanneer een nieuwe Sonos-speler, favoriet, lamp of schakelaar is toegevoegd.

## Migratie vanaf 1.x

De integratie leest bestaande `input_*`-instellingen van het oude `packages/wekker_card.yaml` eenmalig in. Daarna gebruikt versie 2.0 eigen persistente entiteiten. Schakel de oude package vervolgens uit of verwijder hem om te voorkomen dat twee wekkers tegelijk actief worden. De integratie schakelt de oude algemene wekkerhelper bij de eerste start uit wanneer deze nog aanstaat.

## Architectuur

De backend plant alleen exacte callbacks voor de starttijd, wektijd en eventuele snoozetijd. Alleen tijdens een actieve volume-/lichtopbouw worden noodzakelijke apparaatcommando's verstuurd. Er is geen `time_pattern`-poller en er worden geen periodieke statussen vastgelegd.

De runtime bestaat volledig uit:

```text
custom_components/wekker_card/
```

## Veilig gebruik

Test eerst met een laag volume, een tijd enkele minuten in de toekomst en een korte opbouw. Controleer Sonos, licht, SNOOZE, STOP en herstel na een Home Assistant-herstart voordat je de wekker voor belangrijke afspraken gebruikt.

## Licentie

[MIT](LICENSE). Home Assistant en Sonos zijn handelsmerken van hun respectieve eigenaren.
