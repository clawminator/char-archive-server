import {SourceHandler} from "./source-handler";

export class InjectedHandler extends SourceHandler {
    constructor() {
        super("injected", "", "glownigger-bg", false, false, false, false, false, false)
    }

    resolveCardLink(card): string {
        return "https://char-archive.example.com/Just Looking - Tantalization, Lolicon, and Virtual Girls.pdf"
    }

    resolveCardAuthorLink(card): string {
        return "https://char-archive.example.com/Just Looking - Tantalization, Lolicon, and Virtual Girls.pdf"
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        return "Injected"
    }

    protected generateCardAvatarApi(card): string {
        return card.img
    }
}
