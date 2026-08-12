# Probleemoplossing

## Wekker-card is leeg of “Custom element doesn't exist”

Installeer v1.10.0 of nieuwer opnieuw met `bash install.sh --restart`. De correcte combinatie is:

```text
Bestand: /config/www/community/wekker-card/wekker-card.js
Module:  /local/community/wekker-card/wekker-card.js?v=1.10.0
Kaart:   custom:wekker-card
```

De mapnaam is bewust volledig lowercase; Home Assistant OS maakt onderscheid tussen `Wekker-card` en `wekker-card`. In storage mode registreert de module zichzelf via de officiële Lovelace-API zodra een beheerder het frontend opent. De installer schrijft dan geen `lovelace.resources` naar `configuration.yaml`, zodat de melding “Lovelace is running in storage mode” niet terugkomt. Vernieuw daarna de browsercache volledig met `Ctrl+F5` of sluit de Home Assistant-app helemaal af en open hem opnieuw.

Controleer bij **Ontwikkelaarstools → Staten** of `input_boolean.sonos_alarm_enabled` bestaat. Ontbreekt die entity, dan is het package niet geladen; controleer in dat geval het Home Assistant-logboek en `/config/packages/wekker_card.yaml`. Gebruik hier een underscore: `wekker-card.yaml` veroorzaakt de fout `invalid slug wekker-card`.

## Geen geluid

Controleer of de ingevulde entity exact bestaat, de speaker online is en de URI rechtstreeks door Sonos bereikbaar is. Test `media_player.play_media` handmatig in Ontwikkelaarstools. Controleer ook of een vereiste muziekdienst in de Sonos-app is gekoppeld. Gebruik bij een radiostation de directe stream-URI, niet de webpagina.

## Status verandert maar volume niet

Controleer de attributen van de media-playerentity en test `media_player.volume_set`. Kijk in **Instellingen → Automatiseringen → Traces** bij “Sonos wekker - gebeurtenisgestuurde controller”. Een ongeldige entity-ID verschijnt in het Home Assistant-logboek.

## Alarm start op de verkeerde tijd

Controleer **Instellingen → Systeem → Algemeen → Tijdzone** en de hosttijd. De berekeningen gebruiken Home Assistants lokale `now()`, inclusief zomer-/wintertijd.

## Snooze hervat niet

Bekijk `input_datetime.sonos_alarm_snooze_until`, `input_select.sonos_alarm_status` en de automation-trace. Een gebruiker of andere automation die interne helpers wijzigt kan herstel verstoren.

## Favoriet werkt niet

Schakel de Sonos Favorites-sensor in bij de Sonos-entiteiten en gebruik de sleutel (bijvoorbeeld `FV:2/31`), niet alleen de zichtbare naam. Kies mediatype `favorite_item_id`.

Als de dropdown leeg blijft, controleer dan of het station in de Sonos-app werkelijk onder Mijn Sonos/Favorieten staat, of de Favorites-sensor in Home Assistant is ingeschakeld en of deze sensor een attribuut `items` bevat. Druk vervolgens in de kaart op **Ververs spelers, lampen en favorieten**.

## Configuratiefout na kopiëren

Controleer dat `homeassistant:` maar één keer op topniveau voorkomt en dat `packages: !include_dir_named packages` daar correct ingesprongen staat. Gebruik altijd Home Assistants configuratiecontrole vóór een restart.

## Home Assistant wordt traag of loopt vast

Installeer v1.10.0 opnieuw met `bash install.sh --restart`. Deze versie bevat geen `time_pattern`-triggers, geen periodieke discovery en geen periodiek bijgewerkte statussensoren. Alleen de noodzakelijke volume- en lichtstappen lopen tijdens een actieve opbouw.
