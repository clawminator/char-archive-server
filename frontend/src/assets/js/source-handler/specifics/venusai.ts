import {GenericHandler} from "../generic";

export class VenusAISpecificHandler extends GenericHandler {
    constructor() {
        super()
    }

    get identifier(): string {
        return "venusai";
    }

    get prettyName(): string {
        return "VenusAI";
    }

    get cardColor(): string {
        return "bg-teal-very-light";
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        return `${this.prettyName} - ${name} - ${id}`
    }
}