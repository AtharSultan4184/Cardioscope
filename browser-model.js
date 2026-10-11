function sigmoid(value) {
  if (value >= 0) return 1 / (1 + Math.exp(-value));
  const exp = Math.exp(value);
  return exp / (1 + exp);
}

export function predictModels(values, modelData) {
  const transformed = [];
  const contributions = [];

  modelData.numeric.columns.forEach((name, index) => {
    const input = values[name];
    const value = input === null || input === "" ? modelData.numeric.medians[index] : Number(input);
    const scaled = (value - modelData.numeric.means[index]) / modelData.numeric.scales[index];
    transformed.push(scaled);
    contributions.push(scaled);
  });

  modelData.categorical.columns.forEach((name, columnIndex) => {
    const input = values[name];
    const value = input === null || input === "" ? modelData.categorical.imputers[columnIndex] : String(input);
    for (const category of modelData.categorical.categories[columnIndex]) {
      transformed.push(value === category ? 1 : 0);
      contributions.push(value === category ? 1 : 0);
    }
  });

  if (transformed.length !== modelData.feature_names.length) {
    throw new Error("Browser model feature layout does not match its exported weights.");
  }

  const results = {};
  for (const [target, model] of Object.entries(modelData.targets)) {
    if (model.coefficients.length !== transformed.length) {
      throw new Error(`Browser model weights for ${target} have an invalid feature count.`);
    }
    let logOdds = model.intercept;
    for (let index = 0; index < transformed.length; index += 1) {
      logOdds += transformed[index] * model.coefficients[index];
    }
    const probability = sigmoid(logOdds);
    results[target] = {
      probability,
      predicted_status: probability >= 0.5
        ? target === "CAD" ? "CAD" : "Stenotic"
        : "Normal",
    };
  }

  const cad = modelData.targets.CAD;
  const explanation = transformed
    .map((value, index) => ({
      feature: modelData.feature_names[index].split("__").at(-1),
      contribution: value * cad.coefficients[index],
    }))
    .filter((item) => item.contribution !== 0)
    .sort((left, right) => Math.abs(right.contribution) - Math.abs(left.contribution))
    .slice(0, 8)
    .map((item) => ({
      ...item,
      direction: item.contribution >= 0 ? "increases" : "decreases",
    }));

  return {
    cad: results.CAD,
    vessels: Object.fromEntries(
      ["LAD", "LCX", "RCA"].map((name) => [
        name,
        { available: true, ...results[name] },
      ]),
    ),
    explanation,
  };
}
