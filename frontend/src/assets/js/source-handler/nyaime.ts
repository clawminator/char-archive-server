import {SourceHandler} from "./source-handler";
import {doubleDecodeUrlParam, doubleEncodeUrlParam} from "../strings";
import {NodeLoadInfo} from "./types/load-data";

export class NyaimeHandler extends SourceHandler {
    constructor() {
        super("nyaime", "nyai.me", "bg-harvest-gold-very-light", true, true, true, true, true, false)
    }

    get getDownloadKey(): string {
        return "downloads"
    }

    resolveCardLink(card): string {
        return `/#/nyaime/${doubleEncodeUrlParam(card.author)}/character/${doubleEncodeUrlParam(card.name)}+${card.id}`
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        const author = fullPathParts[1]
        const [cardName, id] = fullPathParts[fullPathParts.length - 1].split("+").map(part => doubleDecodeUrlParam(part))
        const cardType = fullPathParts[2]
        const url = `nyaime/node/${fullPathParts[2]}/${author}/${id}?ratings=true&node=true`
        return new NodeLoadInfo(cardType, url, decodeURIComponent(decodeURIComponent(author)))
    }

    resolveDataDownload(card): [string, string] {
        const urlEnd = `${doubleEncodeUrlParam(card.author)}/${card.id}`
        const filename = `${card.author} -- ${card.name} ${card.id}`
        return [urlEnd, filename]
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        console.assert(author != null)
        return `${this._prettyName} - ${author} - ${name} - ${id}`
    }

    resolveAuthorExternalUrl(authorData) {
        return `https://nyai.me/user/${authorData.username}`
    }

    resolveCardExternalUrl(cardData): string {
        const name = cardData.name.replace(/ /g, "-").replace(/\//g, "-")
        const encId = encodeToBase26(cardData.id).toLowerCase()
        return `https://nyai.me/ai/bots/${name}_${encId}`
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        return ["img/nyaime-logo.png", null]
    }

    pageName(card): string {
        return `nyai.me -- ${card.author} - ${card.name}`
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

function encodeToBase26(input: string | number): string {
    const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let result = "";
    let num: number;
    if (typeof input === "string") {
        num = parseInt(input, 10);
    } else {
        num = input;
    }
    while (num > 0) {
        const remainder = (num - 1) % 26;
        result = alphabet[remainder] + result;
        num = Math.floor((num - 1) / 26);
    }
    return result || "A";
}
