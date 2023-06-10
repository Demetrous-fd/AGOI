import {retryGetRequest} from "@/helpers/retry";

export async function getLocations(addressId) {
    return await retryGetRequest(`/api/v1/location/?address=${addressId}`)
}
