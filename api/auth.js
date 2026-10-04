const { checkAdminAuth } = require('./_auth');

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const session = checkAdminAuth(req);

  if (!session) {
    return res.status(401).json({ authenticated: false, error: 'Unauthorized or token expired' });
  }

  return res.status(200).json({
    authenticated: true,
    user: { username: session.user, role: session.role },
  });
};
