import { ModelCard } from "@/components/content/model-card";
import { listModels, type ModelSummary } from "@/services/api";

export const metadata = {
  title: "AI Models",
  description: "Structured profiles for more than fifty important AI models.",
};

export default async function ModelsPage() {
  let models: ModelSummary[] = [];
  try {
    models = await listModels();
  } catch {
    models = [];
  }

  return (
    <div className="mx-auto flex w-full max-w-[1280px] flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
      <header className="border-b border-rule pb-6">
        <p className="text-[0.7rem] font-semibold tracking-[0.32em] text-crimson uppercase">Catalog</p>
        <h1 className="font-display mt-2 text-4xl tracking-tight md:text-5xl">AI models</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-ink/70">
          {models.length} models covering language, reasoning, multimodal, image, video,
          audio, and embeddings. Figures are indicative public specifications and can change.
        </p>
      </header>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src="/covers/cover-chip.png" alt="" className="aspect-[21/8] w-full object-cover" />
      {models.length === 0 ? (
        <p className="border border-dashed border-rule bg-cream p-8 text-sm text-ink/70">
          The catalog appears after the API can reach PostgreSQL and complete startup seeding.
        </p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {models.map((model) => (
            <ModelCard key={model.slug} model={model} />
          ))}
        </div>
      )}
    </div>
  );
}
