const fs = require('fs');
const path = require('path');
const { checkAdminAuth } = require('./_auth');

const STORAGE_FILE = path.join('/tmp', 'whalerex_messages.json');

function readMessages() {
  try {
    if (fs.existsSync(STORAGE_FILE)) {
      const data = fs.readFileSync(STORAGE_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.error('Error reading messages file:', err);
  }
  return [];
}

function saveMessages(messages) {
  try {
    fs.writeFileSync(STORAGE_FILE, JSON.stringify(messages, null, 2), 'utf8');
  } catch (err) {
    console.error('Error writing messages file:', err);
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // POST: Public submission (Contact form on portfolio)
  if (req.method === 'POST') {
    try {
      const { name, email, subject, message } = req.body || {};

      if (!name || !email || !message) {
        return res.status(400).json({ error: 'Name, email, and message are required' });
      }

      // Basic validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(String(email).trim())) {
        return res.status(400).json({ error: 'Valid email address is required' });
      }

      const newMessage = {
        id: 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6),
        name: String(name).trim().slice(0, 100),
        email: String(email).trim().slice(0, 150),
        subject: String(subject || 'General Inquiry').trim().slice(0, 200),
        message: String(message).trim().slice(0, 3000),
        status: 'unread', // 'unread' | 'read' | 'replied'
        createdAt: new Date().toISOString(),
      };

      const messages = readMessages();
      messages.unshift(newMessage);
      saveMessages(messages);

      return res.status(201).json({
        success: true,
        message: 'Your message has been received. Dinesh will get back to you shortly!',
        id: newMessage.id,
      });
    } catch (err) {
      console.error('Save message error:', err);
      return res.status(500).json({ error: 'Could not submit message' });
    }
  }

  // All other methods require admin authentication
  const session = checkAdminAuth(req);
  if (!session) {
    return res.status(401).json({ error: 'Unauthorized: Admin authentication required' });
  }

  // GET: List all messages
  if (req.method === 'GET') {
    const messages = readMessages();
    return res.status(200).json({
      success: true,
      count: messages.length,
      messages,
    });
  }

  // PATCH: Update message status (read / replied)
  if (req.method === 'PATCH') {
    const { id, status } = req.body || {};
    if (!id || !status) {
      return res.status(400).json({ error: 'Message ID and new status are required' });
    }

    const messages = readMessages();
    const index = messages.findIndex((m) => m.id === id);
    if (index === -1) {
      return res.status(404).json({ error: 'Message not found' });
    }

    messages[index].status = status;
    messages[index].updatedAt = new Date().toISOString();
    saveMessages(messages);

    return res.status(200).json({ success: true, message: messages[index] });
  }

  // DELETE: Delete a message
  if (req.method === 'DELETE') {
    const { id } = req.query || req.body || {};
    if (!id) {
      return res.status(400).json({ error: 'Message ID is required' });
    }

    let messages = readMessages();
    const initialCount = messages.length;
    messages = messages.filter((m) => m.id !== id);

    if (messages.length === initialCount) {
      return res.status(404).json({ error: 'Message not found' });
    }

    saveMessages(messages);
    return res.status(200).json({ success: true, message: 'Message deleted' });
  }

  return res.status(405).json({ error: 'Method not allowed' });
};
