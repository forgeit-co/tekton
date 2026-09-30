import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { render, screen } from "@testing-library/vue";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import HealthIndicatorContainer from "@/features/home/components/HealthIndicatorContainer.vue";
import { i18n } from "@/shared/foundation/i18n";
import { HEALTH_API_PATH } from "../../../msw/handlers";
import { server } from "../../../msw/server";

function renderHealthIndicator() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(HealthIndicatorContainer, {
    global: {
      plugins: [i18n, [VueQueryPlugin, { queryClient }]],
    },
  });
}

describe("HealthIndicator", () => {
  it("shows the healthy service status from the health API", async () => {
    server.use(
      http.get(`*${HEALTH_API_PATH}`, () =>
        HttpResponse.json({ status: "ok", schema_revision: "2026-09" }),
      ),
    );

    renderHealthIndicator();

    expect(
      await screen.findByText("All systems operational"),
    ).toBeInTheDocument();
  });

  it("shows an error state when the health API returns a problem response", async () => {
    server.use(
      http.get(`*${HEALTH_API_PATH}`, () =>
        HttpResponse.json(
          {
            type: "urn:tekton:error:service.unavailable",
            title: "Service unavailable",
            status: 503,
            code: "service.unavailable",
            detail: "The health service is unavailable.",
            params: {},
          },
          {
            status: 503,
            headers: { "content-type": "application/problem+json" },
          },
        ),
      ),
    );

    renderHealthIndicator();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Service health could not be confirmed",
    );
    expect(
      screen.getByRole("button", { name: "Try again" }),
    ).toBeInTheDocument();
  });
});
