"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("custom_cards/wekker-card/wekker-card.js", "utf8");
const canonical = "/local/community/wekker-card/wekker-card.js?v=1.10.0";
const hacs = "/hacsfiles/wekker-card/wekker-card.js?hacstag=123456";

async function runScenario(resources, resourceMode = "storage") {
  const calls = [];
  const hass = {
    callWS: async (message) => {
      calls.push(message);
      if (message.type === "lovelace/info") return { resource_mode: resourceMode };
      if (message.type === "lovelace/resources") return resources;
      return { id: "created", type: "module", url: canonical };
    },
  };
  const registry = new Map();
  const shadow = { addEventListener() {} };
  class HTMLElementMock { attachShadow() { this.shadowRoot = shadow; return shadow; } }
  const context = {
    console: { info() {}, warn() {} },
    customElements: {
      get: (name) => registry.get(name),
      define: (name, value) => registry.set(name, value),
    },
    document: {
      documentElement: {},
      querySelector: () => ({ hass }),
    },
    HTMLElement: HTMLElementMock,
    window: { customCards: [], setTimeout() {} },
  };
  vm.createContext(context);
  vm.runInContext(source, context);
  await new Promise((resolve) => setImmediate(resolve));
  await new Promise((resolve) => setImmediate(resolve));
  return calls;
}

(async () => {
  let calls = await runScenario([]);
  assert(calls.some((call) => call.type === "lovelace/resources/create"
    && call.res_type === "module" && call.url === canonical));

  calls = await runScenario([
    { id: "old", type: "module", url: "/local/community/wekker-card/wekker-card.js?v=1.9.0" },
    { id: "duplicate", type: "module", url: "/local/Wekker-card/wekker-card.js?v=1.7.0" },
  ]);
  assert(calls.some((call) => call.type === "lovelace/resources/update"
    && call.resource_id === "old" && call.url === canonical));
  assert(calls.some((call) => call.type === "lovelace/resources/delete"
    && call.resource_id === "duplicate"));

  calls = await runScenario([], "yaml");
  assert.equal(JSON.stringify(calls), JSON.stringify([{ type: "lovelace/info" }]));

  calls = await runScenario([
    { id: "hacs", type: "module", url: hacs },
    { id: "local-duplicate", type: "module", url: canonical },
  ]);
  assert(!calls.some((call) => call.type === "lovelace/resources/update"));
  assert(calls.some((call) => call.type === "lovelace/resources/delete"
    && call.resource_id === "local-duplicate"));

  console.log("OK: 4 automatische resource-registratiescenario's");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
