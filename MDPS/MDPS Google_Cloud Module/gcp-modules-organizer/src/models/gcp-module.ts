export interface GCPModule {
    name: string;
    description: string;
    path: string;
    dependencies?: string[];
    version?: string;
}