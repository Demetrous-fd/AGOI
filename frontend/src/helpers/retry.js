import axios from "axios";

export function delay(time) {
    return new Promise(resolve => setTimeout(resolve, time));
}

export async function retryGetRequest(url, retry=true) {
    try {
        return await axios.get(url)
    } catch {
        if (retry) {
            await delay(100)
            return retryGetRequest(url, false)
        }
    }
}