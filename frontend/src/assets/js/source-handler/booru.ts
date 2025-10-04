import {SourceHandler} from "./source-handler";
import {doubleDecodeUrlParam, doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data"

export class BooruHandler extends SourceHandler {
    constructor() {
        super("booru", "Booru", "bg-violet-very-light", true, false, false, false, true, false)
    }

    resolveCardLink(card): string {
        return `/#/booru/${doubleEncodeUrlParam(card.author)}/${doubleEncodeUrlParam(card.name)}${card.id}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        const parts = fullPathParts[2].split("+")
        const cardID = "+" + parts.pop()
        // const cardName = doubleDecodeUrlParam(parts.join("++"))
        const author = fullPathParts[1]
        const url = `booru/node/character/${cardID}?ratings=true&node=true`
        return new NodeLoadInfo('character', url, doubleDecodeUrlParam(author))
    }

    resolveDataDownload(card): [string, string] {
        const urlEnd = card.id
        const filename = `${card.name} -- ${card.id}`
        return [urlEnd, filename]
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        console.assert(author != null)
        return `${this._prettyName} - ${author} - ${name} - ${id}`
    }

    resolveAuthorExternalUrl(authorData): string {
        return
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        return ["img/sites/booru-logo.svg", null]
    }

    pageName(card): string {
        return `Booru -- ${card.author} - ${card.name} - ${card.id}`
    }

    protected generateCardAvatarApi(card): string {
        return `api/archive/v1/${this._identifier}/image/character/${card.id}`
    }
}
