import {GenericHandler} from "../generic";

export class MlpchagSpecificHandler extends GenericHandler {
    constructor() {
        super()
    }

    get identifier(): string {
        return "mlpchag.neocities.org";
    }

    get prettyName(): string {
        return "mlpchag.neocities.org";
    }
}