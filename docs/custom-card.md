# Retro custom card

`custom:wekker-card` wordt samen met de integratie geïnstalleerd en automatisch geladen. De kaart bevat een retro digitale klok, een grote AAN/UIT-schakelaar, statusmeters, SNOOZE, STOP en een apart instellingentabblad.

Plaats hem via de kaartkiezer als **Wekker-card (Sonos retro)** of handmatig:

```yaml
type: custom:wekker-card
```

De lichtlijst toont alle lampen als `LAMP · …` en alle schakelaars als `SCHAKELAAR · …`. Een lamp volgt de geleidelijke opbouw; een schakelaar wordt alleen aan/uit gestuurd.

De favorietenlijst leest de officiële Sonos Favorites-sensor. Voeg een radiostation eerst in de Sonos-app aan Mijn Sonos/Favorieten toe en schakel de Favorites-sensor in Home Assistant in.
