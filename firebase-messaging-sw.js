importScripts('https://www.gstatic.com/firebasejs/9.6.10/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.6.10/firebase-messaging.js');

firebase.initializeApp({
    apiKey: "BMX8vgljZpQ4y9BjYYBrq9QJfV3OIqolnBBV3b28PrmbyPjAuC13XQkCwloRm6Ztcr626kDM2e9dQliHG_ERIDE",
    projectId: "seizure-notification-system",
    messagingSenderId: "139114613218",
    appId: "1:139114613218:web:b0935f635262f577fc51bb"
});

const messaging = firebase.messaging();
messaging.onBackgroundMessage((payload) => {
    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body,
        icon: '/icon.png'
    };
    self.registration.showNotification(notificationTitle, notificationOptions);
});
