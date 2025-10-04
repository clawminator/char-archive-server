import {handlers} from "./index";
import {specificHandlers} from "./specifics";
import {SourceHandler} from "./source-handler";

export function initializeHandler(identifier: string, specificIdentifier: string = null, throwError: boolean = true): SourceHandler | null {
    if (specificIdentifier != null && specificIdentifier !== "generic") {
        specificIdentifier = specificIdentifier.replace(/\./g, "_")
        const SpecificHandlerClass = specificHandlers[specificIdentifier]
        if (SpecificHandlerClass != null) {
            return new SpecificHandlerClass()
        } else if (throwError) {
            throw new Error(`No specific handler found for identifier "${specificIdentifier}"`)
        }
    } else {
        const HandlerClass = handlers[identifier]
        if (HandlerClass != null) {
            return new HandlerClass()
        } else if (throwError) {
            throw new Error(`No handler found for identifier "${identifier}"`)
        }
    }
}
