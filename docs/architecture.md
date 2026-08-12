# Technische architectuur

## Besluit

De wekker gebruikt uitsluitend ingebouwde Home Assistant-functionaliteit en de officiële Sonos-integratie. Een custom integration voegt hier geen noodzakelijke capability toe en zou installatie, upgrades en foutopsporing juist zwaarder maken.

De native bouwstenen zijn:

- Home Assistant package-YAML voor helpers, scripts en automations;
- de officiële `sonos`/`media_player`-entiteit voor afspelen, pauzeren, stoppen en volume;
- persistente helpers voor instellingen en cyclestatus;
- exacte tijdtriggers op de geplande start-, doel- en snoozetijd;
- een standaard Lovelace-dashboard zonder custom cards.

Vanaf versie 1.3.0 bevat de repository daarnaast een eigen, dependencyvrije Lovelace custom card. Dit is uitsluitend een presentatielaag: alle planning, persistentie en restart-herstel blijven in de native Home Assistant-package. De kaart roept bestaande helper- en scriptacties aan en kan daarom zonder custom integration worden verwijderd of vervangen zonder de wekkerlogica te veranderen.

De module wordt als `/config/www/community/wekker-card/wekker-card.js` geïnstalleerd en via `frontend.extra_module_url` geladen. In de standaard storage mode registreert de module zichzelf daarna via Home Assistants officiële Lovelace WebSocket-API. Bij expliciet `resource_mode: yaml` schrijft de installer de module onder `lovelace.resources`. Daardoor blijft de resource zichtbaar in de kaartkiezer zonder storage mode te wijzigen of `.storage` rechtstreeks te bewerken. Oude en dubbele moduleverwijzingen worden geconsolideerd naar één lowercase URL.

De radiokeuze gebruikt geen hardcoded streamcatalogus. Een discovery-automation leest de `items`-mapping uit de door de officiële Sonos-integratie geleverde Favorites-sensor. De zichtbare favorietennaam wordt gekoppeld aan het stabiele Sonos `favorite_item_id`; de bestaande media-URI-helper bewaart dat ID restart-bestendig. Hiermee blijft de Sonos-app de bron van waarheid voor beschikbare radiostations en muziekdiensten.

## Geen periodieke statuscontrole

In rust draait geen minuut- of secondentimer. De volgende wekcyclus wordt één keer naar `input_datetime.sonos_alarm_start` en `input_datetime.sonos_alarm_target` geschreven; Home Assistant activeert de bijbehorende automation exact op die tijden. Tijdens de actieve opbouw wacht één script tussen noodzakelijke volume- en lichtstappen. Dit is apparaatbesturing, geen statuspolling. Bij een restart wordt de planning één keer opnieuw berekend.

## Toestandsmodel

| Status | Betekenis | Sonos-uitkomst |
|---|---|---|
| `idle` | Geen actieve cyclus | Niet door de wekker gewijzigd |
| `ramping` | Binnen de opbouwperiode vóór wektijd | Speelt; berekend oplopend volume |
| `ringing` | Wektijd bereikt | Speelt op normaal wekvolume |
| `snoozed` | Snooze actief tot absolute eindtijd | Gepauzeerd en volume 0 |

`STOP` schrijft de unieke sleutel van de huidige cyclus naar `input_text.sonos_alarm_stopped_cycle`. Daardoor wordt alleen die cyclus onderdrukt; het weekschema en de algemene aan/uit-schakelaar blijven intact.

## Cyclus en kalender

De doelwektijd komt op maandag t/m vrijdag uit `input_datetime.sonos_alarm_weekday_time` en op zaterdag/zondag uit `input_datetime.sonos_alarm_weekend_time`. De cyclus-ID is de lokale datum plus de gekozen wektijd. Een cyclus begint `opbouwtijd` minuten vóór de doelwektijd. Als de opbouw over middernacht loopt, onderzoekt de berekening zowel vandaag als morgen, zodat bijvoorbeeld een maandagwekker van 00:05 op zondag 23:50 begint.

## Volume-algoritme

