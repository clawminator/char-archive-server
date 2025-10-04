import {GenericHandler} from "../generic";

export class RokoSpecificHandler extends GenericHandler {
    constructor() {
        super()
    }

    get identifier(): string {
        return "roko";
    }

    get prettyName(): string {
        return "Roko";
    }

    get cardColor(): string {
        return "bg-sea-green-very-light";
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        return `${this.prettyName} - ${name} - ${id}`
    }
}