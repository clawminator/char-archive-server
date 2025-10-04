import {doubleEncodeUrlParam} from "../strings";
import {APIHOST} from "../../../components/config";
import {NodeLoadInfo} from "./types/load-data";

export class SourceHandler {
    protected readonly _identifier: string
    protected readonly _prettyName: string
    protected readonly _bgColor: string
    protected readonly _hasAuthors: boolean
    protected readonly _hasVersions: boolean
    protected readonly _hasExternal: boolean
    protected readonly _hasDownloads: boolean
    protected readonly _hasComments: boolean
    protected readonly _hasRatings: boolean

    constructor(identifier: string, prettyName: string, bgColor: string, hasAuthors: boolean, hasVersions: boolean, hasExternal: boolean, hasDownloads: boolean, hasComments: boolean, hasRatings: boolean) {
        this._identifier = identifier
        this._prettyName = prettyName
        this._bgColor = bgColor
        this._hasAuthors = hasAuthors
        this._hasVersions = hasVersions
        this._hasExternal = hasExternal
        this._hasDownloads = hasDownloads
        this._hasComments = hasComments
        this._hasRatings = hasRatings
    }

    get identifier(): string {
        return this._identifier
    }

    get prettyName(): string {
        return this._prettyName
    }

    get cardColor(): string {
        return this._bgColor
    }

    get hasAuthors(): boolean {
        return this._hasAuthors
    }

    get hasVersions(): boolean {
        return this._hasVersions
    }

    get hasExternal(): boolean {
        return this._hasExternal
    }

    get hasDownloads(): boolean {
        return this._hasDownloads
    }

    get hasComments(): boolean {
        return this._hasComments
    }

    get hasRatings(): boolean {
        return this._hasRatings
    }

    get getDownloadKey(): string {
        throw new Error("Method is not implemented")
    }

    resolveCardNameStr(card): string {
        let authorStr = ""
        if (card.data.author != null) {
            authorStr = `${card.data.author} - `
        }
        return `${authorStr}${card.data.name}`
    }

    resolveCardLink(card): string {
        throw new Error("Method is not implemented")
    }

    resolveCardAuthorName(card): string {
        return card.author
    }

    resolveCardAuthorLink(card): string {
        console.assert(card.author != null && card.author !== "")
        return `/#/${this._identifier}/` + doubleEncodeUrlParam(card.author)
    }

    resolveCardAvatarURL(card, blurImages: boolean = false, thumbnail: boolean = false, maxSize: number = null, jpegFormat: boolean = false): string {
        let url = `${APIHOST}/${this.generateCardAvatarApi(card)}`
        let urlParams = new URLSearchParams()

        let width = maxSize || (blurImages ? 200 : 40)
        if (maxSize != null) {
            urlParams.append('max', `${width}`)
        }

        if (thumbnail) {
            urlParams.append('thumbnail', 'true')
            urlParams.append('square', 'true')
            if (!jpegFormat) {
                urlParams.append('format', 'jpeg');
            }
        }

        if (jpegFormat && !urlParams.has('format')) {
            urlParams.append('format', 'jpeg');
        }

        if (blurImages) {
            urlParams.append('blur', 'true')
        } else {
            // Don't optimize blurred images
            urlParams.append('optimize', 'true')
        }

        if (urlParams.toString()) {
            url = url.includes('?') ? `${url}&${urlParams.toString()}` : `${url}?${urlParams.toString()}`
        }

        return url
    }

    resolveAuthorUrl(authorName: string): string {
        if (!this._hasAuthors) {
            return null
        } else {
            return `${APIHOST}/api/archive/v1/${this._identifier}/user/${authorName}`
        }
    }

    handleNodeLoad(fullPathParts: string[]): NodeLoadInfo | null {
        throw new Error("Method is not implemented")
    }

    resolveDataDownload(card): [string, string] {
        throw new Error("Method is not implemented")
    }

    generateMatoSearchResult(name: string, id: string, author: string = null): string {
        throw new Error("Method is not implemented")
    }

    resolveAuthorExternalUrl(authorData): string {
        throw new Error("Method is not implemented")
    }

    resolveCardExternalUrl(cardData): string {
        throw new Error("Method is not implemented")
    }

    resolveAuthorAvatar(authorData): [string, string | null] {
        throw new Error("Method is not implemented")
    }

    pageName(card): string {
        throw new Error("Method is not implemented")
    }

    resolveAuthorBio(authorData): string {
        // Returning `null` disables the bio on the author page.
        return null
    }

    protected generateCardAvatarApi(card): string {
        throw new Error("Method is not implemented")
    }
}
