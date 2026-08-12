const CARD_VERSION = "1.10.0";
const LOCAL_RESOURCE_URL = "/local/community/wekker-card/wekker-card.js?v=1.10.0";
const HACS_RESOURCE_PATH = "/hacsfiles/wekker-card/wekker-card.js";

async function registerWekkerCardResource(hass) {
  try {
    const info = await hass.callWS({ type: "lovelace/info" });
    if (info?.resource_mode !== "storage") return true;

    const resources = await hass.callWS({ type: "lovelace/resources" });
    const isWekkerResource = (resource) => {
      const path = String(resource?.url || "").split("?")[0].toLowerCase();
      return path === "/local/community/wekker-card/wekker-card.js"
        || path === HACS_RESOURCE_PATH
        || path === "/local/wekker-card/wekker-card.js"
        || path === "/local/sonos-smart-alarm-card.js";
    };
    const matches = Array.isArray(resources) ? resources.filter(isWekkerResource) : [];
    const primary = matches.find((resource) =>
      String(resource.url || "").split("?")[0].toLowerCase() === HACS_RESOURCE_PATH
    ) || matches.find((resource) =>
      String(resource.url || "").split("?")[0] === "/local/community/wekker-card/wekker-card.js"
    ) || matches[0];
    const resourceUrl = primary
      && String(primary.url || "").split("?")[0].toLowerCase() === HACS_RESOURCE_PATH
      ? primary.url
      : LOCAL_RESOURCE_URL;

    if (primary) {
      if (primary.url !== resourceUrl || primary.type !== "module") {
        await hass.callWS({
          type: "lovelace/resources/update",
          resource_id: primary.id,
          res_type: "module",
          url: resourceUrl,
        });
      }
    } else {
      await hass.callWS({
        type: "lovelace/resources/create",
        res_type: "module",
        url: LOCAL_RESOURCE_URL,
      });
    }

    for (const duplicate of matches.filter((resource) => resource.id !== primary?.id)) {
      await hass.callWS({
        type: "lovelace/resources/delete",
        resource_id: duplicate.id,
      });
    }
    console.info("WEKKER-CARD: Lovelace-resource is automatisch geregistreerd.");
    return true;
  } catch (error) {
    console.warn("WEKKER-CARD: automatische resource-registratie wacht op een beheerder.", error);
    return false;
  }
}

function registerWhenHomeAssistantIsReady() {
  let attempts = 0;
  const tryRegister = async () => {
    attempts += 1;
    const root = document.querySelector("home-assistant");
    const registered = root?.hass?.callWS
      ? await registerWekkerCardResource(root.hass)
      : false;
    if (!registered && attempts < 12) {
      window.setTimeout(tryRegister, 5000);
    }
  };
  tryRegister();
}

class WekkerCard extends HTMLElement {
  static getStubConfig() {
    return {};
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._tab = "clock";
    this.shadowRoot.addEventListener("click", (event) => this._handleClick(event));
    this.shadowRoot.addEventListener("change", (event) => this._handleChange(event));
    this.shadowRoot.addEventListener("input", (event) => this._handleInput(event));
  }

  connectedCallback() {
    if (!this._clockTimer) {
      this._clockTimer = window.setInterval(() => this._updateLocalClock(), 1000);
    }
    this._updateLocalClock();
  }

  disconnectedCallback() {
    if (this._clockTimer) {
      window.clearInterval(this._clockTimer);
      this._clockTimer = undefined;
    }
  }

