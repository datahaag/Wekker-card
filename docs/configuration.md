# Configuratie

## Door het package aangemaakte helpers

| Entity | Doel | Standaard |
|---|---|---|
| `input_boolean.sonos_alarm_enabled` | Algemeen schema aan/uit | uit/eerder hersteld |
| `input_datetime.sonos_alarm_weekday_time` | Maandag t/m vrijdag | 07:00 |
| `input_datetime.sonos_alarm_weekend_time` | Zaterdag en zondag | 09:00 |
| `input_number.sonos_alarm_start_volume` | Volume aan begin opbouw | 2% |
| `input_number.sonos_alarm_normal_volume` | Volume op wektijd/na snooze | 30% |
| `input_number.sonos_alarm_ramp_minutes` | Opbouwduur | 15 min |
| `input_number.sonos_alarm_step_interval` | Tijd tussen stappen | 30 s |
| `input_number.sonos_alarm_snooze_minutes` | Snoozeduur | 9 min |
| `input_boolean.sonos_alarm_light_enabled` | Optionele lichtwekker aan/uit | uit |
| `input_select.sonos_alarm_light_select` | Automatisch gevulde lijst met lampen en schakelaars | selecteren |
| `input_number.sonos_alarm_light_brightness` | Doelhelderheid op wektijd | 70% |
| `input_select.sonos_alarm_speaker_select` | Automatisch gevulde Sonos-keuzelijst | selecteren |
| `input_text.sonos_alarm_speaker` | Intern opgeslagen entity-ID | automatisch |
| `input_text.sonos_alarm_media_uri` | Stream/media-ID | aanpassen |
| `input_select.sonos_alarm_media_type` | `music`, `playlist` of Sonos-favoriet | `music` |
| `input_select.sonos_alarm_favorite_select` | Officiële Mijn Sonos/Favorieten | automatisch |

De helpers `sonos_alarm_start`, `sonos_alarm_target`, `sonos_alarm_snooze_until`, `sonos_alarm_cycle`, `sonos_alarm_stopped_cycle` en `sonos_alarm_status` zijn interne toestand. Ze veranderen alleen bij plannen, starten, snoozen of stoppen en worden niet periodiek bijgewerkt. Bewerk die niet handmatig.

`input_boolean.sonos_alarm_initialized` zorgt dat de genoemde standaarden alleen bij de allereerste start worden gezet. Verwijder of wijzig deze helper niet: zonder `initial:` herstellen alle helpers daarna hun laatst opgeslagen waarde bij een restart.

## Sonos-speler selecteren

De automation `sonos_smart_alarm_discover_speakers` vraagt via `integration_entities('sonos')` alle entities van de officiële Sonos-integratie op, houdt alleen `media_player`-entities over en vult daarmee de dropdown. De zichtbare optie bevat zowel de vriendelijke naam als de unieke entity-ID. De gekozen entity-ID wordt automatisch persistent opgeslagen in `input_text.sonos_alarm_speaker`.

De lijsten worden eenmaal na Home Assistant-start geladen. Gebruik daarna de knop **Ververs spelers, lampen en favorieten** op het instellingentabblad wanneer je een entity of Sonos-favoriet hebt toegevoegd of verwijderd. Er draait bewust geen periodieke discovery.

De lichtwekkerdropdown bevat alle `light.*`- en `switch.*`-entities. Iedere regel begint zichtbaar met `LAMP ·` of `SCHAKELAAR ·` en toont daarnaast de vriendelijke naam en entity-ID. De keuze wordt intern opgeslagen in `input_text.sonos_alarm_light`. Een dimbare lamp volgt de helderheidsopbouw; een gewone schakelaar kan niet dimmen en gaat daarom aan bij het begin van de opbouw. Snooze, STOP en uitschakelen zetten beide typen uit.

`input_boolean.sonos_alarm_light_initialized` is een interne migratievlag. Deze zorgt dat de doelhelderheid bij zowel een nieuwe installatie als een upgrade eenmalig op 70% wordt gezet, maar daarna bij iedere restart de gebruikerswaarde wordt hersteld.

## Media kiezen

Directe HTTP(S)-radiostreams gebruiken gewoonlijk `music`. Spotify-/Tidal-links kunnen door Sonos worden geaccepteerd als de dienst in de Sonos-app gekoppeld is. Voor een Sonos-playlist gebruik je `playlist`. Voor een favoriet gebruik je `favorite_item_id` plus het item-ID zoals `FV:2/31`; de officiële Sonos-integratie maakt hiervoor een uitgeschakelde `sensor.sonos_favorites` beschikbaar die je desgewenst activeert.

De aanbevolen route voor radiostations is **Mijn Sonos/Favorieten**. Voeg Radio 538, Qmusic, Sublime of een ander station in de Sonos-app toe aan Mijn Sonos. De automation `sonos_smart_alarm_discover_favorites` leest daarna de officiële Favorites-sensor en toont de stations bij naam. Bij selectie worden het Sonos-ID en mediatype automatisch correct gezet.

Bevat de dropdown alleen **Handmatige URI / eigen stream**, activeer dan bij de entities van de Sonos-integratie de standaard uitgeschakelde Favorites-sensor. Druk daarna op **Ververs spelers, lampen en favorieten**.

Voorbeelden staan in `examples/media-examples.md`. Een websitepagina die alleen een speler bevat is meestal geen directe audiostream en werkt niet.

## Volumes

De UI gebruikt procenten; `media_player.volume_set` ontvangt automatisch een fractie tussen 0 en 1. Kies normaal gesproken startvolume ≤ normaal volume. Wanneer startvolume hoger staat, rekent het algoritme technisch een dalende reeks uit; dat is meestal niet gewenst.

## Wat de gebruiker aanpast

Verplicht: Sonos-speler selecteren, media-URI/type en beide wektijden. Aanbevolen: veilige volumes, interval en snoozeduur. Alleen voor de fysieke knop pas je trigger entity/eventwaarden in het gekozen voorbeeld aan. Alle scripts, interne helpers en controller-automations worden automatisch door het package gemaakt.
