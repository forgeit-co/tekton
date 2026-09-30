import { useQuery } from "@tanstack/vue-query";
import { fetchHealth, HEALTH_QUERY_KEY } from "../api/healthApi";

export function useHealthQuery() {
  return useQuery({
    queryKey: HEALTH_QUERY_KEY,
    queryFn: fetchHealth,
    retry: false,
  });
}
