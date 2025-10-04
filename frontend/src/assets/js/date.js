import {DateTime} from "luxon";

export function FormatDate(date) {
    return DateTime.fromISO(date).toLocaleString(DateTime.DATETIME_MED);
}

export function DateFromSeconds(date) {
    return DateTime.fromSeconds(date).toLocaleString(DateTime.DATETIME_MED);
}

export function FormatSize(size) {
    const i = size === 0 ? 0 : Math.floor(Math.log(size) / Math.log(1024));
    return (size / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i];
}