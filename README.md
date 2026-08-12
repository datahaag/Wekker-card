# Wekker-card voor Home Assistant

Een gebeurtenisgestuurde slimme wekker voor één Sonos-speaker, volledig gebouwd met native Home Assistant-functionaliteit en de officiële Sonos-integratie. De wekker ondersteunt afzonderlijke week- en weekendtijden, een automatisch berekende volume-opbouw, onbeperkt snoozen, stoppen van alleen de actuele cyclus, een fysieke knop en een compleet Lovelace-dashboard.

## Functies

- normale tijdkiezers voor maandag–vrijdag en zaterdag–zondag;
- algemene aan/uit-schakelaar;
- instelbare Sonos-entiteit, radio-/muziek-URI en mediatype;
- automatisch gevulde keuzelijst met uitsluitend spelers uit de Sonos-integratie;
- instelbaar startvolume, normaal volume, opbouwduur (standaard 15 minuten) en stapinterval;
- automatisch berekende volumestappen die exact op de wektijd eindigen;
- standaard snooze van 9 minuten, onbeperkt herhaalbaar;
- SNOOZE en STOP op dashboard én ondersteuning voor een fysieke knop;
- planning en herstel op exacte `input_datetime`-triggers, zonder periodieke statuscontrole;
- geen custom integration of externe custom-cardafhankelijkheden vereist;
- gescheiden kaarttabbladen voor dagelijkse bediening en instellingen;
- prominente actuele tijd en eerstvolgende wektijd.
- zelfstandige retro `custom:wekker-card` die op ieder Lovelace-dashboard kan worden geplaatst;
- canonieke installatie onder `/config/www/community/wekker-card`;
- grote fysieke-look AAN/UIT-schakelaar die duidelijk maakt of het weekschema actief is.
- kleinere permanente weergave van zowel de weekdag- als weekendwektijd;
- optionele lichtwekker met alle lampen en schakelaars; `LAMP` en `SCHAKELAAR` zijn duidelijk gemarkeerd in de keuzelijst.
- automatische keuze uit officiële Mijn Sonos/Favorieten, inclusief opgeslagen radiostations;
- handmatige stream-URI blijft als alternatief beschikbaar.
- HACS-compatibele dashboardinstallatie met automatische `/hacsfiles/`-bronregistratie.

## Architectuurkeuze

De officiële Sonos-integratie ondersteunt de benodigde media-playeracties en URI's. Home Assistant plant de volgende start-, doel- en snoozetijd met exacte tijdtriggers. Er zijn geen `time_pattern`-pollers, periodieke discovery-runs of periodiek bijgewerkte statussensoren. Alleen tijdens een actieve opbouw worden op het gekozen interval noodzakelijke volume- en lichtcommando's uitgevoerd. Zie [architectuur](docs/architecture.md).

## Snelle installatie

### Via HACS (aanbevolen voor de kaart en dashboardbron)

Voeg `https://github.com/datahaag/wekker-card` in HACS toe als aangepaste
repository van het type **Dashboard** en download **Wekker-card**. HACS plaatst
de kaart onder `www/community/wekker-card` en beheert de bron
`/hacsfiles/wekker-card/wekker-card.js`.

HACS installeert alleen de frontendkaart. Installeer de native wekkerlogica met
de onderstaande ZIP-opdracht en voeg daarbij `--hacs` toe, zodat de installer de
door HACS beheerde kaart en bron niet overschrijft:

```bash
cd /config && unzip -oq wekker-card-v1.10.0.zip && bash /config/wekker-card/install.sh --hacs --restart
```

Zie [GitHub en HACS](docs/github-hacs.md) voor de volledige publicatie-,
migratie- en installatie-instructies.

### Automatisch op Home Assistant OS/Hassio

Kopieer `wekker-card-v1.10.0.zip` naar `/config`, open de **Terminal & SSH**-add-on en plak één opdracht:

```bash
cd /config && unzip -oq wekker-card-v1.10.0.zip && bash /config/wekker-card/install.sh --restart
```

