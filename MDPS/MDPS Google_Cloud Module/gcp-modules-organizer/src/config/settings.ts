export const settings = {
    github: {
        token: process.env.GITHUB_TOKEN || '',
        username: process.env.GITHUB_USERNAME || '',
    },
    project: {
        basePath: 'gcp-modules',
        outputPath: 'organized-modules',
    },
    module: {
        defaultBranch: 'main',
        moduleTypes: ['compute', 'storage', 'networking', 'database'],
    },
};