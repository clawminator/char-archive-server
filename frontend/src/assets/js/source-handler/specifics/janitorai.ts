import {GenericHandler} from "../generic";

export class JanitorAISpecificHandler extends GenericHandler {
    constructor() {
        super()
    }

    get identifier(): string {
        return "janitorai";
    }

    get prettyName(): string {
        return "JanitorAI";
    }

    get cardColor(): string {
        return "bg-dutch-white-very-light";
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        return `${this.prettyName} - ${name} - ${id}`
    }
}