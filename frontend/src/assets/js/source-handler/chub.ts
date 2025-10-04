import {SourceHandler} from "./source-handler";
import {doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data";

export class ChubHandler extends SourceHandler {
    constructor() {
        super("chub", "chub.ai", "bg-jasper-very-light", true, true, true, true, true, true)
    }

    get getDownloadKey(): string {
        return "starCount"
    }

    resolveCardLink(card): string {
        console.assert(card.type != null)
        let fullPath
        if (card.chub == null) {
            // Author view.
            fullPath = card.path
        } else {
            fullPath = card.chub.fullPath
        }
        return `/#/chub/${doubleEncodeUrlParam(card.author)}/${card.type}/${doubleEncodeUrlParam(fullPath[fullPath.length - 1])}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        if (!["character", "lorebook"].includes(fullPathParts[2])) {
            return null
        }
        // const cardName = fullPathParts[3]
        const url = `chub/node/${fullPathParts[2]}/${fullPathParts[1]}/${fullPathParts[3]}?chats=true&ratings=true&node=true`
        return new NodeLoadInfo(fullPathParts[2], url, decodeURIComponent(decodeURIComponent(fullPathParts[1])))
    }

    resolveDataDownload(card): [string, string] {
        const urlEnd = `${card.node.fullPath.join('/')}`
        const filename = `${card.author} -- ${card.name}`
        return [urlEnd, filename]
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        console.assert(author != null)
        return `${this._prettyName} - ${author} - ${name} - ${id}`
    }

    resolveCardAuthorName(card): string {
        let postfix = ""
        if (card.chub.anonymousAuthor != null) {
            postfix = ` (${card.chub.anonymousAuthor})`
        }
        return card.author + postfix
    }

    resolveCardAuthorLink(card): string {
        if (card.chub.anonymousAuthor != null) {
            return `/#/${this._identifier}/` + doubleEncodeUrlParam(card.chub.anonymousAuthor)
        } else {
            return super.resolveCardAuthorLink(card)
        }
    }

    resolveAuthorExternalUrl(authorData): string {
        return `https://characterhub.org/users/${authorData.username}`
    }

    resolveCardExternalUrl(cardData): string {
        return `https://characterhub.org/${cardData.type}s/${cardData.node.fullPath.join('/')}`
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
        return `chub.ai -- ${card.author} - ${card.name}`
    }

    resolveAuthorBio(authorData): string {
        if (authorData.username === "Anonymous") {
            return "This is an internal user for when an author wishes to publish a character anonymously."
        } else {
            return authorData.description
        }
    }

    protected generateCardAvatarApi(card): string {
        let fullPath: string[]
        if (card.node != null) {
            // On the item view.
            fullPath = card.node.fullPath
        } else if (card.chub != null) {
            // On the home page.
            fullPath = card.chub.fullPath
        } else {
            // On the author page.
            fullPath = card.path
        }
        // if (card.type === "lorebook") {
        //     fullPath = card.node.fullPath
        // }
        let cardType = card.type
        if (cardType == null) {
            cardType = "character"
        }
        if (fullPath[0] === "lorebooks") {
            fullPath = fullPath.slice(1)
        }
        return `api/archive/v1/${this._identifier}/image/${cardType}/${fullPath.join("/")}`
    }
}
