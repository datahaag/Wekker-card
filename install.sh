#!/usr/bin/env bash
# One-shot installer for Home Assistant OS / Supervised (Terminal & SSH add-on).
set -eu

CONFIG_DIR="/config"
RESTART_CORE="false"
RUN_CHECK="true"
RELEASE_VERSION="1.10.0"
INSTALL_VALIDATED="false"
HACS_MODE="false"

usage() {
  echo "Gebruik: bash install.sh [--restart] [--hacs] [--config /config] [--no-check]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --restart) RESTART_CORE="true"; shift ;;
    --hacs) HACS_MODE="true"; shift ;;
    --config)
      [ "$#" -ge 2 ] || { usage; exit 2; }
      CONFIG_DIR="$2"; shift 2 ;;
    --no-check) RUN_CHECK="false"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Onbekende optie: $1"; usage; exit 2 ;;
  esac
done

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
CONFIG_FILE="$CONFIG_DIR/configuration.yaml"
PACKAGE_SOURCE="$SCRIPT_DIR/packages/wekker_card.yaml"
INVALID_PACKAGE_SOURCE="$SCRIPT_DIR/packages/wekker-card.yaml"
DASHBOARD_SOURCE="$SCRIPT_DIR/dashboard/wekker-card.yaml"
CARD_SOURCE="$SCRIPT_DIR/custom_cards/wekker-card/wekker-card.js"
PACKAGE_TARGET="$CONFIG_DIR/packages/wekker_card.yaml"
INVALID_PACKAGE_TARGET="$CONFIG_DIR/packages/wekker-card.yaml"
DISABLED_PACKAGE_TARGET="$CONFIG_DIR/packages/wekker_card.yaml.disabled"
LEGACY_PACKAGE_TARGET="$CONFIG_DIR/packages/sonos_smart_alarm.yaml"
DASHBOARD_TARGET="$CONFIG_DIR/dashboards/wekker-card.yaml"
LEGACY_DASHBOARD_TARGET="$CONFIG_DIR/dashboards/sonos-smart-alarm.yaml"
CARD_TARGET="$CONFIG_DIR/www/community/wekker-card/wekker-card.js"
LEGACY_CARD_ROOT="$CONFIG_DIR/www/sonos-smart-alarm-card.js"
LEGACY_CARD_FOLDER="$CONFIG_DIR/www/Wekker-card/wekker-card.js"
LEGACY_CARD_COMMUNITY_UPPER="$CONFIG_DIR/www/community/Wekker-card/wekker-card.js"
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_DIR="$CONFIG_DIR/backups/wekker-card-$STAMP"

cleanup_installation_files() {
  # Verwijder uitsluitend de uitgepakte release op de canonieke locatie.
  CONFIG_REAL="$(CDPATH= cd -- "$CONFIG_DIR" && pwd -P)"
  EXPECTED_SCRIPT_DIR="$CONFIG_REAL/wekker-card"
  if [ "$SCRIPT_DIR" != "$EXPECTED_SCRIPT_DIR" ]; then
    echo "Installatiebron staat niet in $EXPECTED_SCRIPT_DIR; bronbestanden worden niet verwijderd."
    return 0
  fi

  cd "$CONFIG_REAL"
  if rm -f -- "$CONFIG_REAL/wekker-card-v${RELEASE_VERSION}.zip" &&
     rm -rf -- "$EXPECTED_SCRIPT_DIR"; then
    echo "Installatie-ZIP en tijdelijke map $EXPECTED_SCRIPT_DIR verwijderd."
  else
    echo "WAARSCHUWING: tijdelijke installatiebestanden konden niet volledig worden verwijderd."
  fi
}

[ -f "$CONFIG_FILE" ] || { echo "FOUT: $CONFIG_FILE bestaat niet."; exit 1; }
[ -f "$PACKAGE_SOURCE" ] || { echo "FOUT: packagebron ontbreekt naast install.sh."; exit 1; }
[ -f "$DASHBOARD_SOURCE" ] || { echo "FOUT: dashboardbron ontbreekt naast install.sh."; exit 1; }
[ -f "$CARD_SOURCE" ] || { echo "FOUT: custom-cardbron ontbreekt naast install.sh."; exit 1; }