Met startvolume `S`, normaal volume `N`, opbouwduur `D` seconden, interval `I` seconden en verstreken tijd `t`:

```text
aantal_stappen = ceil(D / I)
voltooide_stappen = floor(t / I)
volume = S + (N - S) * voltooide_stappen / aantal_stappen
```

Het resultaat wordt begrensd tussen `S` en `N`. Op de exacte doelwektijd wordt het volume expliciet op `N` gezet. Het interval bepaalt dus de stapfrequentie; de stapgrootte wordt automatisch afgeleid. Zowel stijgende als gelijke start-/eindwaarden zijn toegestaan; de UI en documentatie adviseren `S ≤ N`.

## Synchrone lichtwekker

Een optioneel gekozen `light`-entity gebruikt exact dezelfde `aantal_stappen` en `voltooide_stappen` als de audio. Het startniveau is vast 0%; het eindniveau is `input_number.sonos_alarm_light_brightness`. Bij ramping is de doelhelderheid `eindniveau × voltooide_stappen / aantal_stappen`. Op de wektijd en na snooze wordt het eindniveau expliciet gezet. Snooze, STOP en het uitschakelen van het schema zetten de geselecteerde lamp uit.

De lampkeuze wordt net als de Sonos-keuze in een dynamische dropdown aangeboden en in een aparte `input_text`-helper persistent opgeslagen. Hierdoor kan de dropdown na restart veilig opnieuw worden opgebouwd zonder de selectie kwijt te raken.

## Gebeurtenisgestuurde planning en restart-herstel

De controller reageert alleen op:

- Home Assistant-start;
- het wijzigen van de aan/uitstand, wektijden of opbouwduur;
- de exact geplande starttijd, doelwektijd of snooze-eindtijd;
- instellingen die tijdens een actieve ramp worden gewijzigd.

Een restart tijdens de opbouw berekent één keer het actuele rampniveau en vervolgt vandaar. Een restart tijdens snooze behoudt de deadline via een `input_datetime` met datum én tijd. Er zijn geen `time_pattern`-triggers en geen periodiek veranderende template-sensoren.

Een interne initialisatievlag laat de package één keer veilige standaardwaarden invullen. De instelhelpers hebben bewust geen `initial:`-optie, omdat Home Assistant zo hun laatst opgeslagen waarde herstelt in plaats van gebruikerskeuzes bij iedere restart te overschrijven.

## Afspelen en idempotentie

Afspelen wordt alleen gestart bij de overgang naar `ramping`, eenmaal bij startup-herstel tijdens de ramp, of na afloop van snooze. Een onbereikbare of gestopte speaker veroorzaakt geen onbeperkte herhaalpogingen. Rampstappen wijzigen volume of licht alleen wanneer dat voor de gekozen opbouw nodig is.

De digitale secondenklok, volgende-wektijdweergave, volumeweergave, lichtweergave en snooze-afteller worden lokaal in de Lovelace-kaart berekend uit bestaande entities. Daarvoor worden geen extra Home Assistant-statussen aangemaakt of periodiek opgeslagen.

## Fysieke knop

De aanbevolen mapping is:

- kort indrukken: `script.sonos_alarm_context_button` — snooze tijdens `ramping`/`ringing`, stop tijdens `snoozed`, geen actie tijdens `idle`;
- lang indrukken: `script.sonos_alarm_stop` — altijd de huidige cyclus stoppen.

Omdat de event/entity-vorm per Zigbee-, Z-Wave-, Matter- of ESPHome-knop verschilt, bevat de repository aanpasbare voorbeelden in plaats van een apparaatgebonden integratie.

## Grenzen en aannames

- Er is precies één Sonos `media_player` voor deze wekker.
- De Sonos kan de gekozen URI bereiken en de benodigde muziekdienst is vooraf in de Sonos-app geconfigureerd.
- Home Assistant gebruikt de juiste lokale tijdzone.
- Na `ringing` blijft de muziek spelen totdat de gebruiker stopt; de cyclus wordt niet automatisch na een arbitraire duur beëindigd.
- Omdat de speaker exclusief voor de wekker is, wordt geen Sonos-snapshot hersteld.
