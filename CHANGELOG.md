# Changelog

Alle opvallende wijzigingen worden in dit bestand bijgehouden volgens Keep a Changelog; versies volgen Semantic Versioning.

## [1.10.0] - 2026-08-12

### Added

- Officiële HACS-dashboardstructuur met `hacs.json`, `dist/wekker-card.js` en een HACS-validatieworkflow.
- Nieuwe installatiemodus `--hacs` waarbij HACS eigenaar blijft van het kaartbestand en de `/hacsfiles/`-dashboardbron.
- Volledige Nederlandse instructies voor publiceren op GitHub en installeren als aangepaste HACS-repository.

### Fixed

- De kaart herkent een bestaande HACS-bron en overschrijft die niet meer met een `/local/`-bron.
- Een dubbele oude lokale resource wordt verwijderd terwijl de HACS-resource behouden blijft.

## [1.9.2] - 2026-08-12

### Fixed

- Na een geslaagde configuratiecontrole worden de release-ZIP en de tijdelijke map `/config/wekker-card` automatisch verwijderd.
- De installer verwijdert uitsluitend de exact gecontroleerde installatiemap; permanente configuratiebestanden en back-ups blijven behouden.
- Bij een mislukte installatie blijven ZIP en installatiemap beschikbaar voor herstel en diagnose.

## [1.9.1] - 2026-08-12

### Fixed

- In Lovelace storage mode schrijft de installer geen ongeldig `lovelace.resources`-blok meer naar `configuration.yaml`.
- De kaart registreert of actualiseert zichzelf automatisch via Home Assistants officiële Lovelace WebSocket-API zodra een beheerder het frontend opent.
- Oude en dubbele Wekker-cardresources worden automatisch geconsolideerd naar de canonieke lowercase v1.9.1-URL.
- Bij expliciet `resource_mode: yaml` blijft de installer de resource correct onder `lovelace.resources` registreren.
- De lichtwekkerlijst bevat nu alle `light.*`- en `switch.*`-entities, duidelijk gemarkeerd als `LAMP` of `SCHAKELAAR`.
- Schakelaars volgen aan/uit, snooze en STOP; dimbare lampen behouden de geleidelijke helderheidsopbouw.

## [1.9.0] - 2026-08-12

### Changed

- Alle `time_pattern`-triggers en periodiek bijgewerkte template-sensoren zijn verwijderd.
- De wekker plant exacte start-, doel- en snoozetijden en reageert verder alleen op wijzigingen en Home Assistant-start.
- Spelers, alle `light`-entities en Sonos-favorieten worden eenmaal na startup geladen en daarna alleen via de nieuwe handmatige verversknop.
- De kaart berekent tijd, volgende wektijd en snooze lokaal en leest volume, licht en status rechtstreeks uit bestaande entities.

### Fixed

- Dropdowns hebben vaste geldige beginopties en worden alleen herschreven wanneer hun opties werkelijk veranderen.

## [1.8.2] - 2026-08-12

### Fixed

- De controller draait niet meer iedere seconde en gebruikt `mode: single` om overlappende of telkens herstartende runs te voorkomen.
- Sonos wordt bij een niet-spelende of onbereikbare speaker niet meer onbeperkt opnieuw aangestuurd.
- Volume-, licht- en statusacties worden alleen uitgevoerd wanneer de doeltoestand werkelijk afwijkt.
- De actuele tijd en snooze-seconden lopen lokaal in de kaart; Home Assistant schrijft hiervoor geen seconde-status meer naar Recorder.
- De module wordt behalve via `frontend.extra_module_url` ook als officiële Lovelace-resource geregistreerd, zodat de kaartkiezer hem betrouwbaar ziet.

## [1.8.1] - 2026-08-11

### Fixed

- Packagebestand gecorrigeerd naar `/config/packages/wekker_card.yaml`; Home Assistant weigert de ongeldige package-slug `wekker-card`.
- Installer verwijdert na back-up automatisch het foutieve v1.8.0-bestand `/config/packages/wekker-card.yaml`.
- Installatietest controleert nu expliciet de Home Assistant-slugregel en de migratie van het ongeldige packagebestand.

## [1.8.0] - 2026-08-11

### Fixed

- Het canonieke, hoofdlettergevoelige modulepad is nu overal `/config/www/community/wekker-card/wekker-card.js`.
- De installer controleert na het kopiëren of de module bestaat en daadwerkelijk `custom:wekker-card` registreert.
- Verwijzingen naar zowel `Wekker-card` als eerdere modulepaden worden vóór registratie verwijderd.

### Changed

