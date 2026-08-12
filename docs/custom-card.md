# Retro custom card

## Wat de kaart bevat

`custom:wekker-card` is één zelfstandige Lovelace-kaart met:

- een ouderwetse donkere wekkerkast met schroeven, voetjes en drukknoppen;
- een rode digitale display met actuele tijd, datum en volgende wektijd;
- een kleinere vaste regel met de weekdag- en weekendwektijd;
- een grote schakelaar met statuslampje voor het weekschema;
- status-, volume- en snoozemeters;
- SNOOZE en STOP;
- een interne tab **INSTELLINGEN** met speler, media, wektijden, volumes en timing.
- een optionele lichtwekker met automatisch gevonden lampen én schakelaars; de lijst markeert ieder item duidelijk als `LAMP` of `SCHAKELAAR`.
- een keuzelijst met de officiële Mijn Sonos/Favorieten en opgeslagen radiostations.

De kaart gebruikt geen externe JavaScript-library of custom integration en kan rechtstreeks of als HACS-dashboardelement worden geïnstalleerd.

## De wekker aanzetten

Open de kaarttab **WEKKER** en druk eenmaal op de brede schakelaar **WEKKER UIT**. De knop verandert in **WEKKER AAN**, het lampje wordt groen en in de display licht `ALARM` op. Daarmee staat het volledige week-/weekendschema aan.

Dit verschilt van STOP:

- **WEKKER AAN/UIT** schakelt het hele terugkerende schema;
- **STOP** beëindigt alleen de huidige wekcyclus en laat het schema voor de volgende dag aan;
- **SNOOZE** onderbreekt alleen de actieve cyclus voor de ingestelde snoozeduur.

## Op een ander dashboard plaatsen

Na installatie staat de module globaal geladen. Voeg via **Dashboard bewerken → Kaart toevoegen → Handmatig** deze minimale configuratie toe:

```yaml
type: custom:wekker-card
```

De kaart verschijnt ook als **Wekker-card (Sonos retro)** in de custom-cardsectie van de kaartkiezer. Je mag dezelfde kaart op meerdere dashboards plaatsen; alle exemplaren bedienen dezelfde helpers en blijven direct gesynchroniseerd.

## Optionele naam

```yaml
type: custom:wekker-card
name: SLAAPKAMERWEKKER
```

Alle entity-ID's hebben werkende projectstandaarden. Gevorderde gebruikers kunnen ze in de kaartconfig overschrijven, bijvoorbeeld:

```yaml
type: custom:wekker-card
enabled_entity: input_boolean.sonos_alarm_enabled
snooze_script: script.sonos_alarm_snooze
stop_script: script.sonos_alarm_stop
```

## Lichtwekker

Open **INSTELLINGEN → LICHTWEKKER**, zet de lichtwekker op **AAN**, selecteer een lamp en kies de gewenste helderheid op de normale wektijd.

Een `light.*`-lamp gebruikt dezelfde berekende stappen als Sonos:

- aan het begin van de opbouw is de lamp uit (0%);
- gedurende de ingestelde opbouwtijd neemt de helderheid stapsgewijs toe;
- exact op de wektijd staat de lamp op de ingestelde doelhelderheid;
- tijdens snooze gaat de lamp uit;
- na snooze keert hij direct terug naar de doelhelderheid, zonder nieuwe opbouw;
- STOP en het uitschakelen van de wekker zetten de lamp uit;
- na een Home Assistant-restart tijdens de opbouw wordt de actieve ramp vanaf het actuele niveau hervat.

De keuzelijst wordt eenmaal na startup uit alle `light.*`- en `switch.*`-entities opgebouwd. Gebruik de verversknop op het instellingentabblad na het toevoegen of verwijderen van een lamp of schakelaar.

Ook alle `switch.*`-entities staan in dezelfde lijst. Omdat een schakelaar geen helderheidsniveau ondersteunt, gaat hij aan zodra de opbouw start en uit bij snooze, STOP of het uitschakelen van de wekker. De opties tonen `LAMP · …` en `SCHAKELAAR · …`, zodat het verschil direct zichtbaar is.

## Radio uit Mijn Sonos kiezen

1. Voeg het gewenste station, bijvoorbeeld Radio 538, Qmusic of Sublime, in de Sonos-app toe aan **Mijn Sonos/Favorieten**.
2. Controleer in Home Assistant bij **Instellingen → Apparaten & diensten → Sonos → Entiteiten** of de Favorites-sensor is ingeschakeld. Deze sensor is in de officiële integratie standaard uitgeschakeld.
3. Open de kaarttab **INSTELLINGEN**.
4. Kies het station bij **Sonos-favoriet of radiostation**.

De kaart zet automatisch:

```text
media_content_type = favorite_item_id
media_content_id   = het officiële FV:…-ID
```

Je hoeft dus geen streamadres op te zoeken. De geselecteerde wekbron staat klein op het hoofdscherm. Gebruik **Handmatige URI / eigen stream** alleen voor een directe URL of andere bron die niet in Mijn Sonos staat.

## Handmatige module-installatie

Wanneer je de automatische installer niet gebruikt:

1. maak `/config/www/community/wekker-card` aan en kopieer `custom_cards/wekker-card/wekker-card.js` naar `/config/www/community/wekker-card/wekker-card.js`;
2. voeg de URL in de standaard storage mode bij **Instellingen → Dashboards → menu rechtsboven → Resources** toe als **JavaScript-module**. Gebruik het onderstaande YAML-alternatief uitsluitend wanneer onder `lovelace:` expliciet `resource_mode: yaml` staat:

   ```yaml
   lovelace:
     resource_mode: yaml
     resources:
       - url: /local/community/wekker-card/wekker-card.js?v=1.10.0
         type: module
   ```

3. controleer de configuratie en herstart Home Assistant;
4. open rechtstreeks `/local/community/wekker-card/wekker-card.js?v=1.10.0`; daar moet JavaScript en geen 404 verschijnen;
5. vernieuw de browser/app volledig als een oude gecachte versie zichtbaar blijft.

Alle letters in `community/wekker-card` moeten klein zijn: Home Assistant OS is hoofdlettergevoelig. Vanaf versie 1.7.0 is alleen `custom:wekker-card` geldig. Schrijf in storage mode geen `resources:` onder `lovelace:` in `configuration.yaml`; Home Assistant verwacht die dan in de UI. De v1.10.0-installer handelt directe installatie en HACS storage mode afzonderlijk af.
