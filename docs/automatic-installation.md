# Automatische installatie op Hassio

## Wat de installer doet

`install.sh` voert uitsluitend deze afgebakende handelingen uit:

1. controleert of `/config/configuration.yaml` en de bronbestanden bestaan;
2. maakt een gedateerde back-up onder `/config/backups/wekker-card-*`;
3. activeert `homeassistant.packages` wanneer dat nog ontbreekt;
4. registreert `wekker-card` als afzonderlijk YAML-dashboard;
5. verwijdert na back-up het oude package, bekende oude kaartbestanden en moduleverwijzingen;
6. kopieert de retro custom card naar `/config/www/community/wekker-card/wekker-card.js`;
7. laadt de module globaal en registreert hem automatisch in de actieve Lovelace-resourcemodus, zodat de kaart op ieder dashboard en in de kaartkiezer verschijnt;
8. kopieert package `wekker_card.yaml` en dashboard `wekker-card.yaml` naar hun definitieve locaties;
9. voert `ha core check` uit;
10. draait wijzigingen terug bij een mislukte controle;
11. verwijdert na een geslaagde installatie de release-ZIP en tijdelijke installatiemap;
12. herstart Home Assistant alleen met `--restart` én een geslaagde controle.

Een bestaande standaard packages- of dashboardstructuur wordt behouden. Bij een afwijkende `!include`-constructie stopt de installer zonder te gokken en blijft de oorspronkelijke configuratie behouden.

## Eenmalig voorbereiden

Installeer de officiële **Terminal & SSH**-add-on en een manier om bestanden naar `/config` te kopiëren, bijvoorbeeld Studio Code Server of Samba share. Kopieer alleen dit bestand naar `/config`:

```text
/config/wekker-card-v1.10.0.zip
```

Je hoeft de zip niet zelf uit te pakken.

## Installeren en herstarten

Open Terminal & SSH en plak deze ene opdracht:

```bash
cd /config && unzip -oq wekker-card-v1.10.0.zip && bash /config/wekker-card/install.sh --restart
```

`&&` zorgt dat de installer alleen start wanneer uitpakken is gelukt. Na een geslaagde herstart staat **Sonos-wekker** in de zijbalk. Open Home Assistant eenmaal als beheerder; in storage mode registreert de geladen module zichzelf dan automatisch als Lovelace-resource. Klik daarna in de retrokaart op **INSTELLINGEN**, kies je speaker en wekbron en gebruik **Ververs spelers, lampen en favorieten**. De installer kiest persoonlijke apparaten niet namens de gebruiker.

## Installeren zonder automatische restart

```bash
cd /config && unzip -oq wekker-card-v1.10.0.zip && bash /config/wekker-card/install.sh
```

Controleer daarna via **Ontwikkelaarstools → YAML** en herstart handmatig.

## Installeren naast HACS

Wanneer de kaart via HACS is gedownload, gebruik je `--hacs`:

```bash
cd /config && unzip -oq wekker-card-v1.10.0.zip && bash /config/wekker-card/install.sh --hacs --restart
```

Deze modus installeert package en dashboard maar schrijft geen lokale
`frontend.extra_module_url`, overschrijft het HACS-kaartbestand niet en vereist
Lovelace storage mode.

## Opnieuw uitvoeren of bijwerken

De installer is herhaalbaar: de dashboardregistratie wordt niet dubbel toegevoegd en bestaande doelbestanden worden eerst geback-upt. Bij een update worden package en dashboard vervangen door de versies uit de uitgepakte projectmap. De oude `/config/packages/sonos_smart_alarm.yaml`, de ongeldige v1.8.0-package `/config/packages/wekker-card.yaml` en kaartpaden met een hoofdletter worden na de back-up verwijderd.

## Back-up

Na een geslaagde installatie verwijdert het script de release-ZIP en de
uitgepakte map `/config/wekker-card`. De blijvende installatiebestanden onder
`packages`, `dashboards` en `www/community` en de onderstaande back-up worden
niet verwijderd. Als de installatie mislukt, blijven ZIP en installatiemap
staan zodat de fout onderzocht kan worden.

Na iedere run toont de terminal de exacte back-upmap, bijvoorbeeld:

```text
/config/backups/wekker-card-20260811-231500
```

De installer wijzigt geen `.storage`-bestanden rechtstreeks. In storage mode gebruikt de geladen kaart Home Assistants officiële resource-API; daarvoor moet een beheerder na de restart eenmaal het frontend openen. Een eerder geïnstalleerde custom card wordt samen met package, dashboard en `configuration.yaml` in dezelfde gedateerde back-up bewaard. Verwijderd worden alleen de exact bekende oude kaartbestanden en bijbehorende resource-/moduleregels; andere community-cards blijven onaangeraakt.
