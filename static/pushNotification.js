const express = require('express');
const bodyParser = require('body-parser');
const webpush = require('web-push');

const app = express();
const port = 3000;

app.use(bodyParser.json());

// Dummy data representing messages
let messages = [];

// Dummy subscription (in real-world scenario, you would store this in a database)
let subscription = null;

// Configure web-push with your VAPID keys
const vapidKeys = {
  publicKey: 'your-public-key',
  privateKey: 'your-private-key'
};

webpush.setVapidDetails(
  'mailto:your-email@example.com',
  vapidKeys.publicKey,
  vapidKeys.privateKey
);

// Endpoint to receive new messages
app.post('/new-message', (req, res) => {
  const { message } = req.body;
  messages.push(message);

  // Send push notification if there's a subscription
  if (subscription) {
    const payload = JSON.stringify({
      title: 'New Message',
      message: message
    });

    webpush.sendNotification(subscription, payload)
      .catch(error => console.error('Error sending push notification:', error));
  }

  res.sendStatus(200);
});

// Endpoint to store subscription
app.post('/subscribe', (req, res) => {
  subscription = req.body;
  res.sendStatus(201);
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
