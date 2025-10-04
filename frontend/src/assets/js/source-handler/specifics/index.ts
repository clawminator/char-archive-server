import {RokoSpecificHandler} from "./roko";
import {JanitorAISpecificHandler} from "./janitorai";
import {VenusAISpecificHandler} from "./venusai";
import {CatboxSpecificHandler} from "./catbox";
import {MlpchagSpecificHandler} from "./mlpchag";

export const specificHandlers = {
    roko: RokoSpecificHandler,
    janitorai: JanitorAISpecificHandler,
    venusai: VenusAISpecificHandler,
    catbox: CatboxSpecificHandler,
    mlpchag_neocities_org: MlpchagSpecificHandler,
}
