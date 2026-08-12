# Publiceren op GitHub en installeren met HACS

## Wat HACS wel en niet installeert

HACS behandelt deze repository als type **Dashboard**. Daardoor installeert HACS
`dist/wekker-card.js` onder `/config/www/community/wekker-card/` en registreert
het de dashboardbron via:

```text
/hacsfiles/wekker-card/wekker-card.js
```

De native wekkerlogica in `packages/wekker_card.yaml` en het optionele volledige
YAML-dashboard worden niet door een HACS-dashboardrepository geïnstalleerd. Na
het downloaden van de kaart in HACS voer je daarom één keer de release-installer
in HACS-modus uit:

```bash
cd /config && unzip -oq wekker-card-v1.10.0.zip && bash /config/wekker-card/install.sh --hacs --restart
```

`--hacs` installeert de wekkerlogica en het dashboard, verwijdert oude lokale
moduleverwijzingen en laat het HACS-kaartbestand en de HACS-resource ongemoeid.

## Repository eenmalig aanmaken

1. Meld je aan bij GitHub.
2. Open <https://github.com/new>.
3. Kies eigenaar **datahaag**.
4. Gebruik exact de repositorynaam **wekker-card**.
5. Kies **Public**. HACS ondersteunt voor deze route openbare GitHub-repositories.
6. Laat **Add a README**, **Add .gitignore** en **Choose a license** uitgeschakeld.
7. Kies **Create repository**.

De uiteindelijke URL is:

```text
https://github.com/datahaag/wekker-card
```

Geef nooit je GitHub-wachtwoord of een toegangstoken door. Publiceren kan via een
reeds geautoriseerde GitHub-koppeling of via GitHub Desktop.

## Belangrijke GitHub-instellingen

Vul bij **About** een korte omschrijving in, bijvoorbeeld:

```text
Retro Sonos-wekkerkaart voor Home Assistant met lamp- en schakelaarondersteuning
```

Voeg de topics `home-assistant`, `hacs`, `lovelace`, `sonos` en `alarm-clock` toe
en laat Issues ingeschakeld. De meegeleverde workflow
`.github/workflows/validate.yml` controleert de HACS-structuur na iedere push.

## Als aangepaste HACS-repository toevoegen

1. Open **HACS** in Home Assistant.
2. Open rechtsboven het menu met de drie puntjes.
3. Kies **Aangepaste repositories** of **Custom repositories**.
4. Vul `https://github.com/datahaag/wekker-card` in.
5. Selecteer categorie **Dashboard**.
6. Kies **Toevoegen** en daarna **Downloaden**.
7. Voer daarna de bovenstaande `--hacs`-installatieopdracht uit.
8. Vernieuw de browser volledig of sluit de Home Assistant-app een keer af.

Controleer vervolgens onder **Instellingen → Dashboards → Bronnen** dat deze bron
aanwezig is:

```text
/hacsfiles/wekker-card/wekker-card.js
```

Voeg daarna via **Dashboard bewerken → Kaart toevoegen** de kaart
**Wekker-card (Sonos retro)** toe. Handmatige YAML blijft ook mogelijk:

```yaml
type: custom:wekker-card
```

## Nieuwe versies publiceren

Werk eerst `dist/wekker-card.js` bij zodat dit bestand exact gelijk is aan
`custom_cards/wekker-card/wekker-card.js`. Commit en push de wijzigingen. Zonder
GitHub Release gebruikt HACS de standaardbranch. Voor nette versie-selectie kun
je daarna op GitHub via **Releases → Draft a new release** een tag zoals `v1.10.0`
en een volledige release publiceren; alleen een losse tag is daarvoor niet genoeg.
