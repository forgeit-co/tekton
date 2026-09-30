import { apiClient } from "@/shared/foundation/api/client";

export const HEALTH_QUERY_KEY = ["health"] as const;
export const HEALTH_ENDPOINT = "/v1/health";

export async function fetchHealth(): Promise<{
  status: string;
  schema_revision: string;
}> {
  const { data, response } = await apiClient.GET(HEALTH_ENDPOINT);
  if (response.status < 200 || response.status >= 300) {
    throw new Error("The health request failed.");
  }
  if (!data) {
    throw new Error("The health response was empty.");
  }
  return data;
}
