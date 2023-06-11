import {retryGetRequest} from "@/helpers/retry";
import axios from "axios";

export async function getReport(reportId) {
    return await retryGetRequest(`/api/v1/report/${reportId}/`)
}

export async function getReports() {
    return await retryGetRequest(`/api/v1/report/`)
}

export async function getCountInstances(reportId) {
    return await retryGetRequest(`/api/v1/report/${reportId}/item/count/`)
}

export async function getCountScannedInstances(reportId) {
    return await retryGetRequest(`/api/v1/report/${reportId}/item/scanned/count/`)
}

export async function getScannedInstancesId(reportId) {
    return await retryGetRequest(`/api/v1/report/${reportId}/item/scanned/`)
}

export async function createReportItem(reportId, instanceId) {
    return await axios.post(`/api/v1/report/${reportId}/item/`, {
        instance: instanceId
    })
}

export async function createReport(locationId, userId) {
    return await axios.post(`/api/v1/report/`, {
        location: locationId,
        user: userId
    })
}

export async function deleteReport(reportId) {
    return await axios.delete(`/api/v1/report/${reportId}/`)
}

export async function finishReport(reportId) {
    return await axios.patch(`/api/v1/report/${reportId}/`, {status: "finish"})
}

export async function listenReportEvent(callback) {
    let backend = import.meta.env.VITE_API_URL.split("//")[1]
    let socket = new WebSocket(
        `${location.protocol !== 'https:'? 'ws' : 'wss'}://${backend}/ws/`
    )
    socket.onmessage = callback
}

export function getReportsFromLocalStorage() {
    let reports = JSON.parse(localStorage.getItem("reports") || "[]")
    if (reports === null)
        reports = []
    return reports
}

export function saveReportToLocalStorage(report) {
    const reports = getReportsFromLocalStorage()
    for (const value of reports) {
        if (value.id === report.id)
            return
    }
    reports.push(report)
    localStorage.setItem("reports", JSON.stringify(reports))
}

export function removeReportFromLocalStorage(id) {
    const reports = getReportsFromLocalStorage()
    const result = reports.filter(report => report.id !== id)
    localStorage.setItem("reports", JSON.stringify(result))
}

export function downloadReport(id, filename) {
    axios.get(`api/v1/report/${id}/download/`, {responseType: 'blob'}).then(
        response => {
            var url = window.URL.createObjectURL(new Blob([response.data]));
            var a = document.createElement('a');
            a.href = url;
            a.download = `${filename}.xlsx`;
            document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
            a.click();
            a.remove();  //afterwards we remove the element again
        }
    )
}