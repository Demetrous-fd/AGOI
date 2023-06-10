import {retryGetRequest} from "@/helpers/retry";

export async function getInstance(id) {
    return await retryGetRequest(`/api/v1/instance/${id}/`)
}
