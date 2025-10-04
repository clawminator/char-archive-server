import {SourceHandler} from "./source-handler";
import {doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data";

export class CharTavernHandler extends SourceHandler {
    constructor() {
        super("char-tavern", "Character Tavern", "char-tavern-red", true, true, true, true, true, false)
    }

    get getDownloadKey(): string {
        return "downloads"
    }

    resolveCardLink(card): string {
        console.assert(card.type != null)
        const path = card.id.split("/")
        return `/#/char-tavern/${doubleEncodeUrlParam(card.author)}/${card.type}/${doubleEncodeUrlParam(path[path.length - 1])}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        const url = `char-tavern/node/${fullPathParts[2]}/${fullPathParts[1]}/${fullPathParts[3]}?chats=true&ratings=true&node=true`
        return new NodeLoadInfo(fullPathParts[2], url, decodeURIComponent(decodeURIComponent(fullPathParts[1])))
    }

    resolveDataDownload(card): [string, string] {
        const urlEnd = `${card.node.path.join('/')}`
        const filename = `${card.author} -- ${card.name}`
        return [urlEnd, filename]
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        console.assert(author != null)
        return `${this._prettyName} - ${author} - ${name} - ${id}`
    }

    resolveAuthorExternalUrl(authorData): string {
        return `https://character-tavern.com/author/${authorData.username}`
    }

    resolveCardExternalUrl(cardData): string {
        return `https://character-tavern.com/character/${cardData.node.path.join('/')}`
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        let imgHash: string
        if (authorData.username === "Anonymous" || authorData.missing) {
            imgHash = "c18b2a4ef19765ee8adb81f6e3aae1d2"
        } else {
            imgHash = authorData.avatar.hash
        }
        return [`api/archive/v1/image/${imgHash}?thumbnail=true&max=200&square=true`, null]
    }

    pageName(card): string {
        return `Character Tavern -- ${card.author} - ${card.name}`
    }

    resolveAuthorBio(authorData): string {
        return authorData.description
    }

    protected generateCardAvatarApi(card): string {
        return `api/archive/v1/${this._identifier}/image/character/${card.id}`
    }
}
