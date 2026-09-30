import { QueryClient } from "@tanstack/vue-query";

export const vueQueryOptions = {
  defaultOptions: {
    queries: {
      staleTime: Infinity,
      refetchOnWindowFocus: false,
      refetchOnReconnect: false,
    },
  },
} as const;

export const queryClient = new QueryClient(vueQueryOptions);
