if (!window.flashMessagesShown) {
  window.flashMessagesShown = true;

  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
      if (typeof window.showToast === 'function') {
        const messagesElement = document.currentScript;
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
        console.error("Flash messages present, but window.showToast function not found.");
        const messagesElement = document.currentScript;
        const messages = JSON.parse(messagesElement.getAttribute('data-messages'));

        messages.forEach(item => {
          const [category, message] = item;
          alert(`[${category}] ${message}`);
        });
      }
    }, 100);
  });
}