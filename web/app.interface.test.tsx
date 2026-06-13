// @vitest-environment jsdom

import { cleanup, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import App from "./App";
import { ANY_FILTER, MultiFilter } from "./views/VisualizationView";

afterEach(cleanup);

beforeEach(() => {
  localStorage.clear();
  window.history.replaceState(null, "", "/");
});

describe("main application interface", () => {
  it("starts with precise numeric input and navigates to analysis", async () => {
    const user = userEvent.setup();
    render(<App />);

    const inputNavigation = screen.getByRole("button", { name: "Saisie" });
    await user.click(inputNavigation);

    expect(screen.getByRole("checkbox", { name: /Saisie précise/ })).toBeChecked();
    expect(screen.getAllByRole("spinbutton")).toHaveLength(16);

    await user.click(screen.getByRole("button", { name: "Se rendre à l’analyse" }));
    expect(screen.getByRole("heading", { name: /Analyse de/ })).toBeInTheDocument();
    expect(screen.getByText(/Cette lecture est heuristique/)).toBeInTheDocument();
  });

  it("exposes current navigation and persistent theme state", async () => {
    const user = userEvent.setup();
    render(<App />);

    expect(screen.getByRole("button", { name: "Accueil" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    const lightTheme = screen.getByRole("button", { name: "Thème clair" });
    await user.click(lightTheme);
    expect(lightTheme).toHaveAttribute("aria-pressed", "true");
    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("stores the current view and profile in the URL", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Analyse" }));

    expect(`${window.location.pathname}${window.location.search}`).toMatch(/^\/analysis\?profile=/);
    expect(screen.getByRole("button", { name: "Analyse" })).toHaveAttribute(
      "aria-current",
      "page",
    );
  });
});

describe("reference filter interface", () => {
  it("searches options and treats Any as a selectable value", async () => {
    const user = userEvent.setup();
    let selected: string[] = [];
    const { rerender } = render(
      <MultiFilter
        filterKey="country"
        label="Pays"
        options={["France", "Germany", "Greece"]}
        selected={selected}
        open
        language="fr"
        onOpenChange={() => undefined}
        onChange={(next) => {
          selected = next;
          rerender(
            <MultiFilter
              filterKey="country"
              label="Pays"
              options={["France", "Germany", "Greece"]}
              selected={selected}
              open
              language="fr"
              onOpenChange={() => undefined}
              onChange={() => undefined}
            />,
          );
        }}
      />,
    );

    const menu = screen.getByRole("group", { name: "Pays" });
    await user.type(within(menu).getByRole("searchbox"), "fra");
    expect(within(menu).getByText("France")).toBeInTheDocument();
    expect(within(menu).queryByText("Germany")).not.toBeInTheDocument();

    await user.clear(within(menu).getByRole("searchbox"));
    await user.click(within(menu).getByRole("checkbox", { name: "Any" }));
    expect(selected).toEqual([ANY_FILTER]);
  });
});
