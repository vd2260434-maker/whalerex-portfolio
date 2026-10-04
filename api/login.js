const { ADMIN_USERNAME, ADMIN_PASSWORD, signToken, isAuthConfigured } = require('./_auth');

module.exports = async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  if (!isAuthConfigured()) {
    return res.status(500).json({
      error: 'Authentication configuration missing. Please configure ADMIN_USERNAME, ADMIN_PASSWORD, and JWT_SECRET in environment variables.'
    });
  }

  try {
    const { username, password } = req.body || {};

    if (!username || !password) {
      return res.status(400).json({ error: 'Username and password are required' });
    }

    const cleanUsername = String(username).trim();
    const cleanPassword = String(password);

    if (cleanUsername !== ADMIN_USERNAME || cleanPassword !== ADMIN_PASSWORD) {
      return res.status(401).json({ error: 'Invalid username or password' });
    }

    // Generate secure session token (valid 24h)
    const token = signToken({ role: 'admin', user: cleanUsername }, 86400);

    // Set HttpOnly Secure Cookie
    res.setHeader(
      'Set-Cookie',
      `whalerex_token=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400`
    );

    return res.status(200).json({
      success: true,
      message: 'Authentication successful',
      token,
      user: { username: cleanUsername, role: 'admin' },
    });
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ error: 'Internal server error during authentication' });
  }
};
