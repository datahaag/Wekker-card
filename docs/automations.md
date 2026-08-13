# Bediening via externe schakelaars en knoppen

Vervang de voorbeeld-entiteiten `switch.externe_wekker` en `binary_sensor.externe_knop` door je eigen entiteiten. Deze automatiseringen staan los van Wekker-card en kunnen daarom in de Home Assistant-interface worden aangepast of uitgeschakeld.

## Eén externe schakelaar voor wekker aan en uit

```yaml
alias: Externe schakelaar bedient Wekker-card
triggers:
  - trigger: state
    entity_id: switch.externe_wekker
    to: "on"
    id: aan
  - trigger: state
    entity_id: switch.externe_wekker
    to: "off"
    id: uit
actions:
  - choose:
      - conditions: "{{ trigger.id == 'aan' }}"
        sequence:
          - action: switch.turn_on
            target:
              entity_id: switch.wekker_card_enabled
    default:
      - action: switch.turn_off
        target:
          entity_id: switch.wekker_card_enabled
mode: restart
```

## Aparte fysieke snoozeknop

```yaml
alias: Fysieke knop voor snooze
triggers:
  - trigger: state
    entity_id: binary_sensor.externe_knop
    to: "on"
actions:
  - action: button.press
    target:
      entity_id: button.wekker_card_snooze
mode: single
```

## Aparte fysieke stopknop

```yaml
alias: Fysieke knop stopt huidige wekcyclus
triggers:
  - trigger: state
    entity_id: binary_sensor.externe_stopknop
    to: "on"
actions:
  - action: button.press
    target:
      entity_id: button.wekker_card_stop
mode: single
```

Je kunt deze automatiseringen ook volledig via **Instellingen → Automatiseringen & scènes** maken: kies de externe schakelaar of knop als trigger en gebruik daarna **Schakelaar inschakelen/uitschakelen** of **Knop indrukken** als actie.