  setConfig(config) {
    this._config = {
      name: "SONOS SMART ALARM",
      enabled_entity: "input_boolean.sonos_alarm_enabled",
      status_entity: "input_select.sonos_alarm_status",
      snooze_until_entity: "input_datetime.sonos_alarm_snooze_until",
      speaker_select_entity: "input_select.sonos_alarm_speaker_select",
      weekday_time_entity: "input_datetime.sonos_alarm_weekday_time",
      weekend_time_entity: "input_datetime.sonos_alarm_weekend_time",
      media_uri_entity: "input_text.sonos_alarm_media_uri",
      media_type_entity: "input_select.sonos_alarm_media_type",
      favorite_select_entity: "input_select.sonos_alarm_favorite_select",
      start_volume_entity: "input_number.sonos_alarm_start_volume",
      normal_volume_entity: "input_number.sonos_alarm_normal_volume",
      ramp_minutes_entity: "input_number.sonos_alarm_ramp_minutes",
      step_interval_entity: "input_number.sonos_alarm_step_interval",
      snooze_minutes_entity: "input_number.sonos_alarm_snooze_minutes",
      light_enabled_entity: "input_boolean.sonos_alarm_light_enabled",
      light_select_entity: "input_select.sonos_alarm_light_select",
      light_brightness_entity: "input_number.sonos_alarm_light_brightness",
      snooze_script: "script.sonos_alarm_snooze",
      stop_script: "script.sonos_alarm_stop",
      refresh_lists_script: "script.sonos_alarm_refresh_lists",
      ...config,
    };
    if (this._hass) this._render();
  }

  set hass(hass) {
    this._hass = hass;
    const focused = this.shadowRoot?.activeElement;
    if (this._tab === "settings" && focused && ["INPUT", "SELECT"].includes(focused.tagName)) return;
    this._render();
  }

  getCardSize() {
    return this._tab === "settings" ? 10 : 7;
  }

  getGridOptions() {
    return { columns: 6, min_columns: 3 };
  }

  _state(entityId, fallback = "—") {
    return this._hass?.states?.[entityId]?.state ?? fallback;
  }

  _attribute(entityId, name, fallback = "") {
    return this._hass?.states?.[entityId]?.attributes?.[name] ?? fallback;
  }

