# Bediening

De grote knop **WEKKER AAN/UIT** schakelt het terugkerende week- en weekendschema. **STOP** beëindigt alleen de huidige cyclus. **SNOOZE** stopt geluid en licht tijdelijk en hervat op het normale doelvolume en de ingestelde doelhelderheid.

Een fysieke knop kan bij kort indrukken `wekker_card.context_button` en bij lang indrukken `wekker_card.stop` aanroepen. De voorbeelden in `examples/` tonen beide gangbare triggervormen.

Bij een herstart worden instellingen hersteld en worden alleen de benodigde exacte callbacks opnieuw gepland. Er worden geen periodieke statussen vastgelegd.
