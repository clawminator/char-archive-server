import {GenericHandler} from "../generic";

export class CatboxSpecificHandler extends GenericHandler {
    constructor() {
        super()
    }

    get identifier(): string {
        return "catbox";
    }

    get prettyName(): string {
        return "Catbox";
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        return `${this.prettyName} - ${name} - ${id}`
    }
}