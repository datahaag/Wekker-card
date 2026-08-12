# Configuratie

Alle instellingen staan op het tabblad **INSTELLINGEN** van de kaart en worden door de integratie bewaard.

| Entity | Functie | Standaard |
|---|---|---|
| `switch.wekker_card_enabled` | Weekschema aan/uit | uit |
| `time.wekker_card_weekday` | Maandag t/m vrijdag | 07:00 |
| `time.wekker_card_weekend` | Zaterdag en zondag | 09:00 |
| `number.wekker_card_start_volume` | Beginvolume | 2% |
| `number.wekker_card_normal_volume` | Volume op wektijd | 30% |
| `number.wekker_card_ramp_minutes` | Opbouwtijd | 15 min |
| `number.wekker_card_step_interval` | Tijd tussen apparaatstappen | 30 s |
| `number.wekker_card_snooze_minutes` | Snoozeduur | 9 min |
| `select.wekker_card_speaker` | Sonos-speler | selecteren |
| `select.wekker_card_favorite` | Mijn Sonos/Favoriet | selecteren |
| `text.wekker_card_media_uri` | Eigen stream-URI | leeg |
| `switch.wekker_card_light_enabled` | Lichtwekker aan/uit | uit |
| `select.wekker_card_light` | Lamp of schakelaar | selecteren |
| `number.wekker_card_light_brightness` | Doelhelderheid | 70% |

Druk op `button.wekker_card_refresh` na het toevoegen van nieuwe apparaten of Sonos-favorieten. Automations kunnen `wekker_card.snooze`, `wekker_card.stop`, `wekker_card.context_button` en `wekker_card.refresh_lists` aanroepen.
