import {retryGetRequest} from "@/helpers/retry";

export async function getAddresses() {
    return await retryGetRequest(`/api/v1/address/?not_empty=1`)
}
