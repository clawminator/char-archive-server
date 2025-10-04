import {SourceHandler} from "./source-handler";
import {doubleDecodeUrlParam, doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data";

export class RisuaiHandler extends SourceHandler {
    constructor() {
        super("risuai", "RisuAI", "risuai-blue-very-light", true, true, true, true, false, false)
    }

    get getDownloadKey(): string {
        return "downloads"
    }

    resolveCardLink(card): string {
        return `/#/risuai/${doubleEncodeUrlParam(card.author)}/character/${card.id}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        const cardType = fullPathParts[2]
        const cardID = fullPathParts[3]
        const author = doubleDecodeUrlParam(fullPathParts[1])
        const url = `risuai/node/character/${author}/${cardID}?ratings=true&node=true`
        return new NodeLoadInfo(cardType, url, doubleDecodeUrlParam(author))
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        console.assert(author != null)
        return `${this._prettyName} - ${author} - ${name} - ${id}`
    }

    resolveDataDownload(card): [string, string] {
        const urlEnd = `${card.author}/${card.id}`
        const filename = `${card.name} -- ${card.id}`
        return [urlEnd, filename]
    }

    resolveAuthorExternalUrl(authorData): string {
        return `https://realm.risuai.net/creator/${authorData.username}`
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        return ["img/risuai-logo.png", null]
    }

    resolveCardExternalUrl(cardData): string {
        return `https://realm.risuai.net/character/${cardData.id}`
    }

    pageName(card): string {
        return `RisuAI -- ${card.author} - ${card.name}`
    }

    resolveAuthorBio(authorData): string {
        if (authorData.description != null) {
            return authorData.description.replace("\n", "<br>")
        }
    }

    protected generateCardAvatarApi(card): string {
        return `api/archive/v1/${this._identifier}/image/character/${card.author}/${card.id}`
    }
}
