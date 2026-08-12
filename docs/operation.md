# Bediening

## Dagelijks gebruik

Stel de twee tijden in, kies media en zet de algemene schakelaar aan. De controller begint automatisch vóór de wektijd met de ingestelde opbouwduur (standaard 15 minuten). De radio/muziek blijft na het bereiken van normaal volume spelen.

Voor radio is het eenvoudigst om het station als Mijn Sonos/Favoriet op te slaan en daarna bij **Sonos-favoriet of radiostation** te selecteren. De kaart toont de gekozen wekbron ook op het hoofdscherm.

## Snooze

Druk tijdens `ramping` of `ringing` op **SNOOZE**. De speaker stopt onmiddellijk en het volume gaat naar nul. Na standaard 9 minuten start de gekozen media opnieuw op het normale wekvolume. De opbouw wordt niet herhaald. Iedere nieuwe snooze schrijft een nieuwe absolute deadline, dus snoozen kan onbeperkt.

Als de lichtwekker actief is, gaat de gekozen lamp tijdens snooze eveneens uit en na afloop direct terug naar de ingestelde doelhelderheid.

## Stop

Druk op **STOP** om media en volume direct te stoppen en alleen deze cyclus te blokkeren. De algemene schakelaar en week-/weekendtijden blijven ongewijzigd; de volgende geplande cyclus werkt normaal.

Een actieve lichtwekker gaat bij STOP eveneens direct uit.

## Fysieke knop

Aanbevolen mapping:

- kort: `script.sonos_alarm_context_button`; dit snoozet tijdens opbouw/ringing en stopt tijdens snooze;
- lang: `script.sonos_alarm_stop`; dit stopt altijd de huidige cyclus.

Kopieer het passende patroon uit `examples/physical-button-state.yaml` of `examples/physical-button-event.yaml` naar jouw automations en vervang de voorbeeld-entity/eventwaarden. Kijk in **Ontwikkelaarstools → Gebeurtenissen** of in de trace van een door de UI gemaakte knopautomation om de werkelijke payload te vinden.

## Wekker tijdelijk uitschakelen

Zet **Wekker aan** uit. Als een cyclus actief is, stopt de controller hem. Weer inschakelen nadat de starttijd van de huidige cyclus al is verstreken kan die cyclus opnieuw activeren, tenzij hij met STOP is beëindigd. Gebruik daarom STOP voor “vandaag klaar” en de algemene schakelaar voor het schema als geheel.
