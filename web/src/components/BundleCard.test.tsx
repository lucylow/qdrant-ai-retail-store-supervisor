import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { BundleCard } from "./BundleCard";
import type { Product } from "@/lib/api";

const PRODUCTS: Product[] = [
  { id: "p1", name: "MSR Hubba Hubba NX 2", price: 189 },
  { id: "p2", name: "Sea to Summit Spark SP1", price: 239 },
];

describe("BundleCard", () => {
  it("renders all product names", () => {
    render(<BundleCard products={PRODUCTS} />);
    expect(screen.getByText("MSR Hubba Hubba NX 2")).toBeInTheDocument();
    expect(screen.getByText("Sea to Summit Spark SP1")).toBeInTheDocument();
  });

  it("renders product prices with currency", () => {
    render(<BundleCard products={PRODUCTS} currency="CHF" />);
    expect(screen.getByText("CHF 189")).toBeInTheDocument();
    expect(screen.getByText("CHF 239")).toBeInTheDocument();
  });

  it("renders total price when provided", () => {
    render(<BundleCard products={PRODUCTS} totalPrice={428} currency="CHF" />);
    expect(screen.getByText("CHF 428")).toBeInTheDocument();
  });

  it("renders goal text as a quote when provided", () => {
    render(<BundleCard products={PRODUCTS} goalText="2-person tent under 200CHF" />);
    expect(screen.getByText(/"2-person tent under 200CHF"/)).toBeInTheDocument();
  });

  it("renders ETA when provided", () => {
    render(<BundleCard products={PRODUCTS} eta="Fri delivery" />);
    expect(screen.getByText("Fri delivery")).toBeInTheDocument();
  });

  it("renders confidence bar when confidence is provided", () => {
    const { container } = render(<BundleCard products={PRODUCTS} confidence={0.92} />);
    // The percentage text
    expect(screen.getByText("92%")).toBeInTheDocument();
    // The progress bar fill div
    const progressBars = container.querySelectorAll("[style]");
    expect(progressBars.length).toBeGreaterThan(0);
  });

  it("renders 'title' as fallback when 'name' is absent", () => {
    const products: Product[] = [{ id: "p3", title: "Black Diamond Poles", price: 169 }];
    render(<BundleCard products={products} />);
    expect(screen.getByText("Black Diamond Poles")).toBeInTheDocument();
  });

  it("renders empty gracefully with no products", () => {
    const { container } = render(<BundleCard products={[]} />);
    expect(container.firstChild).not.toBeNull();
  });
});
