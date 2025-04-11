import log from '/static/js/logger.js';

export function validateTabsTemplate() {
  const templateData = document.getElementById('template-data');
  const scriptName = templateData.dataset.scriptName;

  // Log initialization info
  const functionName = 'template_init';
  const expected = ['tabs', 'read_only'];
  const received = [];
  const missing = [];

  if (JSON.parse(templateData.dataset.tabsDefined)) received.push('tabs'); else missing.push('tabs');
  if (JSON.parse(templateData.dataset.readOnlyDefined)) received.push('read_only'); else missing.push('read_only');

  log("info", scriptName, functionName, `🔍 Expecting variables: ${expected.join(', ')}`);
  log("info", scriptName, functionName, `Received variables: ${received.join(', ') || 'None'}`);
  if (missing.length > 0) {
    log("warn", scriptName, functionName, `❌ Missing variables: ${missing.join(', ')}`);
  } else {
    log("info", scriptName, functionName, `✅ All expected variables present`);
  }

  // Log tab render info if tabs exist
  const formTabs = document.getElementById('formTabs');
  if (formTabs) {
    const tabRenderFuncName = 'template_render';
    const tabNames = JSON.parse(formTabs.dataset.tabNames);
    log("info", scriptName, tabRenderFuncName, "🧩 Tabs rendered:", tabNames);

    // Log sections for each tab
    document.querySelectorAll('.tab-pane').forEach((tabPane, index) => {
      const sectionNames = JSON.parse(tabPane.dataset.sectionNames || '[]');
      log("debug", scriptName, tabRenderFuncName, `📁 Sections in tab '${tabNames[index]}':`, sectionNames);
    });
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', validateTabsTemplate);