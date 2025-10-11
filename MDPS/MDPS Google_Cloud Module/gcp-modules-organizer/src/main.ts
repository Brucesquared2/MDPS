import { GitHubClient } from './services/github-client';
import { GCPModuleDetector } from './services/gcp-module-detector';
import { ProjectOrganizer } from './services/project-organizer';
import { settings } from './config/settings';

async function main() {
    // Initialize GitHub client
    const githubClient = new GitHubClient(settings.githubToken);

    // Acquire GCP modules from GitHub
    const modules = await githubClient.fetchModules(settings.moduleRepositories);

    // Detect GCP module types and dependencies
    const moduleDetector = new GCPModuleDetector();
    const detectedModules = moduleDetector.detect(modules);

    // Organize the acquired GCP modules
    const projectOrganizer = new ProjectOrganizer();
    projectOrganizer.organize(detectedModules, settings.projectStructure);

    console.log('GCP modules have been successfully organized.');
}

// Start the application
main().catch(error => {
    console.error('Error during application execution:', error);
});