import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { predictModels } from "./browser-model.js";

const model = JSON.parse(
  await readFile(new URL("./models/browser_models.json", import.meta.url), "utf8"),
);
const schema = JSON.parse(
  await readFile(new URL("./models/schema.json", import.meta.url), "utf8"),
);

const blankValues = Object.fromEntries(
  schema.features.map((feature) => [feature.name, null]),
);
const blankResult = predictModels(blankValues, model);
assert.deepEqual(Object.keys(blankResult.vessels), ["LAD", "LCX", "RCA"]);
assert.equal(blankResult.cad.predicted_status, "CAD");
assert.ok(Math.abs(blankResult.cad.probability - 0.8445407122953194) < 1e-12);
assert.ok(Math.abs(blankResult.vessels.LAD.probability - 0.48140396369448357) < 1e-12);
assert.ok(blankResult.explanation.length > 0);

const enteredValues = { ...blankValues, Age: 50, Sex: "Fmale", "Poor R Progression": "Y" };
const enteredResult = predictModels(enteredValues, model);
assert.ok(Math.abs(enteredResult.cad.probability - 0.6096563885781748) < 1e-12);
assert.ok(Math.abs(enteredResult.vessels.LCX.probability - 0.17945594010178356) < 1e-12);
for (const result of [blankResult, enteredResult]) {
  assert.ok(result.explanation.length <= 8);
  for (const estimate of Object.values(result.vessels)) {
    assert.ok(Number.isFinite(estimate.probability));
    assert.ok(estimate.probability >= 0 && estimate.probability <= 1);
  }
}

console.log("browser model: all tests passed");
