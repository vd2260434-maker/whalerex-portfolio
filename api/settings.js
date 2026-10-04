const fs = require('fs');
const path = require('path');
const { checkAdminAuth } = require('./_auth');

const SETTINGS_FILE = path.join('/tmp', 'whalerex_settings.json');

const DEFAULT_SETTINGS = {
  siteTitle: 'Dinesh — Creative Web Developer & Designer',
  brandName: 'Whalerex',
  availability: 'Available for Freelance & Projects — Tamil Nadu, India',
  contactEmail: 'whalerex350@gmail.com',
  featuredProject: {
    title: 'Waffle House',
    tagline: 'Artisanal Belgian Liege Boutique',
    category: 'Featured Web Project',
    description: 'A creative web project built using Antigravity. The website provides an interactive experience where visitors can explore the website and place orders.',
    liveUrl: 'https://waffle-house-sigma.vercel.app/',
    tags: ['Antigravity', 'Web Design', 'Interactive', 'Ordering'],
    status: 'Live & Active',
  },
  socialLinks: {
    github: 'https://github.com/vd2260434-maker',
    linkedin: 'https://www.linkedin.com/in/dinesh-r-342681403',
    email: 'whalerex350@gmail.com',
  },
};

function readSettings() {
  try {
    if (fs.existsSync(SETTINGS_FILE)) {
      const data = fs.readFileSync(SETTINGS_FILE, 'utf8');
      return { ...DEFAULT_SETTINGS, ...JSON.parse(data) };
    }
  } catch (err) {
    console.error('Error reading settings file:', err);
  }
  return DEFAULT_SETTINGS;
}

function saveSettings(settings) {
  try {
    fs.writeFileSync(SETTINGS_FILE, JSON.stringify(settings, null, 2), 'utf8');
  } catch (err) {
    console.error('Error writing settings file:', err);
  }
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // GET: Public or admin retrieval of site data
  if (req.method === 'GET') {
    const settings = readSettings();
    return res.status(200).json({ success: true, settings });
  }

  // POST/PUT: Requires admin authentication
  const session = checkAdminAuth(req);
  if (!session) {
    return res.status(401).json({ error: 'Unauthorized: Admin authentication required' });
  }

  try {
    const updates = req.body || {};
    const current = readSettings();
    const updated = {
      ...current,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    saveSettings(updated);

    return res.status(200).json({
      success: true,
      message: 'Website settings updated successfully',
      settings: updated,
    });
  } catch (err) {
    console.error('Settings update error:', err);
    return res.status(500).json({ error: 'Could not update settings' });
  }
};
