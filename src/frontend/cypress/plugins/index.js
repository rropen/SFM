const { startDevServer } = require("@cypress/vite-dev-server");
const codeCoverageTask = require("@cypress/code-coverage/task");

/**
 * @type {Cypress.PluginConfig}
 */

module.exports = (on, config) => {
  on("dev-server:start", async (options) => startDevServer({ options }));
  codeCoverageTask(on, config);

  return config;
};
