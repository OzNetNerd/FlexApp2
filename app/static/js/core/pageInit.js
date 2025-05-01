import log from './logger.js';

try {
    const pageTitle = document.title || '<TBA>';
    log("info", "base.html", "head", `🎯 Page title set: ${pageTitle}`);
    log("debug", "base.html", "head", "📦 Head assets loaded");
} catch (e) {
    console.error("Error logging from base.html head:", e);
}