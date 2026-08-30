"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { cn } from "@/lib/utils";
import { compareModels, type Comparison, type ModelSummary } from "@/services/api";

type CompareDashboardProps = {
  models: ModelSummary[];
};

export function CompareDashboard({ models }: CompareDashboardProps) {
  const searchParams = useSearchParams();
  const router = useRouter();
  const initial = searchParams.get("models")?.split(",").filter(Boolean) ?? [];
  const [selected, setSelected] = useState<string[]>(initial.slice(0, 6));
  const [query, setQuery] = useState("");
  const [comparison, setComparison] = useState<Comparison | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return models.filter((model) => {
      if (!needle) {
        return true;
      }
      return `${model.name} ${model.provider} ${model.family} ${model.modality}`
        .toLowerCase()
        .includes(needle);
    });
  }, [models, query]);

  function toggle(slug: string) {
    setSelected((current) => {
      if (current.includes(slug)) {
        return current.filter((item) => item !== slug);
      }
      if (current.length >= 6) {
        return current;
      }
      return [...current, slug];
    });
  }

  function runCompare() {
    if (selected.length < 2) {
      setError("Select at least two models.");
      return;
    }
    setError(null);
    startTransition(async () => {
      try {
        const result = await compareModels(selected);
        setComparison(result);
        router.replace(`/compare?models=${selected.join(",")}`, { scroll: false });
      } catch {
        setError("Comparison failed. Confirm the API is running.");
      }
    });
  }

  return (
    <div className="flex w-full flex-col gap-8">
      <div className="rounded-2xl border border-slate-200 bg-white p-6">
        <label className="text-sm font-medium text-slate-700" htmlFor="model-filter">
          Find models
        </label>
        <input
          id="model-filter"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by name, provider, or modality"
          className="mt-2 w-full rounded-xl border border-slate-300 px-3 py-2 text-sm"
        />
        <p className="mt-3 text-sm text-slate-600">
          Selected {selected.length} / 6. Choose 2–6 models, then compare every published
          characteristic.
        </p>
        <div className="mt-4 grid max-h-80 gap-2 overflow-auto sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((model) => {
            const checked = selected.includes(model.slug);
            return (
              <label
                key={model.slug}
                className={cn(
                  "flex cursor-pointer items-start gap-3 rounded-xl border px-3 py-2 text-sm",
                  checked ? "border-slate-950 bg-slate-50" : "border-slate-200",
                )}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggle(model.slug)}
                  className="mt-1"
                />
                <span>
                  <span className="block font-medium">{model.name}</span>
                  <span className="text-xs text-slate-500">
                    {model.provider} · {model.modality}
                  </span>
                </span>
              </label>
            );
          })}
        </div>
        <button
          type="button"
          onClick={runCompare}
          disabled={pending}
          className="mt-6 rounded-full bg-slate-950 px-5 py-2 text-sm font-medium text-white disabled:opacity-60"
        >
          {pending ? "Comparing…" : "Compare selected models"}
        </button>
        {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
      </div>

      {comparison ? <ComparisonTable comparison={comparison} /> : null}
    </div>
  );
}

function ComparisonTable({ comparison }: { comparison: Comparison }) {
  return (
    <div className="flex flex-col gap-6">
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Models" value={String(comparison.summary.model_count)} />
        <Stat label="Open weights" value={String(comparison.summary.open_weights_count)} />
        <Stat label="Reasoning SKUs" value={String(comparison.summary.reasoning_count)} />
        <Stat
          label="Largest context"
          value={comparison.summary.largest_context ?? "Not disclosed"}
        />
      </dl>
      <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="sticky left-0 bg-slate-50 px-4 py-3 font-semibold">Aspect</th>
              {comparison.models.map((model) => (
                <th key={model.slug} className="px-4 py-3 font-semibold">
                  {model.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {comparison.rows.map((row) => (
              <tr key={row.key} className="border-t border-slate-100 align-top">
                <th className="sticky left-0 bg-white px-4 py-3 font-medium text-slate-700">
                  <span>{row.label}</span>
                  <span className="mt-1 block text-xs font-normal text-slate-500">
                    {row.description}
                  </span>
                </th>
                {row.values.map((value, index) => (
                  <td
                    key={`${row.key}-${comparison.models[index]?.slug ?? index}`}
                    className={cn("px-4 py-3 text-slate-800", row.differs && "bg-amber-50/40")}
                  >
                    {value}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4">
      <dt className="text-xs font-semibold tracking-[0.16em] text-slate-500 uppercase">
        {label}
      </dt>
      <dd className="mt-2 text-lg font-semibold">{value}</dd>
    </div>
  );
}
