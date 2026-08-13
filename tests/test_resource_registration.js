"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const source = fs.readFileSync("custom_components/wekker_card/frontend/wekker-card.js", "utf8");
const registry = new Map();
const shadow = { addEventListener() {} };
class HTMLElementMock { attachShadow() { this.shadowRoot = shadow; return shadow; } }
const context = {
  console: { info() {}, warn() {} },
  customElements: { get: (name) => registry.get(name), define: (name, value) => registry.set(name, value) },
  HTMLElement: HTMLElementMock,
  window: { customCards: [] },
};
vm.createContext(context);
vm.runInContext(source, context);

assert(registry.has("wekker-card"));
assert.equal(context.window.customCards.length, 1);
assert.equal(context.window.customCards[0].type, "wekker-card");
assert(source.includes('const CARD_VERSION = "2.0.1"'));
assert(!source.includes("lovelace/resources/create"));
assert(!source.includes("setInterval(() => register"));
console.log("OK: frontend wordt één keer door de integratie geregistreerd");
