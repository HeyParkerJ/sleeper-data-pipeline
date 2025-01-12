import { createTunnel, SshOptions, ForwardOptions } from 'tunnel-ssh';
import { getPrivateKey } from "../utils/getPrivateKey";

export const tunnelServerPort = 27017;

const tunnelOptions = {
    autoClose: true,
    reconnectOnError: false
};
const serverOptions = {
    port: tunnelServerPort
};
const sshOptions: SshOptions = {
    host: process.env.BASTION_HOST!,
    port: process.env.BASTION_PORT!,
    username: process.env.BASTION_USERNAME!,
    privateKey: getPrivateKey(process.env.BASTION_PRIVATE_KEY_NAME!)
};

const forwardOptions: ForwardOptions = {
    srcAddr: 'localhost',
    srcPort: tunnelServerPort,
    dstAddr: process.env.DB_HOST!,
    dstPort: parseInt(process.env.DB_PORT!)
};

export const connect = async () => {
    try {
        const [server, conn] = await createTunnel(tunnelOptions, serverOptions, sshOptions, forwardOptions);
        server.on('connection', (connection) => {
            console.log('new connection');
        });
        server.on('error', (err) => {
            console.error('error', err);
        });
        return server;
    } catch (e) {
        console.error('error caught', e)
    }
}