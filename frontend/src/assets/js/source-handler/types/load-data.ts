export class NodeLoadInfo {
    protected readonly _type: string
    protected readonly _apiUrl: string
    protected readonly _author: string | null

    constructor(type: string, apiUrl: string, author: string = null) {
        this._type = type
        this._apiUrl = apiUrl
        this._author = author
    }

    get type() {
        return this._type
    }

    get apiUrl() {
        return this._apiUrl
    }

    get author() {
        return this._author
    }
}