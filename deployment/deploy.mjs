// deploy.mjs - Kloud Cloud Industrial Deployment Script
// Author: Ledjan Ahmati
// License: Closed Source

import { exec } from 'child_process';
import { promisify } from 'util';
const execAsync = promisify(exec);

async function deploy() {
  console.log('ðŸš€ Starting industrial deployment...');

  try {
    // Step 1: Build Docker images
    console.log('ðŸ”¨ Building Docker images...');
    await execAsync('docker compose build');
    console.log('âœ… Docker images built.');

    // Step 2: Restart Docker services
    console.log('ðŸ”„ Restarting Docker services...');
    await execAsync('docker compose up -d');
    console.log('âœ… Docker services restarted.');

    // Step 3: Health check (optional)
    // You can add health check logic here if needed
    console.log('ðŸ©º Deployment complete.');
  } catch (err) {
    console.error('âŒ Deployment failed:', err);
    process.exit(1);
  }
}

deploy();

