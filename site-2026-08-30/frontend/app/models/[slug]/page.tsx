import Link from "next/link";
import { notFound } from "next/navigation";

import { getModel } from "@/services/api";

type ModelDetailPageProps = {
  params: Promise<{ slug: string }>;
};

export default async function ModelDetailPage({ params }: ModelDetailPageProps) {
  const { slug } = await params;
  let model;
  try {
    model = await getModel(slug);
  } catch {
    notFound();
  }

  const facts = [
    ["Provider", model.provider],
    ["Family", model.family],
    ["Released", model.release_date ?? "Not disclosed"],
    ["Modality", model.modality],
    ["Architecture", model.architecture],
    ["Parameters", model.parameters ?? "Not disclosed"],
    ["Context window", model.context_window_tokens?.toLocaleString() ?? "Not disclosed"],
    ["Max output", model.max_output_tokens?.toLocaleString() ?? "Not disclosed"],
    ["License", model.license_name],
    ["Open weights", model.open_weights ? "Yes" : "No"],
    ["Availability", model.availability],
    ["Reasoning SKU", model.reasoning ? "Yes" : "No"],
    ["Multimodal", model.multimodal ? "Yes" : "No"],
    ["Fine-tuning", model.fine_tune_available ? "Available" : "Not offered / unknown"],
    ["Knowledge cutoff", model.knowledge_cutoff ?? "Not disclosed"],
    [
      "Input price",
      model.input_price_per_million_usd != null
        ? `$${model.input_price_per_million_usd} / 1M tokens`
        : "Not a token-priced API, or undisclosed",
    ],
    [
      "Output price",
      model.output_price_per_million_usd != null
        ? `$${model.output_price_per_million_usd} / 1M tokens`
        : "Not a token-priced API, or undisclosed",
    ],
  ];

  return (
    <article className="flex w-full flex-col gap-10">
      <header className="max-w-3xl">
        <p className="text-xs font-semibold tracking-[0.2em] text-slate-500 uppercase">
          {model.provider}
        </p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight">{model.name}</h1>
        <p className="mt-4 text-base leading-7 text-slate-600">{model.architecture}</p>
        <p className="mt-4">
          <Link href={`/compare?models=${model.slug}`} className="text-sm font-medium underline">
            Compare this model
          </Link>
        </p>
      </header>
      <dl className="grid gap-4 sm:grid-cols-2">
        {facts.map(([label, value]) => (
          <div key={label} className="rounded-2xl border border-slate-200 bg-white p-4">
            <dt className="text-xs font-semibold tracking-[0.16em] text-slate-500 uppercase">
              {label}
            </dt>
            <dd className="mt-2 text-sm leading-6 text-slate-800">{value}</dd>
          </div>
        ))}
      </dl>
      <SpecList title="Typical use cases" items={model.typical_use_cases} />
      <SpecList title="Strengths" items={model.strengths} />
      <SpecList title="Limitations" items={model.limitations} />
      <section>
        <h2 className="text-xl font-semibold">Safety and governance</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-700">{model.safety_notes}</p>
      </section>
      <section>
        <h2 className="text-xl font-semibold">Published scores</h2>
        <p className="mt-2 text-sm text-slate-500">
          Scores are not always comparable across vendors or evaluation dates.
        </p>
        <ul className="mt-4 grid gap-2 sm:grid-cols-2">
          {Object.entries(model.benchmarks).length === 0 ? (
            <li className="text-sm text-slate-600">No public score recorded in the catalog.</li>
          ) : (
            Object.entries(model.benchmarks).map(([name, score]) => (
              <li key={name} className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm">
                <span className="font-medium">{name}</span>: {String(score)}
              </li>
            ))
          )}
        </ul>
      </section>
      <p className="text-sm text-slate-600">{model.pricing_notes}</p>
      <a className="text-sm font-medium underline" href={model.documentation_url} rel="noreferrer">
        Vendor documentation
      </a>
    </article>
  );
}

function SpecList({ title, items }: { title: string; items: string[] }) {
  return (
    <section>
      <h2 className="text-xl font-semibold">{title}</h2>
      <ul className="mt-3 list-disc space-y-1 pl-5 text-sm leading-7 text-slate-700">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