  _updateLocalClock() {
    const now = new Date();
    const time = this.shadowRoot?.querySelector(".digital-time");
    const date = this.shadowRoot?.querySelector(".display-topline > span:first-child");
    if (time) {
      time.textContent = new Intl.DateTimeFormat("nl-NL", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false,
      }).format(now);
    }
    if (date) {
      date.textContent = new Intl.DateTimeFormat("nl-NL", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      }).format(now);
    }
    const nextAlarm = this.shadowRoot?.querySelector(".next-alarm > strong");
    if (nextAlarm && this._config) nextAlarm.textContent = this._nextAlarmLabel();
    const snooze = this.shadowRoot?.querySelector(".snooze-value");
    if (snooze && this._state(this._config?.status_entity, "idle") === "snoozed") {
      const rawDeadline = this._state(this._config?.snooze_until_entity, "");
      const deadline = new Date(rawDeadline.replace(" ", "T")).getTime();
      const remaining = Number.isFinite(deadline) ? Math.max(0, Math.ceil((deadline - now.getTime()) / 1000)) : 0;
      snooze.textContent = remaining > 0
        ? `${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, "0")}`
        : "--:--";
    }
  }

  _selectedEntity(selectEntity, domains) {
    const value = this._state(selectEntity, "");
    const entity = value.split(" — ").at(-1);
    const allowed = Array.isArray(domains) ? domains : [domains];
    return allowed.some((domain) => entity.startsWith(`${domain}.`)) ? entity : "";
  }

  _nextAlarmLabel() {
    if (this._state(this._config.enabled_entity, "off") !== "on") return "Uitgeschakeld";
    const now = new Date();
    for (let offset = 0; offset < 8; offset += 1) {
      const date = new Date(now);
      date.setDate(now.getDate() + offset);
      const isWeekend = [0, 6].includes(date.getDay());
      const raw = this._state(isWeekend ? this._config.weekend_time_entity : this._config.weekday_time_entity, "00:00:00");
      const [hour, minute] = raw.split(":").map(Number);
      date.setHours(hour || 0, minute || 0, 0, 0);
      if (date > now) {
        const day = new Intl.DateTimeFormat("nl-NL", { weekday: "long" }).format(date);
        return `${day} ${String(hour || 0).padStart(2, "0")}:${String(minute || 0).padStart(2, "0")}`;
      }
    }
    return "—";
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  _statusLabel(status) {
    return ({ idle: "GEREED", ramping: "OPBOUW", ringing: "WEKKEN", snoozed: "SNOOZE" })[status] || String(status).toUpperCase();
  }

  _options(entityId) {
    const options = this._attribute(entityId, "options", []);
    return Array.isArray(options) ? options : [];
  }

  _select(entityId, label) {
    const current = this._state(entityId, "");
    const options = this._options(entityId);
    return `
      <label class="field field-wide">
        <span>${this._escape(label)}</span>
        <select data-entity="${this._escape(entityId)}" data-domain="input_select" data-service="select_option" data-field="option">
          ${options.map((option) => `<option value="${this._escape(option)}" ${option === current ? "selected" : ""}>${this._escape(option)}</option>`).join("")}
        </select>
      </label>`;
  }

  _time(entityId, label) {
    const value = this._state(entityId, "07:00:00").slice(0, 5);
    return `
      <label class="field">
        <span>${this._escape(label)}</span>
        <input type="time" value="${this._escape(value)}" data-entity="${this._escape(entityId)}" data-domain="input_datetime" data-service="set_datetime" data-field="time">
      </label>`;
  }

  _number(entityId, label, suffix) {
    const entity = this._hass?.states?.[entityId];
    const value = Number(entity?.state ?? 0);
    const min = Number(entity?.attributes?.min ?? 0);
    const max = Number(entity?.attributes?.max ?? 100);
    const step = Number(entity?.attributes?.step ?? 1);
    return `
      <label class="field field-wide range-field">
        <span>${this._escape(label)} <output>${this._escape(value)}${this._escape(suffix)}</output></span>
        <input type="range" min="${min}" max="${max}" step="${step}" value="${value}" data-entity="${this._escape(entityId)}" data-domain="input_number" data-service="set_value" data-field="value">
      </label>`;
  }

  _settings() {
    const c = this._config;
    const lightEnabled = this._state(c.light_enabled_entity, "off") === "on";
    const selectedLightEntity = this._selectedEntity(c.light_select_entity, ["light", "switch"]);
    const selectedIsSwitch = selectedLightEntity.startsWith("switch.");
    return `
      <section class="settings-panel">
        <div class="section-label">SONOS &amp; MUZIEK</div>
        <div class="form-grid">
          ${this._select(c.speaker_select_entity, "Sonos-speler")}
          ${this._select(c.favorite_select_entity, "Sonos-favoriet of radiostation")}
          <p class="field-hint">Deze lijst gebruikt rechtstreeks Mijn Sonos/Favorieten. Sla Radio 538, Qmusic, Sublime of andere bronnen eerst als favoriet op in de Sonos-app.</p>
          <button class="refresh-button" data-action="refresh-lists">VERVERS SPELERS, LAMPEN EN FAVORIETEN</button>
          <label class="field field-wide">
            <span>Eigen stream- of muziek-URI (optioneel)</span>
            <input type="text" value="${this._escape(this._state(c.media_uri_entity, ""))}" data-entity="${this._escape(c.media_uri_entity)}" data-domain="input_text" data-service="set_value" data-field="value">
          </label>
          ${this._select(c.media_type_entity, "Mediatype")}
        </div>

        <div class="section-label">WEKSCHEMA</div>
        <div class="form-grid two-columns">
          ${this._time(c.weekday_time_entity, "Maandag t/m vrijdag")}
          ${this._time(c.weekend_time_entity, "Zaterdag en zondag")}
        </div>

        <div class="section-label">VOLUME &amp; TIMING</div>
        <div class="form-grid">
          ${this._number(c.start_volume_entity, "Startvolume", "%")}
          ${this._number(c.normal_volume_entity, "Normaal wekvolume", "%")}
          ${this._number(c.ramp_minutes_entity, "Opbouwtijd", " min")}
          ${this._number(c.step_interval_entity, "Volume-interval", " s")}
          ${this._number(c.snooze_minutes_entity, "Snoozeduur", " min")}
        </div>

        <div class="section-label">LICHTWEKKER</div>
        <div class="form-grid">
          <button class="settings-toggle ${lightEnabled ? "enabled" : ""}" data-action="toggle-light" aria-pressed="${lightEnabled}">
            <span class="power-lamp"></span>
            <span><small>LICHTWEKKER</small>${lightEnabled ? "AAN" : "UIT"}</span>
          </button>
          ${this._select(c.light_select_entity, "Lamp of schakelaar")}
          ${this._number(c.light_brightness_entity, "Doelhelderheid op wektijd", "%")}
          <p class="field-hint">${selectedIsSwitch
            ? "SCHAKELAAR geselecteerd: deze ondersteunt geen dimniveau en wordt alleen AAN/UIT gestuurd."
            : "LAMP geselecteerd: het licht begint op 0% en volgt dezelfde opbouw, snooze en stop als het geluid."}</p>
        </div>
      </section>`;
  }

  _clock() {
    const c = this._config;
    const enabled = this._state(c.enabled_entity, "off") === "on";
    const status = this._state(c.status_entity, "idle");
    const lightEnabled = this._state(c.light_enabled_entity, "off") === "on";
    const speakerEntity = this._selectedEntity(c.speaker_select_entity, "media_player");
    const lightEntity = this._selectedEntity(c.light_select_entity, ["light", "switch"]);
    const volumeLevel = this._attribute(speakerEntity, "volume_level", null);
    const brightness = this._attribute(lightEntity, "brightness", null);
    const volumeText = Number.isFinite(volumeLevel) ? Math.round(volumeLevel * 100) : "—";
    const lightText = lightEntity.startsWith("switch.")
      ? (this._state(lightEntity, "off") === "on" ? "AAN" : "UIT")
      : `${this._state(lightEntity, "off") === "on" && Number.isFinite(brightness) ? Math.round(brightness / 255 * 100) : 0}%`;
    const favoriteState = this._state(c.favorite_select_entity, "");
    const mediaUri = this._state(c.media_uri_entity, "Geen bron gekozen");
    const sourceName = favoriteState && favoriteState.endsWith(` — ${mediaUri}`)
      ? favoriteState.split(" — ")[0]
      : mediaUri;
    return `
      <section class="clock-panel">
        <div class="display-bezel">
          <div class="display-topline">
            <span>${new Intl.DateTimeFormat("nl-NL").format(new Date())}</span>
            <span class="alarm-indicator ${enabled ? "lit" : ""}">● ALARM</span>
          </div>
          <div class="digital-time">--:--:--</div>
          <div class="next-alarm"><span>VOLGENDE WEKKER</span><strong>${this._escape(this._nextAlarmLabel())}</strong></div>
          <div class="schedule-times">
            <span>MA–VR <strong>${this._escape(this._state(c.weekday_time_entity, "--:--").slice(0, 5))}</strong></span>
            <span>ZA–ZO <strong>${this._escape(this._state(c.weekend_time_entity, "--:--").slice(0, 5))}</strong></span>
          </div>
          <div class="source-line"><span>WEKBRON</span><strong>${this._escape(sourceName)}</strong></div>
        </div>

        <button class="power-switch ${enabled ? "on" : "off"}" data-action="toggle-alarm" aria-pressed="${enabled}">
          <span class="power-lamp"></span>
          <span><small>WEKKER</small>${enabled ? "AAN" : "UIT"}</span>
          <span class="switch-track"><i></i></span>
        </button>

        <div class="meter-row">
          <div class="meter"><small>STATUS</small><strong>${this._escape(this._statusLabel(status))}</strong></div>
          <div class="meter"><small>VOLUME</small><strong>${this._escape(volumeText)}${volumeText === "—" ? "" : "%"}</strong></div>
          <div class="meter"><small>SNOOZE</small><strong class="snooze-value">--:--</strong></div>
          <div class="meter"><small>LICHT</small><strong>${lightEnabled ? this._escape(lightText) : "UIT"}</strong></div>
        </div>

        <div class="alarm-buttons">
          <button class="snooze" data-action="snooze"><span>SNOOZE</span><small>nog ${this._escape(this._state(c.snooze_minutes_entity, "9"))} minuten</small></button>
          <button class="stop" data-action="stop"><span>STOP</span><small>deze wekcyclus</small></button>
        </div>
      </section>`;
  }

  _render() {
    if (!this._config || !this._hass) return;
    const missing = [this._config.enabled_entity, this._config.status_entity].filter((entity) => !this._hass.states[entity]);
    this.shadowRoot.innerHTML = `
      <style>${this._styles()}</style>
      <ha-card>
        <div class="alarm-case">
          <i class="screw screw-left"></i><i class="screw screw-right"></i>
          <header><span class="brand-dot"></span>${this._escape(this._config.name)}<small>v${CARD_VERSION}</small></header>
          ${missing.length ? `<div class="warning">Ontbrekende entities: ${this._escape(missing.join(", "))}. Installeer of herlaad eerst het Sonos Smart Alarm-package.</div>` : ""}
          <nav>
            <button class="${this._tab === "clock" ? "active" : ""}" data-tab="clock">WEKKER</button>
            <button class="${this._tab === "settings" ? "active" : ""}" data-tab="settings">INSTELLINGEN</button>
          </nav>
          ${this._tab === "clock" ? this._clock() : this._settings()}
          <footer>GEBEURTENISGESTUURD • HOME ASSISTANT • SONOS</footer>
        </div>
      </ha-card>`;
    this._updateLocalClock();
  }

  async _call(domain, service, entityId, data = {}) {
    if (!this._hass) return;
    await this._hass.callService(domain, service, data, { entity_id: entityId });
  }

  _handleClick(event) {
    const button = event.target.closest("button");
    if (!button) return;
    if (button.dataset.tab) {
      this._tab = button.dataset.tab;
      this._render();
      return;
    }
    const action = button.dataset.action;
    if (action === "toggle-alarm") this._call("input_boolean", "toggle", this._config.enabled_entity);
    if (action === "toggle-light") this._call("input_boolean", "toggle", this._config.light_enabled_entity);
    if (action === "snooze") this._call("script", "turn_on", this._config.snooze_script);
    if (action === "stop") this._call("script", "turn_on", this._config.stop_script);
    if (action === "refresh-lists") this._call("script", "turn_on", this._config.refresh_lists_script);
  }

  _handleChange(event) {
    const control = event.target.closest("[data-entity]");
    if (!control) return;
    const data = {};
    data[control.dataset.field] = control.dataset.domain === "input_number" ? Number(control.value) : control.value;
    if (control.dataset.entity === this._config.media_uri_entity) {
      this._call("input_text", "set_value", this._config.media_uri_entity, data);
      this._call("input_select", "select_option", this._config.media_type_entity, { option: "music" });
      this._call("input_select", "select_option", this._config.favorite_select_entity, { option: "Handmatige URI / eigen stream" });
      return;
    }
    this._call(control.dataset.domain, control.dataset.service, control.dataset.entity, data);
  }

  _handleInput(event) {
    const range = event.target.closest('input[type="range"]');
    if (!range) return;
    const output = range.closest("label")?.querySelector("output");
    if (output) {
      const oldText = output.textContent;
      const suffix = oldText.replace(/^[-\d.]+/, "");
      output.textContent = `${range.value}${suffix}`;
    }
  }

  _styles() {
    return `
      :host { display:block; --case:#37352f; --case-light:#555149; --cream:#d7cbb2; --red:#ff3b30; --display:#160b09; font-family:Arial,Helvetica,sans-serif; }
      ha-card { background:transparent; box-shadow:none; overflow:visible; }
      * { box-sizing:border-box; }
      button, input, select { font:inherit; }
      .alarm-case { position:relative; color:#1e1d19; padding:16px 18px 13px; border-radius:28px 28px 18px 18px; border:3px solid #292823; background:linear-gradient(145deg,#625e54 0%,var(--case) 35%,#2c2b27 100%); box-shadow:inset 2px 2px 1px #7b766b,inset -3px -3px 4px #171714,0 12px 24px rgba(0,0,0,.38); }
      .alarm-case::before,.alarm-case::after { content:""; position:absolute; bottom:-9px; width:42px; height:13px; border-radius:0 0 9px 9px; background:#24231f; z-index:-1; }
      .alarm-case::before { left:38px; transform:skew(-12deg); }.alarm-case::after { right:38px; transform:skew(12deg); }
      .screw { position:absolute; top:14px; width:10px; height:10px; border-radius:50%; background:radial-gradient(circle at 35% 30%,#aaa38f,#34332d 60%); box-shadow:0 1px 2px #111; }.screw::after { content:""; position:absolute; left:2px; right:2px; top:4px; border-top:1px solid #171714; }.screw-left{left:14px}.screw-right{right:14px}
      header { color:var(--cream); text-align:center; font-weight:900; font-size:13px; letter-spacing:2.5px; text-shadow:0 1px #111; margin:0 20px 12px; } header small{font-size:8px;opacity:.55;margin-left:8px}.brand-dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#c84132;margin-right:8px;box-shadow:0 0 7px #c84132}
      nav { display:grid; grid-template-columns:1fr 1fr; gap:5px; padding:4px; margin-bottom:10px; border-radius:9px; background:#24231f; box-shadow:inset 0 2px 4px #111; } nav button { border:0; border-radius:6px; padding:8px 5px; background:transparent; color:#8e897d; font-size:11px; font-weight:900; letter-spacing:1.2px; cursor:pointer; } nav button.active { color:#292823; background:linear-gradient(#dfd4bd,#b8ad98); box-shadow:0 2px 4px #111; }
      .display-bezel { border:4px solid #201f1b; border-radius:13px; padding:11px 14px 12px; background:radial-gradient(ellipse at center,#351713 0%,var(--display) 70%); box-shadow:inset 0 0 13px #000,0 2px 1px #716c61; color:var(--red); }
      .display-topline { display:flex; justify-content:space-between; color:#93665d; font:700 10px/1.1 ui-monospace,monospace; letter-spacing:1.4px; }.alarm-indicator{color:#4e2722}.alarm-indicator.lit{color:#ff5549;text-shadow:0 0 7px #ff2e23}
      .digital-time { text-align:center; white-space:nowrap; font:800 clamp(40px,13vw,76px)/1.05 "Courier New",ui-monospace,monospace; letter-spacing:-4px; color:#ff4034; text-shadow:0 0 4px #ff2d22,0 0 13px rgba(255,42,28,.72); font-variant-numeric:tabular-nums; }
      .next-alarm { display:flex; justify-content:space-between; align-items:baseline; padding-top:7px; border-top:1px solid #5f2720; font:700 10px ui-monospace,monospace; letter-spacing:1px; color:#a56a61; }.next-alarm strong{font-size:14px;color:#ff766d;text-align:right}.schedule-times{display:flex;justify-content:flex-end;gap:14px;margin-top:6px;font:700 8px ui-monospace,monospace;letter-spacing:.7px;color:#75453e}.schedule-times strong{color:#cc7770;font-size:10px}.source-line{display:flex;justify-content:space-between;gap:10px;margin-top:6px;padding-top:5px;border-top:1px dotted #4b2723;font:700 8px ui-monospace,monospace;letter-spacing:.7px;color:#75453e}.source-line strong{max-width:70%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#bb706a;font-size:9px}
      .power-switch { width:100%; margin:12px 0 10px; padding:9px 12px; display:grid; grid-template-columns:auto 1fr auto; gap:10px; align-items:center; border:2px solid #22211e; border-radius:9px; color:#272620; background:linear-gradient(#e1d7c1,#afa38d); box-shadow:0 3px 0 #191815,0 5px 7px #111; cursor:pointer; text-align:left; }.power-switch small{display:block;font-size:8px;letter-spacing:1.2px}.power-switch span:nth-child(2){font-size:18px;font-weight:1000;letter-spacing:2px}.power-lamp{width:13px;height:13px;border-radius:50%;background:#5c1813;box-shadow:inset 0 1px 2px #111}.power-switch.on .power-lamp{background:#58d455;box-shadow:0 0 9px #52e750,inset 0 1px #d7ffd5}.switch-track{width:54px;height:24px;padding:3px;border-radius:14px;background:#5a574f;box-shadow:inset 0 2px 4px #222}.switch-track i{display:block;width:18px;height:18px;border-radius:50%;background:#ddd2ba;transition:transform .18s}.power-switch.on .switch-track i{transform:translateX(30px);background:#5cda57}
      .meter-row { display:grid; grid-template-columns:repeat(4,1fr); gap:7px; }.meter { min-width:0; padding:8px 5px; text-align:center; border:1px solid #1b1a17; border-radius:7px; color:#d4c9b2; background:#292824; box-shadow:inset 0 1px 3px #111; }.meter small{display:block;color:#827d72;font-size:8px;letter-spacing:1px}.meter strong{display:block;overflow:hidden;text-overflow:ellipsis;font:800 14px/1.5 ui-monospace,monospace;color:#e8dcc3}
      .alarm-buttons { display:grid; grid-template-columns:1.5fr 1fr; gap:10px; margin-top:12px; }.alarm-buttons button { min-height:62px; border:2px solid #1e1d1a; border-radius:10px; box-shadow:0 4px 0 #171613,0 6px 8px #111; cursor:pointer; font-weight:1000; letter-spacing:1.5px; }.alarm-buttons button:active{transform:translateY(3px);box-shadow:0 1px 0 #171613}.alarm-buttons span,.alarm-buttons small{display:block}.alarm-buttons span{font-size:18px}.alarm-buttons small{font-size:8px;opacity:.7;margin-top:4px}.snooze{color:#27251f;background:linear-gradient(#eadba3,#bca964)}.stop{color:#fff3ec;background:linear-gradient(#d14b3d,#8d2019)}
      .settings-panel { padding:11px; border-radius:12px; background:linear-gradient(#ded3bc,#bcb09a); box-shadow:inset 0 2px 4px #fff8,inset 0 -2px 4px #6c6457; }.section-label{margin:12px 0 7px;padding-bottom:4px;border-bottom:2px solid #827866;color:#4a463e;font-size:10px;font-weight:1000;letter-spacing:1.8px}.section-label:first-child{margin-top:1px}.form-grid{display:grid;grid-template-columns:1fr;gap:8px}.two-columns{grid-template-columns:repeat(2,minmax(0,1fr))}.field{display:flex;flex-direction:column;gap:4px;min-width:0}.field span{font-size:10px;font-weight:800;color:#4e493f}.field input,.field select{width:100%;min-width:0;border:1px solid #77705f;border-radius:6px;padding:9px;color:#26241f;background:#f1e8d4;box-shadow:inset 0 1px 3px #7775;outline:none}.field input:focus,.field select:focus{border-color:#a52c23;box-shadow:0 0 0 2px #b9332944}.range-field input{padding:0;accent-color:#b33127}.range-field span{display:flex;justify-content:space-between}.range-field output{font:900 12px ui-monospace,monospace;color:#9b281f}
      .settings-toggle{width:100%;display:grid;grid-template-columns:auto 1fr;align-items:center;gap:10px;padding:9px 11px;border:1px solid #77705f;border-radius:7px;background:#a99f8c;color:#37332c;text-align:left;cursor:pointer}.settings-toggle small{display:block;font-size:8px;letter-spacing:1px}.settings-toggle span:nth-child(2){font-weight:1000;letter-spacing:1px}.settings-toggle.enabled{background:#bed5ae}.settings-toggle.enabled .power-lamp{background:#58d455;box-shadow:0 0 8px #4fe34c}.field-hint{margin:0;color:#5f584c;font-size:10px;line-height:1.4}
      .refresh-button{width:100%;padding:9px;border:1px solid #675f50;border-radius:6px;background:#827866;color:#fff7e7;font-size:9px;font-weight:900;letter-spacing:.8px;cursor:pointer}
      .warning{margin:0 0 10px;padding:9px;border-radius:6px;background:#ffd9a8;color:#6b2e00;font-size:11px}.alarm-case footer{text-align:center;margin-top:13px;color:#8b867b;font-size:7px;letter-spacing:1.4px}
      @media (max-width:400px){.alarm-case{padding:14px 12px 12px}.digital-time{font-size:44px}.next-alarm{align-items:flex-start;flex-direction:column;gap:3px}.next-alarm strong{text-align:left}.schedule-times{justify-content:flex-start}.two-columns{grid-template-columns:1fr}.meter-row{grid-template-columns:repeat(2,1fr)}.meter strong{font-size:12px}}
    `;
  }
}

if (!customElements.get("wekker-card")) {
  customElements.define("wekker-card", WekkerCard);
}

window.customCards = window.customCards || [];
if (!window.customCards.some((card) => card.type === "wekker-card")) {
  window.customCards.push({
    type: "wekker-card",
    name: "Wekker-card (Sonos retro)",
    preview: true,
    description: "Gebeurtenisgestuurde Sonos-wekker in een retro wekkerbehuizing.",
    documentationURL: "https://developers.home-assistant.io/docs/frontend/custom-ui/custom-card/",
  });
}

registerWhenHomeAssistantIsReady();

console.info(`%c WEKKER-CARD %c v${CARD_VERSION} `, "background:#37352f;color:#e8dcc3;font-weight:bold", "background:#b33127;color:white");
