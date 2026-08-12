# Installatie

## Via HACS

1. Open **HACS → ⋮ → Aangepaste repositories**.
2. Voeg `https://github.com/datahaag/Wekker-card` toe als type **Integratie**.
3. Download **Wekker-card** en herstart Home Assistant.
4. Open **Instellingen → Apparaten & diensten → Integratie toevoegen**.
5. Zoek **Wekker-card** en bevestig de installatie.
6. Voeg `custom:wekker-card` aan een dashboard toe.

Alle runtimebestanden staan in `custom_components/wekker_card`. De integratie registreert de kaart zelf; een Lovelace-resource is niet nodig.

## Migratie vanaf 1.x

Versie 2.0 importeert bestaande instellingen bij de eerste activering. Verwijder of schakel daarna `/config/packages/wekker_card.yaml` uit en herstart Home Assistant nogmaals. Laat de oude en nieuwe wekker niet gelijktijdig actief.

## Verwijderen

Verwijder eerst Wekker-card onder **Instellingen → Apparaten & diensten** en verwijder daarna de download via HACS. Zelf opgeslagen integratie-instellingen verdwijnen bij het verwijderen van de config-entry.
