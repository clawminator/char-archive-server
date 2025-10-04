import {marked} from "marked";

export function parseMarkdown(string) {
    if (string != null) {
        return marked.parse(string)
    } else {
        return ""
    }
}