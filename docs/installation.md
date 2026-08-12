# Installatie

Voor de geautomatiseerde variant zie [Automatische installatie](automatic-installation.md). De stappen hieronder zijn de handmatige methode.

## Vereisten

- Home Assistant met toegang tot de YAML-configuratiemap;
- één bereikbare Sonos-speaker via de officiële Sonos-integratie;
- een back-up van de Home Assistant-configuratie;
- correcte Home Assistant-tijdzone.

De Sonos-integratie vereist werkende netwerkcommunicatie. Controleer in **Instellingen → Apparaten & diensten → Sonos** dat de speaker beschikbaar is en test handmatig volume en media.

## Package installeren

Voeg, als packages nog niet actief zijn, dit eenmaal toe aan `/config/configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Als er al een `homeassistant:`-blok bestaat, voeg alleen de regel `packages:` binnen dat blok toe. Kopieer daarna:

```text
packages/wekker_card.yaml → /config/packages/wekker_card.yaml
```

De underscore in `wekker_card.yaml` is verplicht: met `!include_dir_named` wordt de bestandsnaam de package-slug, en Home Assistant accepteert daarin geen koppelteken.

Ga naar **Ontwikkelaarstools → YAML → Configuratie controleren**. Los iedere gemelde fout op en herstart pas daarna Home Assistant. Helpers uit dit package worden automatisch als YAML-entiteiten aangemaakt; maak ze niet nogmaals via de UI.

## Dashboard installeren

Maak onder **Instellingen → Dashboards** een nieuw dashboard in YAML-modus of kopieer de inhoud via de Raw configuration editor. Gebruik `dashboard/wekker-card.yaml` als basis. De kaarten verwijzen naar automatisch aangemaakte entities.

## Eerste configuratie

1. Open in de retrokaart **INSTELLINGEN** en kies je speaker uit de automatisch gevulde Sonos-lijst.
2. Vul een stream of media-ID in en kies een passend mediatype.
3. Begin met startvolume 1–2% en normaal volume maximaal 10%.
4. Kies een testtijd enkele minuten vooruit en tijdelijk een opbouwtijd van 2 minuten.
5. Zet **Wekker aan** aan en volg op het tabblad **Wekker** de tijd, status en het volume.

## Verificatie vóór dagelijks gebruik

Test achtereenvolgens: normale opbouw; doelvolume op wektijd; snooze; tweede snooze; stop; restart tijdens opbouw; restart tijdens snooze. Controleer na iedere restart dat status, volume en snoozetijd binnen enkele seconden correct zijn.
