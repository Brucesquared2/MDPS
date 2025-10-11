import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

/**
 * Clones a Git repository to the specified local path.
 * @param {string} repoUrl - The URL of the Git repository to clone.
 * @param {string} localPath - The local path where the repository should be cloned.
 * @returns {Promise<void>} - A promise that resolves when the cloning is complete.
 */
export async function cloneRepository(repoUrl: string, localPath: string): Promise<void> {
    try {
        await execPromise(`git clone ${repoUrl} ${localPath}`);
        console.log(`Repository cloned from ${repoUrl} to ${localPath}`);
    } catch (error) {
        console.error(`Failed to clone repository: ${error.message}`);
        throw error;
    }
}

/**
 * Checks the status of a local Git repository.
 * @param {string} localPath - The local path of the Git repository.
 * @returns {Promise<string>} - A promise that resolves with the status of the repository.
 */
export async function checkRepositoryStatus(localPath: string): Promise<string> {
    try {
        const { stdout } = await execPromise(`git -C ${localPath} status`);
        return stdout;
    } catch (error) {
        console.error(`Failed to check repository status: ${error.message}`);
        throw error;
    }
}