# GitHub en HACS

De repository is een HACS-repository van het type **Integratie**. HACS installeert de volledige runtime onder `/config/custom_components/wekker_card`.

Na een Home Assistant-herstart verschijnt **Wekker-card** bij **Instellingen → Apparaten & diensten → Integratie toevoegen**. De configuratiestroom maakt de backend-entiteiten aan en registreert de frontendkaart. Er is geen ZIP, shellscript, package of afzonderlijke dashboardbron.

Voeg `https://github.com/datahaag/Wekker-card` in HACS toe als aangepaste repository van het type **Integratie**, download hem en herstart Home Assistant.
