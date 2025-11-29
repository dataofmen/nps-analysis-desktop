const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow;
let backendProcess;

const isDev = process.env.NODE_ENV === 'development';
const BACKEND_PORT = 8000;

function getBackendPath() {
    if (isDev) {
        // In dev, we assume the backend is running separately or we point to the python script?
        // Actually, typically in dev we run 'uvicorn' manually or via concurrently.
        // But to test the executable logic, we can point to the dist folder.
        // Let's assume in dev we might want to run the python script directly OR the built exe.
        // For simplicity and consistency, let's try to run the built exe if it exists, 
        // or fall back to assuming the developer runs the backend manually.

        // However, the user wants a "packaged" app.
        // Let's point to the built executable in ../backend/dist/nps-backend
        // For onedir, the executable is inside the folder
        // backend/dist/nps-backend/nps-backend
        return path.join(__dirname, '../../backend/dist/nps-backend/nps-backend');
    } else {
        // In prod, the folder is copied to resources/nps-backend
        // So executable is resources/nps-backend/nps-backend
        return path.join(process.resourcesPath, 'nps-backend', 'nps-backend');
    }
}

function startBackend() {
    const backendPath = getBackendPath();
    console.log('Starting backend from:', backendPath);

    backendProcess = spawn(backendPath, [], {
        cwd: isDev ? undefined : process.resourcesPath
    });

    backendProcess.stdout.on('data', (data) => {
        console.log(`Backend: ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`Backend Error: ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Backend process exited with code ${code}`);
    });
}

function checkBackendHealth() {
    return new Promise((resolve, reject) => {
        const req = http.get(`http://localhost:${BACKEND_PORT}/health`, (res) => {
            if (res.statusCode === 200) {
                resolve();
            } else {
                reject('Backend not ready');
            }
        });

        req.on('error', (err) => {
            reject(err);
        });

        req.end();
    });
}

async function waitForBackend() {
    let retries = 20;
    while (retries > 0) {
        try {
            await checkBackendHealth();
            console.log('Backend is ready!');
            return;
        } catch (err) {
            console.log('Waiting for backend...');
            await new Promise(resolve => setTimeout(resolve, 1000));
            retries--;
        }
    }
    console.error('Failed to connect to backend');
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1280,
        height: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // For simple IPC if needed, though we use HTTP
        },
    });

    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }

    mainWindow.on('closed', function () {
        mainWindow = null;
    });
}

app.on('ready', async () => {
    startBackend();
    await waitForBackend();
    createWindow();
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', function () {
    if (mainWindow === null) {
        createWindow();
    }
});

app.on('will-quit', () => {
    if (backendProcess) {
        backendProcess.kill();
    }
});
