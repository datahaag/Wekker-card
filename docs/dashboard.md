# Dashboard

Het meegeleverde dashboard bevat de zelfstandige `custom:wekker-card`. De automatische installer registreert het dashboard én laadt de JavaScript-module globaal vanuit `/config/www/community/wekker-card`. Daardoor kun je dezelfde kaart ook aan ieder ander Lovelace-dashboard toevoegen.

## Kaarttab Wekker

Het hoofdtabblad is bedoeld voor dagelijks gebruik en toont bovenaan groot:

- de actuele lokale tijd met seconden en datum;
- de eerstvolgende toepasselijke week- of weekendwektijd;
- kleiner daaronder beide vaste tijden voor maandag–vrijdag en zaterdag–zondag;
- of het schema aan of uit staat.

Daaronder staan afzonderlijke meters voor status, actueel Sonos-volume, resterende snoozetijd en lichtniveau, gevolgd door grote SNOOZE- en STOP-knoppen. De brede mechanische AAN/UIT-schakelaar bedient het volledige weekschema.

## Kaarttab Instellingen

Alle overige configuratie staat op een eigen tabblad en is opgesplitst in losse kaarten:

- Sonos-speler en media;
- wekschema;
- volume-opbouw;
- snooze.

De Sonos-dropdown wordt automatisch gevuld vanuit de officiële Sonos-integratie; de onderliggende entity-ID wordt zonder extra technische velden bewaard. De kaarttab blijft onderdeel van dezelfde kaart, zodat die overal zelfstandig werkt.

`SNOOZE` heeft buiten `ramping` en `ringing` bewust geen effect. `STOP` stopt de huidige cyclus. De resterende snoozetijd wordt lokaal in de kaart iedere seconde bijgewerkt, zonder iedere seconde een Home Assistant-status op te slaan.

De dashboardeditor kan `action: perform-action` weergeven als “Actie uitvoeren”. Op oudere Home Assistant-frontends kan `tap_action.action: call-service` plus `service: script.sonos_alarm_snooze`/`script.sonos_alarm_stop` nodig zijn.
