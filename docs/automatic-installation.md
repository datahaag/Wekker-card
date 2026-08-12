# Automatische installatie

Vanaf versie 2.0 is de HACS-integratie de automatische installatie. HACS kopieert alle bestanden naar `custom_components/wekker_card`; Home Assistant activeert de gecombineerde kaart en wekker na één herstart en het toevoegen van de integratie.

Er is bewust geen `install.sh`: een integratie hoort `configuration.yaml`, packages en interne `.storage`-bestanden niet rechtstreeks te wijzigen.
