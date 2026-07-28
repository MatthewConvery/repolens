export type HealthResponse = {
    status: String;
};

export async function fetchHealth(): Promise<HealthResponse> {
    const response = await fetch("http://127.0.0.1:8000/health");

    if (!response.ok) {
        throw new Error(`Health request failed: ${response.status}`);
    }

    return response.json() as Promise<HealthResponse>;
}

export type UploadResponse = {
    filename: string;
    content_type: string;
    size_bytes: string;
    status: string;
};

export async function uploadRepository(
    file: File
): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
    });

    if (!response.ok) {
        const errorBody = await response.json().catch(() => null);

        throw new Error(
            errorBody?.detail ?? `Upload failed: ${response.status}`,
        );
    }

    return response.json() as Promise<UploadResponse>;
}