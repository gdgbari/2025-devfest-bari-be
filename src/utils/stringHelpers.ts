import * as crypto from "crypto";

export function generateUniqueRandomStrings(N: number) {
    return Array.from({ length: N }, () => crypto.randomUUID())
};

function generateUniqueRandomStringsLegacy(N: number, length = 8) {
    const uniqueStrings = new Set();
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;

    while (uniqueStrings.size < N) {
        let randomString = '';
        for (let i = 0; i < length; i++) {
            randomString += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        uniqueStrings.add(randomString);
    }

    return Array.from(uniqueStrings);
}