mkdir -p "$BACKUP_DIR" "$CONFIG_DIR/packages" "$CONFIG_DIR/dashboards" "$CONFIG_DIR/www/community/wekker-card"
cp "$CONFIG_FILE" "$BACKUP_DIR/configuration.yaml"

PACKAGE_EXISTED="false"
INVALID_PACKAGE_EXISTED="false"
DISABLED_PACKAGE_EXISTED="false"
LEGACY_PACKAGE_EXISTED="false"
DASHBOARD_EXISTED="false"
LEGACY_DASHBOARD_EXISTED="false"
CARD_EXISTED="false"
LEGACY_ROOT_EXISTED="false"
LEGACY_FOLDER_EXISTED="false"
LEGACY_COMMUNITY_UPPER_EXISTED="false"
if [ -f "$PACKAGE_TARGET" ]; then
  PACKAGE_EXISTED="true"
  cp "$PACKAGE_TARGET" "$BACKUP_DIR/wekker_card.yaml.package"
fi
if [ -f "$INVALID_PACKAGE_TARGET" ]; then
  INVALID_PACKAGE_EXISTED="true"
  cp "$INVALID_PACKAGE_TARGET" "$BACKUP_DIR/invalid-wekker-card.yaml.package"
fi
if [ -f "$DISABLED_PACKAGE_TARGET" ]; then
  DISABLED_PACKAGE_EXISTED="true"
  cp "$DISABLED_PACKAGE_TARGET" "$BACKUP_DIR/disabled-wekker_card.yaml.package"
fi
if [ -f "$LEGACY_PACKAGE_TARGET" ]; then
  LEGACY_PACKAGE_EXISTED="true"
  cp "$LEGACY_PACKAGE_TARGET" "$BACKUP_DIR/legacy-sonos_smart_alarm.yaml.package"
fi
if [ -f "$DASHBOARD_TARGET" ]; then
  DASHBOARD_EXISTED="true"
  cp "$DASHBOARD_TARGET" "$BACKUP_DIR/wekker-card.yaml.dashboard"
fi
if [ -f "$LEGACY_DASHBOARD_TARGET" ]; then
  LEGACY_DASHBOARD_EXISTED="true"
  cp "$LEGACY_DASHBOARD_TARGET" "$BACKUP_DIR/legacy-sonos-smart-alarm.yaml.dashboard"
fi
if [ -f "$CARD_TARGET" ]; then
  CARD_EXISTED="true"
  cp "$CARD_TARGET" "$BACKUP_DIR/wekker-card.js"
fi
if [ -f "$LEGACY_CARD_ROOT" ]; then
  LEGACY_ROOT_EXISTED="true"
  cp "$LEGACY_CARD_ROOT" "$BACKUP_DIR/legacy-sonos-smart-alarm-card.js"
fi
if [ -f "$LEGACY_CARD_FOLDER" ]; then
  LEGACY_FOLDER_EXISTED="true"
  cp "$LEGACY_CARD_FOLDER" "$BACKUP_DIR/legacy-Wekker-card.js"
fi
if [ -f "$LEGACY_CARD_COMMUNITY_UPPER" ]; then
  LEGACY_COMMUNITY_UPPER_EXISTED="true"
  cp "$LEGACY_CARD_COMMUNITY_UPPER" "$BACKUP_DIR/legacy-community-Wekker-card.js"
fi

