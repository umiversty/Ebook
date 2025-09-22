import { render, screen } from "@testing-library/svelte";
import QuestionPanel from "../QuestionPanel.svelte";
import { describe, it, expect, vi } from "vitest";

describe("QuestionPanel component", () => {
  it("renders chip buttons with correct labels", () => {
    render(QuestionPanel, {
      props: {
        chips: [
          { text: "Multiple Choice", ariaLabel: "multiple choice chip", value: "mc" },
          { text: "Essay", ariaLabel: "essay chip", value: "essay" },
        ],
        onBloomChipClick: vi.fn(),
      },
    });

    expect(screen.getByRole("button", { name: /multiple choice/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /essay/i })).toBeInTheDocument();
  });
});
