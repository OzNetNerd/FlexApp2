if (!window.templateErrorShown) {
  window.templateErrorShown = true;

  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
      const errorElement = document.currentScript;
      const errorMsg = errorElement.getAttribute('data-error');

      if (typeof window.showToast === 'function') {
        window.showToast(`Template Render Error: ${errorMsg}`, "danger");
        console.error("❌ Template render error:", errorMsg);
      } else {
        console.error("Template render error occurred, but window.showToast function not found.");
        alert("Template Render Error: " + errorMsg);
      }
    }, 500);
  });
}