rollback() {
  echo "Installatie wordt teruggedraaid; back-up blijft in $BACKUP_DIR"
  cp "$BACKUP_DIR/configuration.yaml" "$CONFIG_FILE"
  if [ "$PACKAGE_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/wekker_card.yaml.package" "$PACKAGE_TARGET"
  else
    rm -f "$PACKAGE_TARGET"
  fi
  if [ "$INVALID_PACKAGE_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/invalid-wekker-card.yaml.package" "$INVALID_PACKAGE_TARGET"
  fi
  if [ "$DISABLED_PACKAGE_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/disabled-wekker_card.yaml.package" "$DISABLED_PACKAGE_TARGET"
  fi
  if [ "$LEGACY_PACKAGE_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/legacy-sonos_smart_alarm.yaml.package" "$LEGACY_PACKAGE_TARGET"
  fi
  if [ "$DASHBOARD_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/wekker-card.yaml.dashboard" "$DASHBOARD_TARGET"
  else
    rm -f "$DASHBOARD_TARGET"
  fi
  if [ "$LEGACY_DASHBOARD_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/legacy-sonos-smart-alarm.yaml.dashboard" "$LEGACY_DASHBOARD_TARGET"
  fi
  if [ "$CARD_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/wekker-card.js" "$CARD_TARGET"
  else
    rm -f "$CARD_TARGET"
  fi
  if [ "$LEGACY_ROOT_EXISTED" = "true" ]; then
    cp "$BACKUP_DIR/legacy-sonos-smart-alarm-card.js" "$LEGACY_CARD_ROOT"
  fi
  if [ "$LEGACY_FOLDER_EXISTED" = "true" ]; then
    mkdir -p "$CONFIG_DIR/www/Wekker-card"
    cp "$BACKUP_DIR/legacy-Wekker-card.js" "$LEGACY_CARD_FOLDER"
  fi
  if [ "$LEGACY_COMMUNITY_UPPER_EXISTED" = "true" ]; then
    mkdir -p "$CONFIG_DIR/www/community/Wekker-card"
    cp "$BACKUP_DIR/legacy-community-Wekker-card.js" "$LEGACY_CARD_COMMUNITY_UPPER"
  fi
}

fail_before_copy() {
  echo "FOUT: $1"
  echo "Er is niets geïnstalleerd. Back-up: $BACKUP_DIR"
  cp "$BACKUP_DIR/configuration.yaml" "$CONFIG_FILE"
  exit 1
}

# Enable packages. Existing non-standard package layouts are left untouched.
if grep -Eq '^[[:space:]]+packages:[[:space:]]*!include_dir_named[[:space:]]+packages[[:space:]]*$' "$CONFIG_FILE"; then
  echo "Packages zijn al correct geactiveerd."
elif grep -Eq '^[[:space:]]+packages:' "$CONFIG_FILE"; then
  fail_before_copy "er bestaat al een andere packages-configuratie. Voeg het package dan handmatig aan die structuur toe."
elif grep -Eq '^homeassistant:[[:space:]]*$' "$CONFIG_FILE"; then
  awk '
    BEGIN { done=0 }
    /^homeassistant:[[:space:]]*$/ && done==0 {
      print
      print "  packages: !include_dir_named packages"
      done=1
      next
    }
    { print }
  ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
  echo "Packages geactiveerd onder homeassistant:."
elif grep -Eq '^homeassistant:' "$CONFIG_FILE"; then
  fail_before_copy "homeassistant gebruikt een niet-standaard inline/include-vorm die niet veilig automatisch kan worden aangepast."
else
  {
    printf '\n# Sonos Smart Alarm\n'
    printf 'homeassistant:\n'
    printf '  packages: !include_dir_named packages\n'
  } >> "$CONFIG_FILE"
  echo "homeassistant/packages-blok toegevoegd."
fi

# Migrate the legacy dashboard key/path before registering the canonical name.
if grep -Eq '^    sonos-smart-alarm:[[:space:]]*$' "$CONFIG_FILE"; then
  if grep -Eq '^    wekker-card:[[:space:]]*$' "$CONFIG_FILE"; then
    awk '
      BEGIN { skip=0 }
      /^    sonos-smart-alarm:[[:space:]]*$/ { skip=1; next }
      skip==1 && !/^      / && !/^[[:space:]]*$/ { skip=0 }
      skip==1 { next }
      { print }
    ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  else
    awk '
      /^    sonos-smart-alarm:[[:space:]]*$/ { print "    wekker-card:"; next }
      /^[[:space:]]+filename:[[:space:]]*dashboards\/sonos-smart-alarm\.yaml[[:space:]]*$/ {
        print "      filename: dashboards/wekker-card.yaml"
        next
      }
      { print }
    ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  fi
  mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
  echo "Oude dashboardregistratie naar wekker-card gemigreerd."
fi

# Register a separate YAML dashboard. Its URL key must contain a hyphen.
if grep -Eq '^    wekker-card:[[:space:]]*$' "$CONFIG_FILE"; then
  echo "Wekker-carddashboard is al geregistreerd."
elif grep -Eq '^  dashboards:[[:space:]]*$' "$CONFIG_FILE"; then
  awk '
    BEGIN { done=0 }
    /^  dashboards:[[:space:]]*$/ && done==0 {
      print
      print "    wekker-card:"
      print "      mode: yaml"
      print "      filename: dashboards/wekker-card.yaml"
      print "      title: Sonos-wekker"
      print "      icon: mdi:alarm"
      print "      show_in_sidebar: true"
      done=1
      next
    }
    { print }
  ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
  echo "Dashboard toegevoegd aan bestaand dashboards-blok."
elif grep -Eq '^lovelace:[[:space:]]*$' "$CONFIG_FILE"; then
  awk '
    BEGIN { done=0 }
    /^lovelace:[[:space:]]*$/ && done==0 {
      print
      print "  dashboards:"
      print "    wekker-card:"
      print "      mode: yaml"
      print "      filename: dashboards/wekker-card.yaml"
      print "      title: Sonos-wekker"
      print "      icon: mdi:alarm"
      print "      show_in_sidebar: true"
      done=1
      next
    }
    { print }
  ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
  echo "Dashboardregistratie toegevoegd onder lovelace:."
elif grep -Eq '^lovelace:' "$CONFIG_FILE"; then
  fail_before_copy "lovelace gebruikt een niet-standaard inline/include-vorm die niet veilig automatisch kan worden aangepast."
else
  {
    printf '\n# Wekker-card dashboard\n'
    printf 'lovelace:\n'
    printf '  dashboards:\n'
    printf '    wekker-card:\n'
    printf '      mode: yaml\n'
    printf '      filename: dashboards/wekker-card.yaml\n'
    printf '      title: Sonos-wekker\n'
    printf '      icon: mdi:alarm\n'
    printf '      show_in_sidebar: true\n'
  } >> "$CONFIG_FILE"
  echo "Lovelace-dashboardblok toegevoegd."
fi

# Remove every known old/current module/resource line first. The card is loaded
# through frontend.extra_module_url, which also works when Lovelace resources
# are managed in the default storage mode.
awk '
  /^[[:space:]]*-[[:space:]]*url:[[:space:]]*\/local\/sonos-smart-alarm-card\.js/ { skip_type=1; next }
  /^[[:space:]]*-[[:space:]]*url:[[:space:]]*\/local\/Wekker-card\/wekker-card\.js/ { skip_type=1; next }
  /^[[:space:]]*-[[:space:]]*url:[[:space:]]*\/local\/community\/Wekker-card\/wekker-card\.js/ { skip_type=1; next }
  /^[[:space:]]*-[[:space:]]*url:[[:space:]]*\/local\/community\/wekker-card\/wekker-card\.js/ { skip_type=1; next }
  skip_type==1 && /^[[:space:]]*type:[[:space:]]*module[[:space:]]*$/ { skip_type=0; next }
  skip_type==1 { skip_type=0 }
  /^[[:space:]]*-[[:space:]]*\/local\/sonos-smart-alarm-card\.js([^[:space:]]*)?[[:space:]]*$/ { next }
  /^[[:space:]]*-[[:space:]]*\/local\/Wekker-card\/wekker-card\.js([^[:space:]]*)?[[:space:]]*$/ { next }
  /^[[:space:]]*-[[:space:]]*\/local\/community\/Wekker-card\/wekker-card\.js([^[:space:]]*)?[[:space:]]*$/ { next }
  /^[[:space:]]*-[[:space:]]*\/local\/community\/wekker-card\/wekker-card\.js([^[:space:]]*)?[[:space:]]*$/ { next }
  { print }
' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"

# Remove extra_module_url when the Wekker-card was its final entry. This is
# required for a clean switch to HACS ownership and is harmless in local mode,
# where the key is added again directly below.
awk '
  function flush_modules() {
    if (in_modules) {
      if (has_module) {
        print modules_header
        printf "%s", modules_body
      }
      in_modules=0
      has_module=0
      modules_header=""
      modules_body=""
    }
  }
  /^  extra_module_url:[[:space:]]*$/ {
    flush_modules()
    in_modules=1
    modules_header=$0
    next
  }
  in_modules==1 {
    if (/^[[:space:]]*$/ || /^    /) {
      modules_body=modules_body $0 ORS
      if (/^    -[[:space:]]/) has_module=1
      next
    }
    flush_modules()
  }
  { print }
  END { flush_modules() }
' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"

# Remove a resources: key that became empty after removing the old Wekker-card
# entry. Keeping even an empty YAML resources block causes a storage-mode warning.
awk '
  function flush_resources() {
    if (in_resources) {
      if (has_resource) {
        print resources_header
        printf "%s", resources_body
      }
      in_resources=0
      has_resource=0
      resources_header=""
      resources_body=""
    }
  }
  /^  resources:[[:space:]]*$/ {
    flush_resources()
    in_resources=1
    resources_header=$0
    next
  }
  in_resources==1 {
    if (/^[[:space:]]*$/ || /^    /) {
      resources_body=resources_body $0 ORS
      if (/^    -[[:space:]]/) has_resource=1
      next
    }
    flush_resources()
  }
  { print }
  END { flush_resources() }
' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
echo "Oude Wekker-cardmodule- en resourceregels uit configuration.yaml verwijderd."

# In HACS mode HACS owns both the file and the storage-mode resource. The
# installer only supplies the native package/dashboard and removes old local
# module lines. Mixing YAML resource mode with HACS cannot be done safely.
if [ "$HACS_MODE" = "true" ]; then
  if grep -Eq '^  resource_mode:[[:space:]]*yaml[[:space:]]*$' "$CONFIG_FILE"; then
    fail_before_copy "--hacs vereist Lovelace storage mode; schakel resource_mode: yaml eerst uit."
  fi
  echo "HACS-modus: dashboardbron en kaartbestand blijven volledig onder beheer van HACS."
else
  # Load the standalone custom card globally, so it works on every dashboard.
  if grep -Eq '^  extra_module_url:[[:space:]]*$' "$CONFIG_FILE"; then
  awk '
    BEGIN { done=0 }
    /^  extra_module_url:[[:space:]]*$/ && done==0 {
      print
      print "    - /local/community/wekker-card/wekker-card.js?v=1.10.0"
      done=1
      next
    }
    { print }
  ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
  echo "Custom card aan bestaande frontendmodules toegevoegd."
  elif grep -Eq '^  extra_module_url:' "$CONFIG_FILE"; then
    fail_before_copy "frontend.extra_module_url gebruikt een include/inline-vorm die niet veilig automatisch kan worden aangepast."
  elif grep -Eq '^frontend:[[:space:]]*$' "$CONFIG_FILE"; then
  awk '
    BEGIN { done=0 }
    /^frontend:[[:space:]]*$/ && done==0 {
      print
      print "  extra_module_url:"
      print "    - /local/community/wekker-card/wekker-card.js?v=1.10.0"
      done=1
      next
    }
    { print }
  ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
  mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
  echo "Custom-cardmodule onder bestaand frontend-blok geregistreerd."
  elif grep -Eq '^frontend:' "$CONFIG_FILE"; then
    fail_before_copy "frontend gebruikt een niet-standaard inline/include-vorm die niet veilig automatisch kan worden aangepast."
  else
  {
    printf '\n# Wekker-card module\n'
    printf 'frontend:\n'
    printf '  extra_module_url:\n'
    printf '    - /local/community/wekker-card/wekker-card.js?v=1.10.0\n'
  } >> "$CONFIG_FILE"
  echo "Frontendmodule voor de custom card geregistreerd."
  fi

  # YAML resource mode is explicit. In that mode the module must remain in the
  # YAML resources list. In the default storage mode the loaded card registers
  # itself through Home Assistant's official Lovelace WebSocket API.
  if grep -Eq '^  resource_mode:[[:space:]]*yaml[[:space:]]*$' "$CONFIG_FILE"; then
    if grep -Eq '^  resources:[[:space:]]*$' "$CONFIG_FILE"; then
    awk '
      BEGIN { done=0 }
      /^  resources:[[:space:]]*$/ && done==0 {
        print
        print "    - url: /local/community/wekker-card/wekker-card.js?v=1.10.0"
        print "      type: module"
        done=1
        next
      }
      { print }
    ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
    else
    awk '
      BEGIN { done=0 }
      /^lovelace:[[:space:]]*$/ && done==0 {
        print
        print "  resources:"
        print "    - url: /local/community/wekker-card/wekker-card.js?v=1.10.0"
        print "      type: module"
        done=1
        next
      }
      { print }
    ' "$CONFIG_FILE" > "$CONFIG_FILE.wekker-card.tmp"
    fi
    mv "$CONFIG_FILE.wekker-card.tmp" "$CONFIG_FILE"
    echo "Wekker-card als YAML-resource geregistreerd (resource_mode: yaml)."
  else
    echo "Storage mode: Wekker-card registreert zichzelf via de officiële Lovelace-API zodra een beheerder het frontend opent."
  fi
fi

rm -f "$LEGACY_PACKAGE_TARGET"
rm -f "$INVALID_PACKAGE_TARGET"
rm -f "$DISABLED_PACKAGE_TARGET"
rm -f "$INVALID_PACKAGE_SOURCE"
rm -f "$LEGACY_DASHBOARD_TARGET"
rm -f "$LEGACY_CARD_ROOT"
rm -f "$LEGACY_CARD_FOLDER"
if [ "$HACS_MODE" = "false" ]; then
  rm -f "$LEGACY_CARD_COMMUNITY_UPPER"
fi
rmdir "$CONFIG_DIR/www/Wekker-card" 2>/dev/null || true
if [ "$HACS_MODE" = "false" ]; then
  rmdir "$CONFIG_DIR/www/community/Wekker-card" 2>/dev/null || true
fi
echo "Oude package en Wekker-cardbestanden verwijderd (back-up behouden indien aanwezig)."

mkdir -p "$CONFIG_DIR/packages" "$CONFIG_DIR/dashboards" "$CONFIG_DIR/www/community/wekker-card"
cp "$PACKAGE_SOURCE" "$PACKAGE_TARGET"
cp "$DASHBOARD_SOURCE" "$DASHBOARD_TARGET"
if [ "$HACS_MODE" = "false" ]; then
  cp "$CARD_SOURCE" "$CARD_TARGET"
  [ -s "$CARD_TARGET" ] || { rollback; echo "FOUT: lowercase Wekker-cardmodule is niet geschreven."; exit 1; }
  grep -Fq 'customElements.define("wekker-card"' "$CARD_TARGET" || {
    rollback
    echo "FOUT: de geschreven module registreert custom:wekker-card niet."
    exit 1
  }
fi
echo "Bestanden naar $CONFIG_DIR geschreven."

if [ "$RUN_CHECK" = "true" ]; then
  if command -v ha >/dev/null 2>&1; then
    echo "Home Assistant-configuratie wordt gecontroleerd..."
    if ! ha core check; then
      rollback
      echo "FOUT: ha core check is mislukt; Home Assistant is niet herstart."
      exit 1
    fi
    echo "Configuratiecontrole geslaagd."
    INSTALL_VALIDATED="true"
  else
    echo "WAARSCHUWING: het ha-commando is hier niet beschikbaar; voer de configuratiecontrole handmatig uit."
    if [ "$RESTART_CORE" = "true" ]; then
      rollback
      echo "FOUT: --restart is zonder geslaagde ha core check niet toegestaan."
      exit 1
    fi
  fi
else
  INSTALL_VALIDATED="true"
fi

# De release-ZIP en uitgepakte installatiemap zijn na een geslaagde controle
# niet meer nodig. Permanente configuratie en back-up blijven behouden.
if [ "$INSTALL_VALIDATED" = "true" ]; then
  cleanup_installation_files
else
  echo "Installatie-ZIP en tijdelijke map blijven staan tot een configuratiecontrole is uitgevoerd."
fi

if [ "$RESTART_CORE" = "true" ]; then
  echo "Home Assistant wordt herstart..."
  ha core restart
else
  echo "Installatie gereed. Herstart na een handmatige configuratiecontrole, of voer opnieuw uit met --restart."
fi

echo "Back-up: $BACKUP_DIR"