- v1.8.0 hernoemde het package naar `/config/packages/wekker-card.yaml`; dit bleek geen geldige Home Assistant-package-slug en is in v1.8.1 teruggedraaid naar `wekker_card.yaml`.
- Dashboardbron, doelbestand en Lovelace-sleutel heten nu consequent `wekker-card`.
- De installer migreert automatisch vanaf `sonos_smart_alarm.yaml` en bewaart het oude bestand in de gedateerde back-up.

## [1.7.0] - 2026-08-11

### Fixed

- Wekker-card wordt nu canoniek vanuit `/config/www/community/Wekker-card/wekker-card.js` geladen.
- Installer verwijdert dubbele en verouderde moduleverwijzingen voordat één correcte verwijzing wordt geschreven.
- Oude modulebestanden worden na back-up gericht van de schijf verwijderd.

### Removed

- Compatibiliteitsalias `custom:sonos-smart-alarm-card`; alleen `custom:wekker-card` wordt nog geregistreerd.
- Oude modulepaden `/config/www/sonos-smart-alarm-card.js` en `/config/www/Wekker-card/wekker-card.js`.

## [1.6.0] - 2026-08-11

### Changed

- Publiek Lovelace-type hernoemd naar `custom:wekker-card`.
- Kaartbron verplaatst naar `custom_cards/Wekker-card/wekker-card.js`.
- Hassio-installatiepad gewijzigd naar `/config/www/Wekker-card/wekker-card.js`.
- Installer migreert automatisch het oude modulepad naar Wekker-card.

### Compatibility

- De nieuwe module registreert ook het oude `custom:sonos-smart-alarm-card` als compatibiliteitsalias.

## [1.5.0] - 2026-08-11

### Added

- Dynamische dropdown met officiële Mijn Sonos/Favorieten.
- Ondersteuning voor als Sonos-favoriet opgeslagen stations zoals Radio 538, Qmusic en Sublime.
- Zichtbare wekbron op het hoofdscherm.
- Handmatige URI-optie naast Sonos-favorieten.

### Changed

- Selectie van een favoriet stelt automatisch `favorite_item_id` en het officiële Sonos-ID in.
- Invoer van een eigen URI schakelt automatisch terug naar mediatype `music`.

## [1.4.0] - 2026-08-11

### Added

- Kleine permanente weergave van weekdag- en weekendwektijd op het hoofdscherm.
- Optionele lichtwekker met automatisch gevulde lampenlijst.
- Instelbare doelhelderheid van 1–100% met een opbouw vanaf 0%.
- Actuele lichtniveaumeter op de retrokaart.

### Changed

- Snooze, STOP, uitschakelen en restart-herstel sturen nu desgewenst Sonos en lamp synchroon aan.

## [1.3.0] - 2026-08-11

### Added

- Zelfstandige `custom:sonos-smart-alarm-card` zonder externe JavaScript-afhankelijkheden.
- Retro wekkerdesign met digitale rode klokdisplay, kast, knoppen en statuslampjes.
- Prominente AAN/UIT-schakelaar voor het weekschema.
- Ingebouwde Wekker- en Instellingen-tabs, waardoor één kaart de volledige bediening bevat.
- Automatische globale module-installatie via `frontend.extra_module_url`.

### Changed

- Het standaarddashboard bestaat nu uit de herbruikbare custom card.
- Installer kopieert, registreert, back-upt en herstelt ook de custom card.

## [1.2.0] - 2026-08-11

### Added

- Automatisch gevulde dropdown met uitsluitend Sonos-media-players.
- Prominente sensors voor actuele tijd en eerstvolgende wektijd.
- Automatische persistente opslag van de gekozen Sonos-entity.

### Changed

- Dashboard verdeeld in de tabbladen **Wekker** en **Instellingen**.
- Dagelijkse bediening, status en instellingen staan in afzonderlijke kaarten.

## [1.1.0] - 2026-08-10

### Added

- Conservatieve één-commando-installer voor Home Assistant OS/Hassio.
- Automatische back-up, configuratiecontrole, rollback en optionele restart.
- Automatische registratie van een afzonderlijk YAML-dashboard.

### Changed

- Dashboard heeft geen vaste speakerentity meer en is daardoor installatie-onafhankelijk.

## [1.0.0] - 2026-08-10

### Added

- Native Home Assistant-package voor week-/weekendwekker op één Sonos.
- Restart-veilige tijdgebaseerde volume-opbouw en snooze.
- SNOOZE-, STOP- en contextknopscripts.
- Standaard Lovelace-dashboard en fysieke-knopvoorbeelden.
- Volledige Nederlandstalige installatie-, configuratie-, bedienings-, dashboard-, architectuur- en troubleshootingdocumentatie.