Na een geslaagde configuratiecontrole verwijdert de installer automatisch zowel
`/config/wekker-card-v1.10.0.zip` als de tijdelijke map `/config/wekker-card`.
De geïnstalleerde configuratie, custom card en back-up blijven behouden.

Deze ene regel pakt de release uit, maakt een back-up, activeert packages, registreert een afzonderlijk YAML-dashboard, installeert en registreert de retro custom card, draait `ha core check` en herstart alleen bij een geldige configuratie. Zie [automatische installatie](docs/automatic-installation.md).

### Handmatig

1. Configureer de officiële Sonos-integratie en controleer dat de speaker vanuit Home Assistant speelt.
2. Activeer packages in `configuration.yaml`:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

3. Kopieer `packages/wekker_card.yaml` naar `/config/packages/`. De underscore is verplicht omdat Home Assistant package-namen als slug valideert.
4. Controleer de configuratie en herstart Home Assistant.
5. Importeer `dashboard/wekker-card.yaml` als YAML-dashboard.
6. Stel de speakerhelper op het dashboard in op jouw echte Sonos-entity-ID.
7. Vul een bereikbare stream-/muziek-URI en het juiste mediatype in, zet veilige volumes en schakel de wekker in.

Lees vóór ingebruikname de volledige [installatie](docs/installation.md) en voer de testprocedure uit.

## Repository-indeling

```text
packages/                    Home Assistant-package met alle logica en helpers
dashboard/                   Standaard Lovelace-dashboard
dist/                        Door HACS te downloaden wekker-card.js
hacs.json                    HACS-repositorymanifest
.github/workflows/           Automatische HACS- en JavaScriptvalidatie
examples/                    Fysieke-knopautomations en mediavoorbeelden
docs/                        Installatie, configuratie, bediening en techniek
tests/                       Statische YAML- en algoritmetests
```

## Documentatie

- [Installatie](docs/installation.md)
- [Automatische installatie](docs/automatic-installation.md)
- [GitHub en HACS](docs/github-hacs.md)
- [Configuratie](docs/configuration.md)
- [Dashboard](docs/dashboard.md)
- [Retro custom card](docs/custom-card.md)
- [Bediening](docs/operation.md)
- [Probleemoplossing](docs/troubleshooting.md)
- [Technische architectuur](docs/architecture.md)

## Compatibiliteit en afhankelijkheden

Ontworpen voor recente Home Assistant-versies met de moderne automation-syntax (`triggers`/`actions`) en de officiële Sonos-integratie. Er zijn geen externe Python-pakketten nodig. De meegeleverde custom card kan rechtstreeks of via HACS worden geïnstalleerd. Sonos-muziekdiensten moeten vooraf in de Sonos-app zijn ingericht.

## Veilig testen

Gebruik eerst een laag normaal volume, een wektijd enkele minuten in de toekomst en een korte opbouwduur. Controleer SNOOZE, herhaalde snooze, STOP en een Home Assistant-restart in elke fase. Gebruik dit project niet als enige alarm voor veiligheidskritische afspraken voordat het in jouw netwerk aantoonbaar betrouwbaar werkt.

## Versies en bijdragen

Zie [CHANGELOG.md](CHANGELOG.md). Maak voor een stabiele release een semantische tag, bijvoorbeeld `v1.0.0`. Wijzigingen horen code, documentatie en tests in dezelfde commit bij te werken.

## Licentie

[MIT](LICENSE). Home Assistant en Sonos zijn handelsmerken van hun respectieve eigenaren. Dit project bevat geen code van externe projecten.

## Primaire technische bronnen

- [Home Assistant: officiële Sonos-integratie](https://www.home-assistant.io/integrations/sonos/)
- [Home Assistant: time-trigger](https://www.home-assistant.io/docs/automation/trigger/#time-trigger)
- [Home Assistant: input text en state restore](https://www.home-assistant.io/integrations/input_text/)
