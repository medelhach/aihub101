import { Suspense } from "react";

import { CompareDashboard } from "@/components/content/compare-dashboard";
import { listModels, type ModelSummary } from "@/services/api";

export const metadata = {
  title: "Model comparison",
  description: "Compare AI models across capability, cost, license, and safety dimensions.",
};

export default async function ComparePage() {
  let models: ModelSummary[] = [];
  try {
    models = await listModels();
  } catch {
    models = [];
  }

  return (
    <div className="mx-auto flex w-full max-w-[1280px] flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
      <header className="border-b border-rule pb-6">
        <p className="text-[0.7rem] font-semibold tracking-[0.32em] text-crimson uppercase">Desk tools</p>
        <h1 className="font-display mt-2 text-4xl tracking-tight md:text-5xl">Model comparison</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-ink/70">
          Select two to six models. The dashboard lines up provider, architecture, context,
          pricing, license, reasoning, multimodality, deployment, benchmarks, and safety notes.
        </p>
      </header>
      {models.length === 0 ? (
        <p className="border border-dashed border-rule bg-cream p-8 text-sm text-ink/70">
          The catalog is empty until the API is connected to the database.
        </p>
      ) : (
        <Suspense fallback={<p className="text-sm text-slate-600">Loading comparison tools…</p>}>
          <CompareDashboard models={models} />
        </Suspense>
      )}
    </div>
  );
}
