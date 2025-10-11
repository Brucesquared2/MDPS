interface ProjectStructure {
    modules: GCPModule[];
    directories: string[];
}

interface GCPModule {
    name: string;
    description: string;
    path: string;
}