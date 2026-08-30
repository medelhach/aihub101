import Link from "next/link";

import type { ModelSummary } from "@/services/api";

type ModelCardProps = {
  model: ModelSummary;
};

export function ModelCard({ model }: ModelCardProps) {
  return (
    <article className="flex h-full flex-col rounded-2xl border border-slate-200 bg-white p-5">
      <p className="text-xs font-semibold tracking-[0.18em] text-slate-500 uppercase">
        {model.provider}
      </p>
      <h2 className="mt-2 text-lg font-semibold tracking-tight">
        <Link href={`/models/${model.slug}`} className="hover:underline">
          {model.name}
        </Link>
      </h2>
      <p className="mt-2 text-sm text-slate-600">
        {model.modality}
        {model.context_window_tokens
          ? ` · ${model.context_window_tokens.toLocaleString()} context`
          : ""}
      </p>
      <ul className="mt-4 flex flex-wrap gap-2 text-xs">
        {model.open_weights ? (
          <li className="rounded-full bg-emerald-50 px-2 py-1 text-emerald-800">Open weights</li>
        ) : (
          <li className="rounded-full bg-slate-100 px-2 py-1 text-slate-700">API / hosted</li>
        )}
        {model.reasoning ? (
          <li className="rounded-full bg-indigo-50 px-2 py-1 text-indigo-800">Reasoning</li>
        ) : null}
        {model.multimodal ? (
          <li className="rounded-full bg-amber-50 px-2 py-1 text-amber-800">Multimodal</li>
        ) : null}
      </ul>
    </article>
  );
}
