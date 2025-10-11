import fs from 'fs';
import path from 'path';

export const createDirectory = (dirPath: string): void => {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
};

export const copyFile = (source: string, destination: string): void => {
    fs.copyFileSync(source, destination);
};

export const readFile = (filePath: string): string => {
    return fs.readFileSync(filePath, 'utf-8');
};

export const writeFile = (filePath: string, data: string): void => {
    fs.writeFileSync(filePath, data, 'utf-8');
};