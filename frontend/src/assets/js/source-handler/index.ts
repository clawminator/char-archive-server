import {BooruHandler} from "./booru";
import {ChubHandler} from "./chub";
import {InjectedHandler} from "./injected";
import {NyaimeHandler} from "./nyaime";
import {RisuaiHandler} from "./risuai";
import {GenericHandler} from "./generic";
import {PlaceholderHandler} from "./placeholder";
import {WebringHandler} from "./webring";
import {CharTavernHandler} from "./char_tavern";

export const handlers = {
    booru: BooruHandler,
    chub: ChubHandler,
    generic: GenericHandler,
    nyaime: NyaimeHandler,
    risuai: RisuaiHandler,
    webring: WebringHandler,
    'char-tavern': CharTavernHandler,
    injected: InjectedHandler,
    placeholder: PlaceholderHandler
}
