# Architectuur

Wekker-card 2.0 bestaat uit één HACS-integratie onder `custom_components/wekker_card`. De config-entry bezit de instellingen, entiteiten, exacte timers en frontendregistratie.

De planner berekent de eerstvolgende week- of weekendwektijd en registreert callbacks voor de opbouwstart en doeltijd. Snooze registreert één aanvullende callback. Er is geen `time_pattern`, intervalpoller of periodieke statusopslag.

Tijdens de actieve opbouw berekent de controller automatisch een veilig interval van 2 tot 30 seconden uit de opbouwduur en het verschil tussen begin- en eindvolume. Sonos gaat lineair van startvolume naar normaal volume; een dimbare lamp gaat van 0% naar de doelhelderheid. Een schakelaar kent geen dimniveau en wordt daarom alleen aan of uit gezet.

Instellingen worden in Home Assistants `Store` bewaard en alleen na wijzigingen vertraagd opgeslagen. Bij de eerste installatie worden bestaande 1.x-helperwaarden eenmalig geïmporteerd.

De kaart wordt door de integratie aangeboden op `/wekker-card/wekker-card.js` via `async_register_static_paths` en door Home Assistant geladen met `add_extra_js_url`. Er wordt geen Lovelace-resource of `.storage`-bestand aangepast.
