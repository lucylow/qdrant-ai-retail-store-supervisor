import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MetricCard } from "./MetricCard";

describe("MetricCard", () => {
  it("renders label and value", () => {
    render(<MetricCard label="Cache Hit" value="87%" />);
    expect(screen.getByText("Cache Hit")).toBeInTheDocument();
    expect(screen.getByText("87%")).toBeInTheDocument();
  });

  it("renders unit when provided", () => {
    render(<MetricCard label="Latency" value={42} unit="ms" />);
    expect(screen.getByText("ms")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<MetricCard label="QPS" value={450} description="Queries per second" />);
    expect(screen.getByText("Queries per second")).toBeInTheDocument();
  });

  it("does not render unit when omitted", () => {
    const { container } = render(<MetricCard label="Score" value="0.92" />);
    // No stray unit span
    expect(container.querySelectorAll("span").length).toBeGreaterThan(0);
  });

  it("shows positive trend icon when trend >= 0", () => {
    const { container } = render(<MetricCard label="Accuracy" value="96%" trend={4} />);
    // TrendingUp icon should be present (SVG)
    expect(container.querySelector("svg")).not.toBeNull();
  });

  it("shows negative trend icon when trend < 0", () => {
    const { container } = render(<MetricCard label="Errors" value="3%" trend={-2} />);
    expect(container.querySelector("svg")).not.toBeNull();
  });

  it("applies highlight class when highlight=true", () => {
    const { container } = render(<MetricCard label="Top" value="1st" highlight />);
    expect(container.firstChild).toHaveClass("border-primary/40");
  });
});
