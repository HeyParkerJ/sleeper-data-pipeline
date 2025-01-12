import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

// Helper function to read SSH private key
export const getPrivateKey = (keyPath?: string): string => {
    // If no path provided, use default ~/.ssh/id_rsa
    if(!process.env.BASTION_PRIVATE_KEY_NAME) {
        throw new Error('BASTION_PRIVATE_KEY_NAME must be provided')
    }
    const finalPath = path.join(os.homedir(), '.ssh', process.env.BASTION_PRIVATE_KEY_NAME);

    try {
        return fs.readFileSync(finalPath, 'utf8');
    } catch (err) {
        console.error(`Error reading private key from ${finalPath}:`, err);
        throw new Error(`Failed to read SSH private key: ${err.message}`);
    }
};
