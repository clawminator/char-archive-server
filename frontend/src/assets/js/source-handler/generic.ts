import {SourceHandler} from "./source-handler";
import {doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data";


export class GenericHandler extends SourceHandler {
    constructor() {
        super("generic", "", "bg-gold-very-llight", true, false, false, false, false, false)
    }

    resolveCardLink(card): string {
        return `/#/generic/${doubleEncodeUrlParam(card.name)}+${card.id}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        const parts = fullPathParts[1].split("+")
        const cardDataHash = parts.pop()
        // const cardName = doubleDecodeUrlParam(parts.join(" - "))
        const url = `generic/node/character/${cardDataHash}`
        return new NodeLoadInfo(fullPathParts[0], url)
    }

    resolveDataDownload(card): [string, string] {
        const urlEnd = card.id
        const filename = `${card.name} -- ${card.id}`
        return [urlEnd, filename]
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        return `${this._prettyName} - ${name} - ${id}`
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        return ["img/sites/generic-logo.png", null]
    }

    protected generateCardAvatarApi(card): string {
        return `api/archive/v1/${this._identifier}/image/character/${card.id}`
    }

    pageName(card): string {
        return `${card.type} - ${card.name}`
    }

}
