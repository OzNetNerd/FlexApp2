if (!window.flashMessagesShown) {
  window.flashMessagesShown = true;

  // Capture the script reference immediately
  const messagesElement = document.currentScript;

  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
      if (typeof window.showToast === 'function') {
        if (messagesElement && messagesElement.hasAttribute('data-messages')) {
          const messages = JSON.parse(messagesElement.getAttribute('data-messages'));
          console.log(`⚡ Processing ${messages.length} flash messages...`);

          messages.forEach((item, index) => {
            setTimeout(function() {
              const [category, message] = item;
              const cat = category || 'info';
              window.showToast(message, cat);
              console.log(`📢 Flash shown (${cat}):`, message);
            }, index * 300);
          });
        } else {
          console.log("No flash messages found or script element not available");
        }
      } else {
        console.error("Flash messages present, but window.showToast function not found.");
        // Fallback alert code...
      }
    }, 100);
  });
}