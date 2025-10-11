export class Module {
    constructor(public name: string, public description: string) {}

    initialize() {
        console.log(`Initializing module: ${this.name}`);
    }

    execute() {
        console.log(`Executing module: ${this.name}`);
    }
}