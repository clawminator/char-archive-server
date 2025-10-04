import {SourceHandler} from "./source-handler";
import {doubleDecodeUrlParam, doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data"

export class WebringHandler extends SourceHandler {
    constructor() {
        super("webring", "Webring", "bg-cafe-noir-very-light", true, false, false, false, false, false)
    }

    resolveCardLink(card): string {
        return `/#/${this._identifier}/${doubleEncodeUrlParam(card.author)}/${card.id}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        const cardID = fullPathParts[2]
        const author = fullPathParts[1]
        const url = `${this._identifier}/node/character/${cardID}?ratings=true&node=true`
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
        return `https://${authorData.username}`
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        return [`api/archive/v1/webring/icon/${authorData.username}`, "/img/webring-logo.png"]
    }

    pageName(card): string {
        return `Webring -- ${card.author} - ${card.name}`
    }

    protected generateCardAvatarApi(card): string {
        return `api/archive/v1/${this._identifier}/image/character/${card.id}`
    }

}
