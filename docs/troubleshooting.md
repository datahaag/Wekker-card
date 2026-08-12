# Probleemoplossing

## Integratie niet zichtbaar

Controleer of HACS de repository als **Integratie** heeft toegevoegd en of `/config/custom_components/wekker_card/manifest.json` bestaat. Herstart Home Assistant en vernieuw de browser volledig.

## Kaart niet zichtbaar

Controleer bij **Instellingen → Apparaten & diensten** dat Wekker-card is toegevoegd. De integratie registreert `/wekker-card/wekker-card.js` automatisch; er hoort geen handmatige bron onder **Dashboards → Bronnen** te staan.

## Geen Sonos-spelers of favorieten

Druk in het instellingentabblad op **VERVERS**. Alleen spelers van de officiële Sonos-integratie worden getoond. Voor favorieten moet de Favorites-sensor van Sonos zijn ingeschakeld en moet het station eerst in de Sonos-app aan Mijn Sonos/Favorieten zijn toegevoegd.

## Oude en nieuwe wekker lopen tegelijk

Schakel de oude package uit of verwijder `/config/packages/wekker_card.yaml` en herstart Home Assistant. Versie 2.0 importeert de oude instellingen, maar verwijdert gebruikersbestanden niet automatisch.

## Stabiliteit

De integratie gebruikt alleen exacte start-, doel- en snoozecallbacks. Er draait geen periodieke statuscontrole. Tijdens een actieve opbouw worden alleen de noodzakelijke Sonos- en lichtcommando's verstuurd.
