import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import App from "./App";
import type { Product } from "./types";

function respond(body: unknown, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(body), { status }));
}

function mockFetch(handler: (init?: RequestInit) => Promise<Response>) {
  const fetch = vi.fn((_url: string, init?: RequestInit) => handler(init));
  vi.stubGlobal("fetch", fetch);
  return fetch;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

test("lists products", async () => {
  mockFetch(() => respond([{ id: 1, name: "P1" }]));

  render(<App />);

  expect(await screen.findByText("P1")).toBeInTheDocument();
});

test("creates a product and shows it", async () => {
  const products: Product[] = [];
  const fetch = mockFetch((init) => {
    if (init?.method === "POST") {
      const product = { id: 1, ...JSON.parse(init.body as string) };
      products.push(product);
      return respond(product, 201);
    }
    return respond(products);
  });

  render(<App />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "P1" } });
  fireEvent.click(screen.getByRole("button", { name: "Create" }));

  expect(await screen.findByText("P1")).toBeInTheDocument();
  expect(screen.getByRole("textbox")).toHaveValue("");
  expect(fetch).toHaveBeenCalledWith("/api/products", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ name: "P1" }),
  });
});

test("disables create for a blank name", () => {
  mockFetch(() => respond([]));

  render(<App />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "  " } });

  expect(screen.getByRole("button", { name: "Create" })).toBeDisabled();
});

test("shows the error when create fails", async () => {
  const detail = '{"detail":"name must not be blank"}';
  mockFetch((init) =>
    init?.method === "POST"
      ? Promise.resolve(new Response(detail, { status: 422 }))
      : respond([]),
  );

  render(<App />);
  fireEvent.change(screen.getByRole("textbox"), { target: { value: "P1" } });
  fireEvent.click(screen.getByRole("button", { name: "Create" }));

  expect(await screen.findByText(detail)).toBeInTheDocument();
});
