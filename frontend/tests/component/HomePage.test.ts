import { render, screen } from "@testing-library/vue";
import { describe, expect, it } from "vitest";
import HomePage from "@/features/home/HomePage.vue";
import { i18n } from "@/shared/foundation/i18n";

describe("HomePage", () => {
  it("shows the localized home heading", () => {
    render(HomePage, { global: { plugins: [i18n] } });

    expect(
      screen.getByRole("heading", {
        name: "Build your home, one step at a time",
      }),
    ).toBeInTheDocument();
  });
});
