export function removeItem(array: any[], item: any): void {
    for (let i in array) {
        if (array[i] === item) {
            array.splice(parseInt(i), 1);
            break;
        }
    }
}

export function getRandomItem(arr: any[]): any {
    let randomIndex = Math.floor(Math.random() * arr.length);
    return arr[randomIndex];
}

export function insertAt(arr: any[], index: number, item: any): void {
    arr.splice(index, 0, item);
}
