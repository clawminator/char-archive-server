import {SourceHandler} from "./source-handler";

export class PlaceholderHandler extends SourceHandler {
    constructor() {
        super("", "", "bg-gray-300", false, false, false, false, false, false)
    }

    resolveCardLink(card): string {
        return ''
    }

    resolveCardAuthorLink(card): string {
        return ''
    }

    protected generateCardAvatarApi(card): string {
        return ''

    }
}
