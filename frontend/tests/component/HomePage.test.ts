import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";
import HomePage from "@/features/home/HomePage.vue";
import { i18n } from "@/shared/foundation/i18n";

describe("HomePage", () => {
  it("shows the localized heading and health served by the default handler", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(HomePage, {
      global: {
        plugins: [i18n, [VueQueryPlugin, { queryClient }]],
      },
    });

    expect(
      screen.getByRole("heading", {
        name: "Build your home, one step at a time",
      }),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("All systems operational"),
    ).toBeInTheDocument();
  });
});
