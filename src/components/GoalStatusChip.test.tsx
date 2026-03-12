import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { GoalStatusChip } from "./GoalStatusChip";

describe("GoalStatusChip", () => {
  it("renders 'Open' for open status", () => {
    render(<GoalStatusChip status="open" />);
    expect(screen.getByText("Open")).toBeInTheDocument();
  });

  it("renders 'Pending' for pending status", () => {
    render(<GoalStatusChip status="pending" />);
    expect(screen.getByText("Pending")).toBeInTheDocument();
  });

  it("renders 'Fulfilled' for fulfilled status", () => {
    render(<GoalStatusChip status="fulfilled" />);
    expect(screen.getByText("Fulfilled")).toBeInTheDocument();
  });

  it("renders 'Failed' for failed status", () => {
    render(<GoalStatusChip status="failed" />);
    expect(screen.getByText("Failed")).toBeInTheDocument();
  });

  it("renders as an inline span element", () => {
    const { container } = render(<GoalStatusChip status="open" />);
    expect(container.firstChild?.nodeName).toBe("SPAN");
  });

  it("includes a colored dot indicator", () => {
    const { container } = render(<GoalStatusChip status="fulfilled" />);
    // The dot is the inner span with rounded-full
    const dots = container.querySelectorAll("span > span");
    expect(dots.length).toBeGreaterThan(0);
  });
});
