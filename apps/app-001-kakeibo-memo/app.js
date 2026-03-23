const APP_ID = "app-001-kakeibo-memo";
const VISITOR_TRACKING = true;

document.addEventListener('DOMContentLoaded', () => {
  if (VISITOR_TRACKING) {
    fetch(API_CONFIG.baseUrl + API_CONFIG.endpoints.visitor, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'visit',
        app_id: APP_ID,
        page: location.pathname,
        referrer: document.referrer || 'direct'
      })
    }).catch(() => {});
  }
});
