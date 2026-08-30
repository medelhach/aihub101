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
    <div className="flex w-full flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="text-3xl font-semibold tracking-tight">Model comparison</h1>
        <p className="mt-3 text-base leading-7 text-slate-600">
          Select two to six models. The dashboard lines up provider, architecture, context,
          pricing, license, reasoning, multimodality, deployment, benchmarks, and safety notes.
        </p>
      </header>
      {models.length === 0 ? (
        <p className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-sm text-slate-600">
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
